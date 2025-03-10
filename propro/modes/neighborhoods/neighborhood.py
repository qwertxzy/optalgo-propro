'''
Contains a basic neighborhood definition that must be inherited from
'''
from abc import ABC, abstractmethod

from problem.box_problem.box_solution import BoxSolution
from problem.heuristic import AbstractHeuristic
from ..move import Move, ScoredMove


class Neighborhood(ABC):
  '''Abstract neighborhood base class'''

  #TODO: place the abstract heuristic score stuff here. Now it is in the problem.py. But it is mode-specific, so it should be here.
  
  @classmethod
  def initialize(cls, solution: BoxSolution) -> BoxSolution:
    '''Initializes the neighborhood for the given solution.'''
    pass

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
  def get_neighbors(cls, solution: BoxSolution) -> list[ScoredMove]:
    '''
    Calculates neighbors of a given start solution.
    '''

  @classmethod
  @abstractmethod
  def generate_heuristic(cls, solution: BoxSolution, move: Move = None) -> AbstractHeuristic:
    '''
    Calculates a heuristic score for a given solution after applying a move.
    If the move is None, the heuristic score of the solution is calculated.
    '''
