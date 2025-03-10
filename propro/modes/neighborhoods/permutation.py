from __future__ import annotations
import logging
from dataclasses import dataclass
import random
# from multiprocessing import Pool, cpu_count
# from copy import deepcopy
# import os

from problem.box_problem.geometry import Box, Rectangle
from problem.box_problem.box_heuristic import PermutationHeuristic
from problem.box_problem.box_solution import BoxSolution
from utils import flatten
from .neighborhood import Neighborhood
from ..move import ScoredMove, Move

logger = logging.getLogger(__name__)

#TODO: Currently the permutation neighborhood sometimes does not find an optimal solution.
# 1)this could be fixed by taking all the boxes with only one rectangle in it and place it at the front.
# 1 does not work as it screas up already made moves.
# 2) this could be fixed by not swapping rectangles if we do a fillup, but put the inserting rectangle at this position.
#    By this the recond part will be moved to the end of the list.
#    BUT: it might violate the permutation rule, as this is almost like a swap.

#TODO: implement generate_heuristic for this neighborhood

class Permutation(Neighborhood):
  '''Implementation for a permutation-based neighborhood'''

  # n_proc = max(int(os.environ.get("OPTALGO_MAX_CPU", 0)), cpu_count())

  @classmethod
  def initialize(cls, solution: BoxSolution) -> BoxSolution:
    '''Initializes the neighborhood by returning the initial solution'''
    encoded_sol = cls.encode_solution(solution)
    encoded_sol.sort(key=lambda x: x.get_width() * x.get_height(), reverse=True)
    decoded_sol = cls.decode_rect_list(encoded_sol, solution.side_length)
    solution.boxes = { box.id: box for box in decoded_sol }
    return solution

  @classmethod
  def encode_solution(cls, solution: BoxSolution) -> list[Rectangle]:
    '''
    Turns the solution into a list of boxes
    '''
    # TODO: remove this function from the permutationMove class.
    return flatten([b.rects.values() for b in solution.boxes.values()])

  @classmethod
  def decode_rect_list(cls, rects: list[Rectangle], box_length: int) -> list[Box]:
    '''
    Turns a list of rectangles into a valid solution to the box-rect problem.
    '''

    # Take rects one by one and put them into a new box..
    # # Once one boundary is crossed, start with a new box
    boxes = [Box(0, box_length)]
    current_box = boxes[0]
    # Go through rects until all have been processed
    for rect in rects:
      # for the rect check if it fits somewhere in the current box
      succ = current_box.fit_rect_compress(rect)
      if not succ:
        # If it does not fit, create a new box and put it there
        current_box = Box(len(boxes), box_length)
        current_box.fit_rect_compress(rect)
        boxes.append(current_box)
    return boxes

  @classmethod
  def evaluate_moves(cls, solution: BoxSolution, moves: list[PermutationMove]) -> list[ScoredMove]:
    scored_moves = []
    for move in moves:
      heuristic_score = cls.generate_heuristic(solution, move)
      if move.is_fill:
        heuristic_score = cls.generate_heuristic(solution, move)
      scored_moves.append(ScoredMove(move, heuristic_score))
    return scored_moves

  @classmethod
  def generate_neighbor_moves(cls, solution: BoxSolution) -> list[PermutationMove]:
    '''Generates a list of permutation moves to go from this solution to a neighboring one
        A Permutation is a swap of two rectangles or a flip of one rectangle.'''
    moves: list[PermutationMove] = []
    encoded_rects = cls.encode_solution(solution)

    # it first tries to fill remaining space of the boxes with rectangles located in succeeding boxes.
    # It then tries to get good swaps of rectangles to improve the solution.

    # First, fill the remaining space of the boxes with rectangles located in succeeding boxes.
    for box_id, box in solution.boxes.items():
      #get dimensions of the biggest rectangle that fits in the box
      biggest_rect = box.get_biggest_placeable_rect()
      if biggest_rect == (0,0) or biggest_rect is None:
        continue
      for i, rect_to_swap in enumerate(encoded_rects):
        if rect_to_swap.box_id <= box_id:
          continue
        if rect_to_swap.get_width() <= biggest_rect[0] and rect_to_swap.get_height() <= biggest_rect[1]:
          #get any rectangle of the box.
          dummy_target_box_rect = list(box.rects.values())[0]
          dummy_target_box_rect_idx = encoded_rects.index(dummy_target_box_rect)
          moves.append(PermutationMove(dummy_target_box_rect_idx , i, dummy_target_box_rect, rect_to_swap, False, True))
          break
      if moves:
        break
    if moves:
      return moves

    # Second, try to get good swaps of rectangles to improve the solution.
    # for each rectangle check the space below and to the right.
    # If there is space, search for a rectangle that fits most optimally there and swap them.
    for i, rect_a in enumerate(encoded_rects):
      #get the free area around A.
      box_a = solution.boxes[rect_a.box_id]
      available_space_x : int = rect_a.get_width()
      available_space_y : int = rect_a.get_height()
      free_coords = box_a.get_free_coordinates()
      # check in x direction
      is_free = True
      for x in range(rect_a.get_x() + rect_a.get_width(), solution.side_length):
        for y in range(rect_a.get_y(), rect_a.get_y() + rect_a.get_height()):
          if (x, y) not in free_coords:
            is_free = False
            break
        if not is_free:
          break
        available_space_x += 1
      #check in y direction
      is_free = True
      for y in range(rect_a.get_y() + rect_a.get_height(), solution.side_length):
        for x in range(rect_a.get_x(), rect_a.get_x() + rect_a.get_width()):
          if (x, y) not in free_coords:
            is_free = False
            break
        if not is_free:
          break
        available_space_y += 1


      #iterate for B over the rest of encoded_rects, starting at i+1
      for j, rect_b in enumerate(encoded_rects[i+1:], start=i+1):
        # check if the rectangle fits in the free area around rect_a
        # get the next best rectangle that fits in the free area and is larger than rect_a

        # not flipped
        if rect_b.get_width() <= rect_a.get_width() and rect_b.get_height() <= rect_a.get_height():
          continue
        if rect_b.get_width() < rect_a.get_width() or rect_b.get_height() < rect_a.get_height():
          continue
        if rect_b.get_width() <= available_space_x and rect_b.get_height() <= available_space_y:
          moves.append(PermutationMove(i, j, rect_a, rect_b, False))
          continue

        # flipped
        if rect_b.get_height() <= rect_a.get_width() and rect_b.get_width() <= rect_a.get_height():
          continue
        if rect_b.get_height() < rect_a.get_width() or rect_b.get_width() < rect_a.get_height():
          continue
        if rect_b.get_height() <= available_space_x and rect_b.get_width() <= available_space_y:
          moves.append(PermutationMove(i, j, rect_a, rect_b, True))
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

    # # If we have more than 4 moves per chunk, go multithreaded
    # if (len(moves) >= cls.n_proc * 4):
    #   # Copy the current solution so every thread can modify it independently
    #   # Expensive, but worth it (hopefully)
    #   solution_copies = [deepcopy(solution) for _ in range(cls.n_proc)]

    #   # Split moves into chunks for pool to process
    #   chunks = np.array_split(moves, cls.n_proc)

    #   # Evaluate all moves to scored moves concurrently
    #   with Pool(processes=cls.n_proc) as pool:
    #     scored_moves = flatten(pool.starmap(cls.evaluate_moves, zip(solution_copies, chunks)))

    # # Else just do it in this thread
    # else:
    scored_moves = cls.evaluate_moves(solution, moves)

    logger.info("Explored %i neighbors", len(scored_moves))
    return scored_moves

  @classmethod
  def generate_heuristic(cls, solution: BoxSolution, move: Move = None):
    if move is None:
      return PermutationHeuristic(solution)

    rect_a = move.first_rect
    rect_b = move.second_rect
    heuristic = PermutationHeuristic(rect_a, rect_b)
    if move.is_fill:
      heuristic = PermutationHeuristic(rect_a, rect_b, True, solution.side_length)
    return heuristic

