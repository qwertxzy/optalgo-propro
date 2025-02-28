'''
Implementation of a local search algorithm
'''

import logging
import random

from modes import Neighborhood, Geometric, GeometricOverlap
from .base import OptimizationAlgorithm

logger = logging.getLogger(__name__)

class LocalSearch(OptimizationAlgorithm):
  '''
  Implements a local search through the solution space
  '''

  def __init__(self, problem, neighborhood_definition: Neighborhood = Geometric):
    super().__init__(problem)
    self.strategy = neighborhood_definition
    # TODO: just set permissible overlap here, should be set by some kind of schedule?
    #       can only be tested once neighborhood exploration speeds up..
    if neighborhood_definition == GeometricOverlap:
      self.problem.currently_permissible_overlap = 1.0

  def set_strategy(self, strategy: Neighborhood):
    '''Sets the neighborhood definition.'''
    logger.debug("Set the neighborhood definition to %s", strategy)
    self.strategy = strategy
    # See todo in __init__
    if self.strategy == GeometricOverlap:
      self.problem.currently_permissible_overlap = 1.0

  def tick(self):
    # Get all possible neighbors
    neighbors = self.strategy.get_neighbors(self.get_current_solution())

    if len(neighbors) == 0:
      logger.info("Algorithm stuck! No neighbors could be found.")
      return

    logger.info("Found %i neighbors", len(neighbors))

    best_score = min(n.get_score() for n in neighbors)
    # Pick one of the best neighbors at random
    best_neighbors = [n for n in neighbors if n.get_score() == best_score]
    best_neighbor = random.choice(best_neighbors)

    self.problem.current_solution = best_neighbor


    # TODO: also not really something that should be handled in the search algorithm?
    # Adjust permissible overlap
    if self.strategy == GeometricOverlap:
      current_overlap = self.problem.current_solution.currently_permissible_overlap
      new_overlap = max(0, current_overlap - 1  / self.problem.current_solution.get_score().box_count)
      self.problem.current_solution.currently_permissible_overlap = new_overlap

    logger.info("Now at score %s", self.problem.current_solution.get_score())
