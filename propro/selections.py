'''
Contains different selection schemas for the greedy algorithm.
'''

from enum import Enum, auto
from itertools import product

from problem import BoxSolution, Rectangle, Box

class SelectionSchema(Enum):
  '''Enumeration type for all different selection schemas'''
  FIRST_FIT = auto()
  # TODO: assignment calls for a second schema

  def get_selection_schema(self):
    '''Returns the according selection method for this type'''
    match self:
      case SelectionSchema.FIRST_FIT: return select_first_fit

def select_first_fit(partial_solution: BoxSolution, rect: Rectangle) -> BoxSolution:
  '''
  Returns the first possible fit for a given rectangle in the boxes.
  If every rectangle gets its first fit, the number of boxes should be minimal.
  '''
  for box in partial_solution.boxes.values():
    possible_fit = __fits_rect(box, partial_solution.side_length, rect)
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

def __fits_rect(box: Box, box_length: int, rect: Rectangle) -> tuple[int, int] | None:
  '''Checks if a given rect fits somewhere in a box and returns the origin coordinates if possible'''
  # TODO: do something smarter :)
  # Loop over all origins
  for origin in product(range(box_length), range(box_length)):
    # Set x/y of rect to these coordinates
    rect.x, rect.y = origin
    # See if rect's coordinates are in the set of box free coordinates
    if rect.get_all_coordinates() <= box.get_free_coordinates():
      return origin
  # If loop never returned then nothing fits -> Return None
  return None
