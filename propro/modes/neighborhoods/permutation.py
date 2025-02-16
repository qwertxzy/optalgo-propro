import logging
from dataclasses import dataclass

from geometry import Box, Rectangle
from utils import flatten
from problem import BoxSolution
from .neighborhood import Neighborhood
from ..move import ScoredMove, Move

logger = logging.getLogger(__name__)

class Permutation(Neighborhood):
  '''Implementation for a permutation-based neighborhood'''

  @classmethod
  def get_neighbors(cls, solution: BoxSolution) -> list[ScoredMove]:
    '''
    Encodes the solution into a long list of rects that get placed from top left-to bottom-right
    in each box. Then computes permutations of this list and turns them back to solutions.
    '''
    logger.info("Claculating Permutation neighborhood")

    neighbors = []

    # Do every possible pairwise swap
    num_rects = sum(map(lambda b: len(b.rects), solution.boxes.values()))
    for i in range(num_rects - 1):
      move = PermutationMove(i, i + 1, False)
      score = solution.get_potential_score(move)
      neighbors.append(ScoredMove(move, score))

    # Also flip every possible rect
    for i in range(num_rects):
      move = PermutationMove(i, i, True)
      score = solution.get_potential_score(move)
      neighbors.append(ScoredMove(move, score))

    return neighbors

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

    # Below was a cool idea for better placement, but makes it about 20x slower..
    # for rect in rects:
    #   rect_placed = False
    #   # Try to fit it in every box
    #   for box in boxes:
    #     # If it was placed already break box iteration, we've found its home
    #     if rect_placed:
    #       break

    #     # Iterate over every possible origin
    #     for origin in product(range(box_length - rect.width), range(box_length - rect.height)):
    #       rect.move_to(*origin)

    #       # Place if it fits
    #       if rect.get_all_coordinates() <= box.get_free_coordinates():
    #         box.add_rect(rect)
    #         rect_placed = True
    #         break

    #   # If none fit, create a new one and put it at 0/0
    #   if not rect_placed:
    #     rect.move_to(0, 0)
    #     new_box = Box(len(boxes), box_length, rect)
    #     boxes.append(new_box)

    # Take rects one by one and put them into a new box..
    # Once one boundary is crossed, start with a new box
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
