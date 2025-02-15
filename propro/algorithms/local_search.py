'''
Implementation of a local search algorithm
'''

import random

from modes import Neighborhood, Geometric, GeometricOverlap
from .base import OptimizationAlgorithm

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
    print(f"Set the neighborhood definition to {strategy}")
    self.strategy = strategy
    # See todo in __init__
    if self.strategy == GeometricOverlap:
      self.problem.currently_permissible_overlap = 1.0

  def tick(self):
    # Get all possible neighbors
    neighbors = self.strategy.get_neighbors(self.get_current_solution())

    if len(neighbors) == 0:
      print("Algorithm stuck! No neighbors could be found.")
      return

    print(f"Found {len(neighbors)} neighbors")

    best_score = min([n.score for n in neighbors])
    # Pick one of the best neighbors at random
    best_neighbors = [n.move for n in neighbors if n.score == best_score]
    best_neighbor = random.choice(best_neighbors)
    # Actually apply the move
    best_neighbor.apply_to_solution(self.problem.current_solution)

    # TODO: also not really something that should be handled in the search algorithm?
    # Adjust permissible overlap
    current_overlap = self.problem.current_solution.currently_permissible_overlap
    new_overlap = max (0, current_overlap - 1  / self.problem.current_solution.get_score().box_count)
    self.problem.current_solution.currently_permissible_overlap = new_overlap

    print(f"Now at score {self.problem.current_solution.get_score()}")
