'''
Contains different selection schemas for the greedy algorithm.
'''

from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass

from problem.box_problem.box_solution import BoxSolution
from problem.box_problem.geometry import Rectangle
from ..mode import Mode
from ..move import Move

class SelectionSchema(Mode):
  '''Base class for all different selection schemas'''

  @classmethod
  @abstractmethod
  def select(cls, partial_solution: BoxSolution, unprocessed_rects: list[Rectangle]) -> SelectionMove:
    '''
     Looks at the current solution and returns a tuple of
     rectangle id, box id and X/Y coordinate where it should be placed.
    '''

@dataclass
class SelectionMove(Move):
  '''
  Selection moves are not bound to a specific implementation
  since they always apply in the same way
  '''
  rect_id: int
  box_id: int

  def apply_to_solution(self, solution: BoxSolution, unprocessed_rects: dict[int, Rectangle] = None):
    '''Adds the given rect to the solution'''
    rect = unprocessed_rects.pop(self.rect_id)
    box = solution.boxes.get(self.box_id)
    box.add_rect(rect)

  def undo(self, solution: BoxSolution, unprocessed_rects:dict[int, Rectangle] = None):
    # Just remove this rect from the solution again
    box = solution.boxes.get(self.box_id)
    rect = box.remove_rect(self.rect_id)
    unprocessed_rects[rect.id] = rect
