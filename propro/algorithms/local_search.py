from algorithms.base import OptimizationAlgorithm
from neighborhoods import NeighborhoodDefinition
import random

class LocalSearch(OptimizationAlgorithm):
  '''
  Implements a local search through the solution space
  '''

  neighborhood_definition: NeighborhoodDefinition

  def __init__(self, problem, neighborhood_definition: NeighborhoodDefinition = NeighborhoodDefinition.GEOMETRIC):
    super().__init__(problem)
    self.neighborhood_definition = neighborhood_definition
    # TODO: just set permissible overlap here, should be set by some kind of schedule?
    #       can only be tested once neighborhood exploration speeds up..
    if neighborhood_definition == NeighborhoodDefinition.GEOMETRIC_OVERLAP:
      self.problem.currently_permissible_overlap = 0.2

  def set_neighborhood_definition(self, neighborhood_definition: NeighborhoodDefinition):
    '''Sets the neighborhood definition.'''
    print(f"Set the neighborhood definition to {neighborhood_definition}")
    self.neighborhood_definition = neighborhood_definition
    # See todo in __init__
    if neighborhood_definition == NeighborhoodDefinition.GEOMETRIC_OVERLAP:
      self.problem.currently_permissible_overlap = 0.2

  def tick(self):
    # Get all possible neighbors
    get_neighbors = self.neighborhood_definition.get_neighborhood_method()
    neighbors = get_neighbors(self.get_current_solution())

    if len(neighbors) == 0:
      print("Algorithm stuck! No neighbors could be found.")
      return

    # Get the best score from the neighbors
    best_score = min(neighbors, key=lambda n: n.get_score()).get_score()

    # Pick one of the best neighbors at random
    # NOTE: Tends to plateau on two alternating solutions, so shuffle pick one of the best ones instead?
    self.problem.current_solution = random.choice([n for n in neighbors if n.get_score() == best_score])
    print(f"Current score: {best_score}")
