from __future__ import annotations
import logging
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
from copy import deepcopy
import os

import numpy as np

from problem.box_problem.geometry import Box, Rectangle
from problem.box_problem.box_heuristic import PermutationHeuristic
from utils import flatten
from problem.box_problem.box_solution import BoxSolution
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

  n_proc = max(int(os.environ.get("OPTALGO_MAX_CPU", 0)), cpu_count())

  # TODO: call this when running with permutation algorithm
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
      rect_A = move.first_rect
      rect_B = move.second_rect
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
    for i, rect_A in enumerate(encoded_rects):
      box_A = solution.boxes[rect_A.box_id]
      for j, rect_B in enumerate(encoded_rects[i+1:], start=i+1):
        if rect_B.box_id == rect_A.box_id:
          continue
        if rect_B.box_id < rect_A.box_id:
          continue
        succ = box_A.fit_rect_compress(rect_B, False)
        flipped = not succ
        if not succ:
          #rect_B.get_height(), rect_B.get_width() = rect_B.get_width(), rect_B.get_height()
          rect_B.flip()
          succ = box_A.fit_rect_compress(rect_B, False)
          if not succ:
            #rect_B.get_height(), rect_B.get_width() = rect_B.get_width(), rect_B.get_height()
            rect_B.flip()
        if succ:
          # swap rect_B with the first rectangle in the box that is not rect_A
          for k, rect_C in enumerate(encoded_rects[i+1:], start=i+1):
            assert rect_C.box_id is not None, "Rectangles must have a box id"
            #assert rect_C.box_id >= rect_A.box_id, "Box IDs must be in ascending order"
            if rect_C.id == rect_A.id:
              continue
            if rect_C.id == rect_B.id:
              continue
            if rect_C.box_id == (rect_A.box_id + 1):
              # swap rect_B with rect_C
              moves.append(PermutationMove(k,j, rect_C, rect_B, flipped, True))
              break
          break
      if moves != []:
        break
    if moves != []:
      return moves

    # Second, try to get good swaps of rectangles to improve the solution.
    # for each rectangle check the space below and to the right. 
    # If there is space, search for a rectangle that fits most optimally there and swap them.
    for i, rect_A in enumerate(encoded_rects):
      #get the free area around A.
      box_A = solution.boxes[rect_A.box_id]
      available_space_x : int = rect_A.get_width()
      available_space_y : int = rect_A.get_height()
      free_coords = box_A.get_free_coordinates()
      # check in x direction
      is_free = True
      for x in range(rect_A.get_x() + rect_A.get_width(), solution.side_length):
        for y in range(rect_A.get_y(), rect_A.get_y() + rect_A.get_height()):
          if (x, y) not in free_coords:
            is_free = False
            break
        if not is_free:
          break
        available_space_x += 1
      #check in y direction
      is_free = True
      for y in range(rect_A.get_y() + rect_A.get_height(), solution.side_length):
        for x in range(rect_A.get_x(), rect_A.get_x() + rect_A.get_width()):
          if (x, y) not in free_coords:
            is_free = False
            break
        if not is_free:
          break
        available_space_y += 1
        

      #iterate for B over the rest of encoded_rects, starting at i+1
      for j, rect_B in enumerate(encoded_rects[i+1:], start=i+1):
        # check if the rectangle fits in the free area around rect_A
        # get the next best rectangle that fits in the free area and is larger than rect_A

        # not flipped
        if rect_B.get_width() <= rect_A.get_width() and rect_B.get_height() <= rect_A.get_height():
          continue
        if rect_B.get_width() < rect_A.get_width() or rect_B.get_height() < rect_A.get_height():
          continue
        if rect_B.get_width() <= available_space_x and rect_B.get_height() <= available_space_y:
          moves.append(PermutationMove(i, j, rect_A, rect_B, False))
          continue

        # flipped
        if rect_B.get_height() <= rect_A.get_width() and rect_B.get_width() <= rect_A.get_height():
          continue
        if rect_B.get_height() < rect_A.get_width() or rect_B.get_width() < rect_A.get_height():
          continue
        if rect_B.get_height() <= available_space_x and rect_B.get_width() <= available_space_y:
          moves.append(PermutationMove(i, j, rect_A, rect_B, True))
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
    if (len(moves) >= cls.n_proc * 4) and False:
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
  
  @classmethod
  def generate_heuristic(cls, solution: BoxSolution, move: Move = None):
    if move is None:
      return PermutationHeuristic(solution)
  
    rect_A = move.first_rect
    rect_B = move.second_rect
    heuristic = PermutationHeuristic(rect_A, rect_B)
    if move.is_fill:
      heuristic = PermutationHeuristic(rect_A, rect_B, True, solution.side_length)
    return heuristic

