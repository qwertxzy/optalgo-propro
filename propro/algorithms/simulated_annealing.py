'''
Implementation for a simulated annealing algorithm
'''

import random
import sys

from neighborhoods import NeighborhoodDefinition

from .base import OptimizationAlgorithm

START_TEMP = 100.0

# A simulated annealing is basically local search with the off chance of
# choosing a worse neighbor every now and then
class SimulatedAnnealing(OptimizationAlgorithm):
  '''Simulates the annealing process to search the solution space'''

  temperature: float

  def __init__(self, problem, neighborhood_definition: NeighborhoodDefinition = NeighborhoodDefinition.GEOMETRIC):
    super().__init__(problem)
    self.temperature = START_TEMP
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

    # Get a random neighbor (but none that is invalid)
    neighbor = random.choice([n for n in neighbors if n.get_score() != (sys.maxsize, sys.maxsize)])

    accept_move = False
    # If the score is better, always accept move
    if neighbor.get_score() < self.get_current_solution().get_score():
      accept_move = True
    else:
      # If random value in the temp range is below current temp, also accept
      if random.randint(0, int(START_TEMP)) <= self.temperature:
        accept_move = True

    if accept_move:
      self.problem.current_solution = neighbor

    # Adjust temperature
    # TODO: needs a proper cooling schedule
    self.temperature = self.temperature * 0.95
    print(f"Temperature: {self.temperature}")
