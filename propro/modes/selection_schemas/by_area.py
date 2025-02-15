from itertools import product
from typing import Optional

from problem import BoxSolution
from geometry import Rectangle, Box

from .selections import SelectionSchema, SelectionMove

class ByAreaSelection(SelectionSchema):
  '''
  Simple concept: At every step, take the rectangle which has the minimal area.
  This will use up the big ones first and the smaller ones can fit into the gaps
   which are created in the process.
  '''

  @staticmethod
  def __fits_rect(box: Box, box_length: int, rect: Rectangle) -> Optional[tuple[int, int]]:
    '''Checks if a given rect fits somewhere in a box and returns the origin coordinates if possible'''
    # Loop over all origins
    for origin in product(range(box_length), range(box_length)):
      # Set x/y of rect to these coordinates
      rect.x, rect.y = origin
      # See if rect's coordinates are in the set of box free coordinates
      if rect.get_all_coordinates() <= box.get_free_coordinates():
        return origin
    # If loop never returned then nothing fits -> Return None
    return None

  @staticmethod
  def find_placement(partial_solution: BoxSolution, rect: Rectangle) -> SelectionMove:
    '''
    Finds a place for a given rectangle into the partial solution.
    If no fit was found, a new box is created to accomodate it.
    '''
    for box in partial_solution.boxes.values():
      possible_fit = ByAreaSelection.__fits_rect(box, partial_solution.side_length, rect)
      if possible_fit is not None:
        rect.x, rect.y = possible_fit
        return SelectionMove(rect, box.id)
    # If no box had room, create a new one
    new_box = Box(len(partial_solution.boxes), partial_solution.side_length)
    partial_solution.boxes[new_box.id] = new_box
    (rect.x, rect.y) = (0, 0)
    return SelectionMove(rect, new_box.id)

  @classmethod
  def select(cls, partial_solution: BoxSolution, unprocessed_rects: list[Rectangle]) -> SelectionMove:
    '''
     Will always return the rectangle with the largest area from the input queue
     and place it at the smallest possible coordinate.
    '''
    # Find which rect to go for
    rect = max(unprocessed_rects, key=lambda r: r.get_area())
    # Find a placement
    return cls.find_placement(partial_solution, rect)
