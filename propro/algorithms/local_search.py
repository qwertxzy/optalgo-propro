'''
Implementation of a local search algorithm
'''

import random
from typing import Type

from neighborhoods.neighborhood import Neighborhood
from neighborhoods.geometric import Geometric
from neighborhoods.geometric_overlap import GeometricOverlap

from .base import OptimizationAlgorithm

class LocalSearch(OptimizationAlgorithm):
  '''
  Implements a local search through the solution space
  '''
  # strategy: Type[Neighborhood]

  def __init__(self, problem, neighborhood_definition: Type[Neighborhood] = Geometric):
    super().__init__(problem)
    LocalSearch.strategy = neighborhood_definition
    # TODO: just set permissible overlap here, should be set by some kind of schedule?
    #       can only be tested once neighborhood exploration speeds up..
    if neighborhood_definition == GeometricOverlap:
      self.problem.currently_permissible_overlap = 0.2

  def set_strategy(self, neighborhood_definition: Neighborhood):
    '''Sets the neighborhood definition.'''
    print(f"Set the neighborhood definition to {neighborhood_definition}")
    LocalSearch.strategy = neighborhood_definition
    # See todo in __init__
    if LocalSearch.strategy == GeometricOverlap:
      self.problem.currently_permissible_overlap = 0.2

  def tick(self):
    # Get all possible neighbors
    neighbors = LocalSearch.strategy.get_neighbors(self.get_current_solution())

    if len(neighbors) == 0:
      print("Algorithm stuck! No neighbors could be found.")
      return

    # Get the best score from the neighbors
    best_score = min(neighbors, key=lambda n: n.get_score()).get_score()

    # Pick one of the best neighbors at random
    # NOTE: Tends to plateau on two alternating solutions, so shuffle pick one of the best ones instead?
    self.problem.current_solution = random.choice([n for n in neighbors if n.get_score() == best_score])
    print(f"Current score: {best_score}")
