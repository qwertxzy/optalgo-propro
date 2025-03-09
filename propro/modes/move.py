'''
This module contains classes arount the concept of a 'move'
which brings you from one solution to a neighboring one
'''

from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar, Generic
from abc import ABC, abstractmethod

from problem import Solution
from heuristic import AbstractHeuristic

class Move(ABC):
  '''
  Represents a move from one (partial) solution to another.
  '''

  @abstractmethod
  def apply_to_solution(self, solution: Solution):
    '''Applies this move to a given solution'''

  @abstractmethod
  def undo(self, solution: Solution):
    '''Reverts the changes to the solution from this move'''

H = TypeVar('H', bound=AbstractHeuristic)
@dataclass
class ScoredMove(Generic[H]):
  '''
  Represents a move with its potential score.
  '''
  move: Move
  score: AbstractHeuristic

  def __iter__(self):
    return iter((self.move, self.score))

  def is_valid(self) -> bool:
    '''Returns true if applying this move results in a valid solution'''
    return self.score.is_valid()
