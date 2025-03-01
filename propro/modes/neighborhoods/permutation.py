from __future__ import annotations
import logging
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
from copy import deepcopy

import numpy as np

from geometry import Box, Rectangle
from utils import flatten
from problem import BoxSolution
from .neighborhood import Neighborhood
from ..move import ScoredMove, Move

logger = logging.getLogger(__name__)

class Permutation(Neighborhood):
  '''Implementation for a permutation-based neighborhood'''

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

    # Now evaluate all these moves in parallel
    n_proc = max(6, cpu_count()) # How many do we want?

    # If we have more than 4 moves per chunk, go multithreaded
    if len(moves) >= n_proc * 4:
      # Copy the current solution so every thread can modify it independently
      # Expensive, but worth it (hopefully)
      solution_copies = [deepcopy(solution) for _ in range(n_proc)]

      # Split moves into chunks for pool to process
      chunks = np.array_split(moves, n_proc)

      # Evaluate all moves to scored moves concurrently
      with Pool(processes=n_proc) as pool:
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

    for rect in rects:
      rect_placed = False
      # Try to fit it in every box
      for box in boxes:
        # If it was placed already break box iteration, we've found its home
        if rect_placed:
          break

        # Iterate over every possible origin
        for origin in box.get_adjacent_coordinates():
          rect.move_to(*origin)

          # Place if it fits
          if rect.get_all_coordinates() <= box.get_free_coordinates():
            box.add_rect(rect)
            rect_placed = True
            break

      # If none fit, create a new one and put it at 0/0
      if not rect_placed:
        rect.move_to(0, 0)
        new_box = Box(len(boxes), box_length, rect)
        boxes.append(new_box)
    # return list of constructed boxes
    return boxes

  def apply_to_solution(self, solution: BoxSolution):
    '''Applies this move to a given box solution'''
    encoded_rects = self.encode_solution(solution)
    # Swap
    if self.first_idx != self.second_idx:
      encoded_rects[self.first_idx], encoded_rects[self.second_idx] = encoded_rects[self.second_idx], encoded_rects[self.first_idx]

    # Flip
    if self.flip:
      this_rect = encoded_rects[self.first_idx]
      this_rect.width, this_rect.height = this_rect.height, this_rect.width

    # Decode and modify in-place
    solution.boxes = { box.id: box for box in self.decode_rect_list(encoded_rects, solution.side_length) }

  def undo(self, solution: BoxSolution):
    # Luckily this operation is symmetric :)
    self.apply_to_solution(solution)
