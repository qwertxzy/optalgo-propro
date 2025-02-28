'''
Contains a basic neighborhood definition that must be inherited from
'''
from abc import ABC, abstractmethod

from problem import BoxSolution

class Neighborhood(ABC):
  '''Abstract neighborhood base class'''

  neighbors = []

  @classmethod
  @abstractmethod
  def get_neighbors(cls, solution: BoxSolution) -> list[BoxSolution]:
    '''
    Takes a solution and returns a list of neighboring solutions
    with the first index being for each neighbor.
    '''
