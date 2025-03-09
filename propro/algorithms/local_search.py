'''
Implementation of a local search algorithm
'''

import logging
import random

from modes import Neighborhood, Geometric, Permutation
from .base import OptimizationAlgorithm

logger = logging.getLogger(__name__)

class LocalSearch(OptimizationAlgorithm):
  '''
  Implements a local search through the solution space
  '''

  def __init__(self, problem, neighborhood_definition: Neighborhood = Geometric):
    super().__init__(problem)
    self.strategy = neighborhood_definition
    # if Permutation is used, rerun the current solution
    if self.strategy == Permutation:
      self.problem.current_solution = self.strategy.initialize(self.problem.current_solution)

  def set_strategy(self, strategy: Neighborhood):
    '''Sets the neighborhood definition.'''
    logger.debug("Set the neighborhood definition to %s", strategy)
    self.strategy = strategy

  def tick(self):
    # Get all possible neighbors
    neighbors = self.strategy.get_neighbors(self.problem.current_solution)

    if len(neighbors) == 0:
      logger.info("Algorithm stuck! No neighbors could be found.")
      return

    logger.info("Found %i neighbors", len(neighbors))

    best_score = min(n.score for n in neighbors)

    # if best_score > self.problem.current_solution.get_heuristic_score():
    #   logger.warning("Algorithm reached a local minimum.")
    #   return

    # Pick one of the best neighbors at random
    best_neighbors = [n.move for n in neighbors if n.score == best_score]
    best_neighbor = random.choice(best_neighbors)

    # Actually apply the move
    best_neighbor.apply_to_solution(self.problem.current_solution)

    # Per definition the current solution will also be the best solution
    self.best_solution = self.problem.current_solution

    logger.info("Now at score %s", self.problem.current_solution.get_heuristic_score())
