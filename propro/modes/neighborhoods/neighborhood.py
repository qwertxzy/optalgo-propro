'''
Contains a basic neighborhood definition that must be inherited from
'''
from abc import ABC, abstractmethod

from problem import BoxSolution
from ..move import Move, ScoredMove


class Neighborhood(ABC):
  '''Abstract neighborhood base class'''

  #TODO: place the abstract heuristic score stuff here.
  # Now it is in the problem.py. But it is mode-specific, so it should be here.

  @classmethod
  @abstractmethod
  def initialize(cls, solution: BoxSolution) -> BoxSolution:
    '''Initializes the neighborhood for the given solution.'''

  @classmethod
  @abstractmethod
  def evaluate_moves(cls, solution: BoxSolution, moves: list[Move]) -> list[ScoredMove]:
    '''Takes a list of moves and evaluates them on the given solution.'''
    # return [
    #   ScoredMove(move, solution.calculate_heuristic_score(move))
    #   for move in moves
    # ]

  @classmethod
  @abstractmethod
  def get_neighbors(cls, solution: BoxSolution) -> list[Move]:
    '''
    Calculates neighbors of a given start solution.
    '''

  @classmethod
  @abstractmethod
  def generate_heuristic(cls, solution: BoxSolution, move: Move) -> float:
    '''
    Calculates a heuristic score for a given solution.
    '''
