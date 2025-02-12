from problem import BoxSolution
from geometry import Rectangle

from .selections import SelectionSchema

class ByAreaSelection(SelectionSchema):
  '''
  Simple concept: At every step, take the rectangle which has the minimal area.
  This will use up the big ones first and the smaller ones can fit into the gaps
   which are created in the process.
  '''
  # TODO: Could sort the list once and save it somewhere, might be faster
  @classmethod
  def select(cls, _: BoxSolution, unprocessed_rects: list[Rectangle]) -> int:
    '''Will always return the rectangle with the largest area from the input queue.'''
    return max(unprocessed_rects, key=lambda r: r.get_area()).id
