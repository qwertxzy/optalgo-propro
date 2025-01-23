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

    print(f"Found {len(neighbors)} neighbors")


    # Get the best score from the neighbors
    best_score = min([n.score for n in neighbors])
    print(f"Best score: {best_score}")

    # Pick one of the best neighbors at random
    # NOTE: Tends to plateau on two alternating solutions, so shuffle pick one of the best ones instead?

    # pick a neighbor with the best score
    best_neighbors = [n.move for n in neighbors if n.score == best_score]
    best_neighbor = random.choice(best_neighbors)

    # actually apply the move
    self.problem.current_solution.apply_move(best_neighbor)

    # calculate the score of the new solution
    best_score = self.problem.current_solution.get_score()
    print(f"now at score {self.problem.current_solution.get_score()}")

    print(f"Current score: {best_score}")
