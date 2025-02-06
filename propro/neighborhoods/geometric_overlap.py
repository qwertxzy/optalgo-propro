from problem import BoxSolution
from .neighborhood import Neighborhood

class GeometricOverlap(Neighborhood):
  '''Implements a geometric neighborhood definition that allows for adjustable overlap between rects.'''
  @classmethod
  def get_neighbors(cls, solution: BoxSolution) -> list:
    print("Claculating Geometric Overlap neighborhood")
    raise NotImplementedError("GeometricOverlap.get_neighbors not implemented yet")
