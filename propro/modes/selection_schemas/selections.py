'''
Contains different selection schemas for the greedy algorithm.
'''

from itertools import product
from abc import abstractmethod

from problem import BoxSolution, Rectangle, Box
from ..mode import Mode

class SelectionSchema(Mode):
  '''Base class for all different selection schemas'''

  @classmethod
  @abstractmethod
  def select(cls, partial_solution: BoxSolution, unprocessed_rects: list[Rectangle]) -> int:
    '''Looks at the current solution and returns one rectangle via id from the input list to be placed next'''

  @classmethod
  def __fits_rect(cls, box: Box, box_length: int, rect: Rectangle) -> tuple[int, int] | None:
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

  @classmethod
  def insert_object(cls, partial_solution: BoxSolution, rect: Rectangle) -> BoxSolution:
    '''
    Inserts a given rectangle into the partial solution.
    If no fit was found, a new box is created to accomodate it.
    '''
    for box in partial_solution.boxes.values():
      possible_fit = cls.__fits_rect(box, partial_solution.side_length, rect)
      if possible_fit is not None:
        rect.x, rect.y = possible_fit
        box.add_rect(rect)
        break
    else:
      # If no box had room, create a new one
      rect.x, rect.y = (0, 0)
      new_box = Box(len(partial_solution.boxes), partial_solution.side_length, rect)
      partial_solution.boxes[new_box.id] = new_box
    return partial_solution
