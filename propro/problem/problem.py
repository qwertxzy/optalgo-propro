'''
Module contains an abstract problem definition as well as the
concrete implementation for the box-rectangle problem given.
'''

from __future__ import annotations
from abc import ABC, abstractmethod
from random import choice
from itertools import combinations
from dataclasses import dataclass
from math import log2
from collections import deque

from problem.solution import Solution
from .box_problem.geometry import Rectangle, Box
from .heuristic import AbstractHeuristic


#TODO: need to ersetzen the calls to this method from the box_solution class with the Heuristic score calls.
@dataclass
class Score:
  '''
  Represents the score of a solution.
  `None` as a box count will indicate an invalid solution.
  '''
  box_count: int
  '''Number of overall boxes in this solution. Lower is better.'''
  # Was planned as 'gain' but that can only work on a move, not on a solution
  box_entropy: int
  '''Measure of how distributed rects are among boxes. Lower is better.'''
  incident_edges: int
  '''Number of coordinates shared by two adjacent rects. Higher is better.'''

  def __iter__(self):
    return iter((self.box_count, self.box_entropy, self.incident_edges))


class Problem(ABC):
  '''
  Abstract base class for a generic optimization problem.
  '''
  current_solution: Solution
