'''
Contains a basic neighborhood definition that must be inherited from
'''
from abc import ABC, abstractmethod

from problem import BoxSolution, Rectangle, Box, ScoredMove
from utils import flatten

class Neighborhood(ABC):
  '''Abstract neighborhood base class'''

  neighbors = []

  MAX_NEIGHBORS = 100

  @classmethod
  @abstractmethod
  def get_neighbors(cls, solution: BoxSolution) -> list[ScoredMove]:
    '''
    Calculates neighbors of a given start solution.
    '''

  @classmethod
  def _encode_solution(cls, solution: BoxSolution) -> list[Rectangle]:
    '''
    Turns the solution into a list of boxes
    '''
    return flatten([b.rects.values() for b in solution.boxes.values()])

  @classmethod
  def _decode_rect_list(cls, rects: list[Rectangle], box_length: int) -> BoxSolution:
    '''
    Turns a list of rectangles into a valid solution to the box-rect problem.
    '''
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
      if next_x + rect.width < box_length and next_y + rect.height < box_length:
        # Update this rect's coordinates
        rect.x = next_x
        rect.y = current_y
        current_box.add_rect(rect)
        # Also update the next corodinate
        next_x += rect.width
        next_y = max(next_y, current_y + rect.height)
        continue
      #  Case 2: Rects overflows to the right, but fits into a next row within this box
      if next_x + rect.width >= box_length and next_y + rect.height < box_length:
        # NOTE: By specification this must fit here, box_length is guaranteed to be larger than any rect side
        rect.x = 0
        rect.y = next_y
        current_box.add_rect(rect)
        # Update coordinates for the next box
        next_x = rect.width
        current_y = next_y
        next_y = current_y + rect.height
        continue
      # Case 3: Rect does not fit into this box, create a new one and push it to boxes
      current_box = Box(len(boxes), box_length)
      rect.x = 0
      rect.y = 0
      current_box.add_rect(rect)
      boxes.append(current_box)
      # And set the next coordinates again
      next_x = rect.width
      current_y = 0
      next_y = rect.height

    # Construct box solution from list of boxes
    return BoxSolution(box_length, boxes)
