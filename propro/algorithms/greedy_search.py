'''
Implementation of a greedy search algorithm
'''
from typing import Any

from modes import SelectionSchema, SelectionMove
from problem import Problem
from .base import OptimizationAlgorithm

class GreedySearch(OptimizationAlgorithm):
  '''
  Implements a greedy selection scheme for the solution space
  '''

  unprocessed_objects: dict[int, Any]

  # Override constructor to strip initial solution
  def __init__(self, problem: Problem, selection_schema: SelectionSchema):
    self.unprocessed_objects = []
    self.strategy = selection_schema

    # Init the dict from the given initial solution
    # (this will clear the current solution as well)
    self.unprocessed_objects = { r.id: r for r in  problem.current_solution.to_greedy_queue() }

    # Now call the base constructor
    super().__init__(problem)

  def tick(self):
    # If there are no unplaced objects we are done here
    if len(self.unprocessed_objects) == 0:
      return

    # Get the next object with the given strategy
    next_move: SelectionMove = self.strategy.select(self.problem.current_solution, self.unprocessed_objects.values())

    # Insert it into the solution
    next_move.apply_to_solution(self.problem.current_solution, self.unprocessed_objects)