@dataclass
class PermutationMove(Move):
  '''Describes a move as two indices of rects to be swapped in the encoded rect list (with optional flip).
  If it is a fillup, the second rect is inserted to the box of the first rect.'''

  first_idx: int
  second_idx: int
  first_rect: Rectangle
  second_rect: Rectangle
  flip: bool
  is_fill: bool = False



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

    # Take rects one by one and put them into a new box..
    # # Once one boundary is crossed, start with a new box
    boxes = [Box(0, box_length)]
    current_box = boxes[0]
    # Go through rects until all have been processed
    for rect in rects:
      # for the rect check if it fits somewhere in the current box
      succ = current_box.fit_rect_compress(rect)
      if not succ:
        # If it does not fit, create a new box and put it there
        current_box = Box(len(boxes), box_length)
        current_box.fit_rect_compress(rect)
        boxes.append(current_box)
    return boxes


  @classmethod
  def apply_fillup_move(
    cls,
    target_box: int,
    rect_to_swap: Rectangle,
    boxes: dict[int, Box]
  ) -> bool:
    '''
    Applies a fillup move to the solution.
    It moves the second rectangle to the box of the first rectangle.
    returns False if the move is not possible.
    '''
    # Get the boxes that contain the rectangle
    box_b = boxes[rect_to_swap.box_id]

    # Remove the rectangle from box_b
    box_b.remove_rect(rect_to_swap.id)
    # might need to remove the box if it is empty
    if not box_b.rects:
      boxes.pop(box_b.id)
      for i, box in boxes.items():
        box.set_box_id(i)

    # Try to fit the rectangle into box_a
    succ = boxes[target_box].fit_rect_compress(rect_to_swap)
    rect_to_swap.highlighted = True
    return succ

  def apply_to_solution(self, solution: BoxSolution) -> bool:
    '''Applies this move to a given box solution'''
    if (self.first_idx == self.second_idx) and not self.flip:
      return False

    #if it is a fillup move, apply it and return
    if self.is_fill:
      succ = self.apply_fillup_move(self.first_rect.box_id, self.second_rect, solution.boxes)
      if not succ:
        return False
      if random.randint(1, 20) == 1:
        solution.boxes = {
          box.id: box
          for box in self.decode_rect_list(self.encode_solution(solution), solution.side_length)
          }
      return True

    encoded_rects = self.encode_solution(solution)

    rect_a = encoded_rects[self.first_idx]
    rect_b = encoded_rects[self.second_idx]
    assert rect_a.box_id is not None and rect_b.box_id is not None, "Rectangles must have a box id"

    # Swap
    if self.first_idx != self.second_idx:
      (
        encoded_rects[self.first_idx], encoded_rects[self.second_idx]
      ) = (
        encoded_rects[self.second_idx], encoded_rects[self.first_idx]
      )
      encoded_rects[self.first_idx].highlighted ^= True
      encoded_rects[self.second_idx].highlighted ^= True

    # Flip
    if self.flip:
      this_rect = encoded_rects[self.first_idx]
      this_rect.flip()
      #this_rect.get_width(), this_rect.get_height() = this_rect.get_height(), this_rect.get_width()
      # Highlight it as changed
      this_rect.highlighted ^= True

    # Decode and modify in-place
    solution.boxes = { box.id: box for box in self.decode_rect_list(encoded_rects, solution.side_length) }
    return True

  def undo(self, solution: BoxSolution):
    # Luckily this operation is symmetric :)
    self.apply_to_solution(solution)
