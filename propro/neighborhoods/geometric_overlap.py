
from .neighborhood import Neighborhood
from problem import BoxSolution


class GeometricOverlap(Neighborhood):
        
    @classmethod    
    def get_neighbors(cls, solution: BoxSolution) -> list:
        neighbors = []
        print("Claculating Geometric Overlap neighborhood")
        raise NotImplementedError("GeometricOverlap.get_neighbors not implemented yet")