from abc import ABC, abstractmethod
from problem.heuristic import AbstractHeuristic

class Solution(ABC):
  '''
  Abstract base class for a generic optimization solution.
  '''
  @abstractmethod
  def get_heuristic_score(self) -> AbstractHeuristic:
    '''
    Computes and returns the score of this solution.
    '''
  @abstractmethod
  def is_valid(self) -> bool:
    '''
    Checks whether this solution is valid in the first place.
    '''
