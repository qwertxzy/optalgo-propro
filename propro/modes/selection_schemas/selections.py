'''
Contains different selection schemas for the greedy algorithm.
'''

from __future__ import annotations
from abc import abstractmethod

from problem import BoxSolution
from ..mode import Mode

class SelectionSchema(Mode):
  '''Base class for all different selection schemas'''

  @classmethod
  @abstractmethod
  def select(cls, partial_solution: BoxSolution) -> BoxSolution:
    '''
     Looks at the current solution and places one of the unplaced rectangles in a box.
    '''
