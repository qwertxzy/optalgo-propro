from problem import BoxSolution
from geometry import Rectangle

from .selections import SelectionSchema

class ByLengthSelection(SelectionSchema):
  '''
  ( current idea )
  Selection schema will:
   - look for the minimal coordinate where a rect could be placed next
   - try to return a rect that fills this box
   - if none does, try with the next smallest coordinate
   - if all fail, return the largest box
  '''

  @classmethod
  def select(cls, partial_solution: BoxSolution, unprocessed_rects: list[Rectangle]) -> int:
    '''Will always return the rectangle with the largest area from the input queue.'''
    raise NotImplementedError("Implement by-length selection please!!")
