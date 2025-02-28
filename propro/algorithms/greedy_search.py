'''
Implementation of a greedy search algorithm
'''

from modes import SelectionSchema
from problem import Problem
from .base import OptimizationAlgorithm

class GreedySearch(OptimizationAlgorithm):
  '''
  Implements a greedy selection scheme for the solution space
  '''

  strategy: SelectionSchema

  # Override constructor to strip initial solution
  def __init__(self, problem: Problem, selection_schema: SelectionSchema):
    self.strategy = selection_schema

    # Need to call prepare method to unplace all rects
    problem.prepare_greedy()

    # Now call the base constructor
    super().__init__(problem)

  def tick(self):
    # If there are no unplaced objects we are done here
    if self.problem.greedy_done():
      return

    # Do the next move with the given selection strategy
    self.problem.current_solution = self.strategy.select(self.problem.current_solution)
