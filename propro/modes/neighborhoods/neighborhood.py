'''
Contains a basic neighborhood definition that must be inherited from
'''
from abc import ABC, abstractmethod

from problem import BoxSolution
from ..move import Move

class Neighborhood(ABC):
  '''Abstract neighborhood base class'''

  neighbors = []

  # MAX_NEIGHBORS = 250

  @classmethod
  @abstractmethod
  def get_neighbors(cls, solution: BoxSolution) -> list[Move]:
    '''
    Calculates neighbors of a given start solution.
    '''
