'''
Contains a basic neighborhood definition that must be inherited from
'''
from abc import ABC, abstractmethod

from problem import BoxSolution
from ..move import Move, ScoredMove

class Neighborhood(ABC):
  '''Abstract neighborhood base class'''

  @classmethod
  def evaluate_moves(cls, solution: BoxSolution, moves: list[Move]) -> list[ScoredMove]:
    '''Takes a list of moves and evaluates them on the given solution.'''
    return [
      ScoredMove(move, solution.get_potential_score(move))
      for move in moves
    ]

  @classmethod
  @abstractmethod
  def get_neighbors(cls, solution: BoxSolution) -> list[Move]:
    '''
    Calculates neighbors of a given start solution.
    '''
