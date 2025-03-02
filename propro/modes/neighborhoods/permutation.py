from __future__ import annotations
import logging
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
from copy import deepcopy
import os

import numpy as np

from geometry import Box, Rectangle
from utils import flatten
from problem import BoxSolution
from .neighborhood import Neighborhood
from ..move import ScoredMove, Move

logger = logging.getLogger(__name__)

class Permutation(Neighborhood):
  '''Implementation for a permutation-based neighborhood'''

  n_proc = max(int(os.environ.get("OPTALGO_MAX_CPU", 0)), cpu_count())

  @classmethod
  def generate_neighbor_moves(cls, solution: BoxSolution) -> list[PermutationMove]:
    '''Generates a list of permutation moves to go from this solution to a neighboring one'''
    moves = []

    # Do every possible pairwise swap
    num_rects = sum(map(lambda b: len(b.rects), solution.boxes.values()))
    for i in range(num_rects - 1):
      move = PermutationMove(i, i + 1, False)
      moves.append(move)

    # Also flip every possible rect
    for i in range(num_rects):
      move = PermutationMove(i, i, True)
      moves.append(move)

    return moves

  @classmethod
  def get_neighbors(cls, solution: BoxSolution) -> list[ScoredMove]:
    '''
    Encodes the solution into a long list of rects that get placed from top left-to bottom-right
    in each box. Then computes permutations of this list and turns them back to solutions.
    '''
    logger.info("Claculating Permutation neighborhood")

    moves = cls.generate_neighbor_moves(solution)

    logger.info("Generated %i moves", len(moves))

    # If we have more than 4 moves per chunk, go multithreaded
    if len(moves) >= cls.n_proc * 4:
      # Copy the current solution so every thread can modify it independently
      # Expensive, but worth it (hopefully)
      solution_copies = [deepcopy(solution) for _ in range(cls.n_proc)]

      # Split moves into chunks for pool to process
      chunks = np.array_split(moves, cls.n_proc)

      # Evaluate all moves to scored moves concurrently
      with Pool(processes=cls.n_proc) as pool:
        scored_moves = flatten(pool.starmap(cls.evaluate_moves, zip(solution_copies, chunks)))

    # Else just do it in this thread
    else:
      scored_moves = cls.evaluate_moves(solution, moves)

    logger.info("Explored %i neighbors", len(scored_moves))
    return scored_moves

@dataclass
class PermutationMove(Move):
  '''Describes a move as two indices of rects to be swapped in the encoded rect list (with optional flip)'''
  first_idx: int
  second_idx: int
  flip: bool

  @classmethod
  def encode_solution(cls, solution: BoxSolution) -> list[Rectangle]:
    '''
    Turns the solution into a list of boxes
    '''
    return flatten([b.rects.values() for b in solution.boxes.values()])

  @classmethod
  def decode_rect_list(cls, rects: list[Rectangle], box_length: int) -> list[Box]:
    '''
    Turns a list of rectangles into a valid solution to the box-rect problem.
    '''
    boxes = [Box(0, box_length)]

    # TODO: add upwards packing for every rect placed

    # Take rects one by one and put them into a new box..
    # # Once one boundary is crossed, start with a new box
    boxes = [Box(0, box_length)]
    current_box = boxes[0]
    current_y = 0 # Current row's y index
    next_x = 0 # Next x coordinate for a box
    next_y = 0 # Next y index for a row
    # Go through rects until all have been processed
    for rect in rects:
      # Case 1: Rect fits into this row
      if next_x + rect.width <= box_length and next_y + rect.height <= box_length:
        # Update this rect's coordinates
        rect.move_to(next_x, current_y)
        current_box.add_rect(rect)
        # Also update the next corodinate
        next_x += rect.width
        next_y = max(next_y, current_y + rect.height)
        continue
      #  Case 2: Rects overflows to the right, but fits into a next row within this box
      if next_x + rect.width > box_length and next_y + rect.height <= box_length:
        # NOTE: By specification this must fit here, box_length is guaranteed to be larger than any rect side
        rect.move_to(0, next_y)
        current_box.add_rect(rect)
        # Update coordinates for the next box
        next_x = rect.width
        current_y = next_y
        next_y = current_y + rect.height
        continue
      # Case 3: Rect does not fit into this box, create a new one and push it to boxes
      current_box = Box(len(boxes), box_length)
      rect.move_to(0, 0)
      current_box.add_rect(rect)
      boxes.append(current_box)
      # And set the next coordinates again
      next_x = rect.width
      current_y = 0
      next_y = rect.height
    return boxes

  def apply_to_solution(self, solution: BoxSolution) -> bool:
    '''Applies this move to a given box solution'''
    encoded_rects = self.encode_solution(solution)

    # Swap
    if self.first_idx != self.second_idx:
      (
        encoded_rects[self.first_idx], encoded_rects[self.second_idx]
      ) = (
        encoded_rects[self.second_idx], encoded_rects[self.first_idx]
      )
      encoded_rects[self.first_idx].highlighted = True
      encoded_rects[self.second_idx].highlighted = True

    # Flip
    if self.flip:
      this_rect = encoded_rects[self.first_idx]
      this_rect.width, this_rect.height = this_rect.height, this_rect.width
      # Highlight it as changed
      this_rect.highlighted = True

    # Decode and modify in-place
    solution.boxes = { box.id: box for box in self.decode_rect_list(encoded_rects, solution.side_length) }
    return True

  def undo(self, solution: BoxSolution):
    # Luckily this operation is symmetric :)
    self.apply_to_solution(solution)