@dataclass
class PermutationMove(Move):
  '''Describes a move as two indices of rects to be swapped in the encoded rect list (with optional flip)'''
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
    current_y = 0 # Current row's y index
    next_x = 0 # Next x coordinate for a box
    next_y = 0 # Next y index for a row
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
  def partial_decode(cls, rect_A: Rectangle, rect_B: Rectangle, rects: list[Rectangle], box_length: int, boxes: dict[int, Box]) -> dict[int, Box]:
    '''
    Decodes a list of rectangles into a valid solution to the box-rect problem.
    It only modifies the boxes that contain the rectangles that were swapped and eventally propagated changes.
    '''
    # Get the boxes that contain the rectangles
    boxA = boxes[rect_A.box_id]
    boxB = boxes[rect_B.box_id]

    # sort them by box id
    if boxA.id > boxB.id:
      boxA, boxB = boxB, boxA

    currBox = boxes[0]
    fine : bool = True
    needs_new_box : bool = False
    for i, rect in enumerate(rects):
      assert rect.box_id is not None, "Rectangles must have a box id"

      # check if we have finished a box with a permutation that did not need additional boxes
      if currBox.id != rect.box_id and not fine and not needs_new_box:
        fine = True

      if fine: 
        # skip until we find the first box
        if (currBox.id + 1 == rect.box_id):
          currBox = boxes[rect.box_id]
        if (currBox.id != boxA.id and currBox.id != boxB.id):
          continue
        assert currBox.id == boxA.id or currBox.id == boxB.id, "Rectangle must be in one of the two boxes"
        # we have encountered a box where a move happens. 
        # reset this box to get newly filled.
        currBox = Box(currBox.id, box_length)
        boxes[currBox.id] = currBox
        fine = False

      # try to place the rectangle in this box.
      # if it does not fit in the box, create a new box and place it there. Overwriting the next box.
      succ = currBox.fit_rect_compress(rect)
      if not succ:
        needs_new_box = True
        currBox = Box(currBox.id+1, box_length)
        currBox.fit_rect_compress(rect)
        assert rect.get_x() == 0 and rect.get_y() == 0, f"Rectangle must be placed in the upper left corner as the box is empty. currlocation is: {rect.get_x()} {rect.get_y()}"
        boxes[currBox.id] = currBox
    #might need to remove boxes if the currBox is not the last box
    if currBox.id < len(boxes):
      for i in range(currBox.id+1, len(boxes)):
        boxes.pop(i)
    return boxes
      




  def apply_to_solution(self, solution: BoxSolution) -> bool:
    '''Applies this move to a given box solution'''
    if (self.first_idx == self.second_idx) and not self.flip:
      return False

    encoded_rects = self.encode_solution(solution)

    rect_A = encoded_rects[self.first_idx]
    rect_B = encoded_rects[self.second_idx]
    assert rect_A.box_id is not None and rect_B.box_id is not None, "Rectangles must have a box id"
    boxA_id = rect_A.box_id
    boxB_id = rect_B.box_id

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

    #solution.boxes = self.partial_decode(rect_A, rect_B, encoded_rects, solution.side_length, solution.boxes)

    # Decode and modify in-place
    solution.boxes = { box.id: box for box in self.decode_rect_list(encoded_rects, solution.side_length) }
    return True

  def undo(self, solution: BoxSolution):
    # Luckily this operation is symmetric :)
    self.apply_to_solution(solution)
