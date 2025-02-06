'''
Implementation for a simulated annealing algorithm
'''

import random
import sys
from math import exp

from neighborhoods import NeighborhoodDefinition
from problem import Solution

from .base import OptimizationAlgorithm

START_TEMP = 100.0
TEMP_STEPS = 10

# A simulated annealing is basically local search with the off chance of
# choosing a worse neighbor every now and then
class SimulatedAnnealing(OptimizationAlgorithm):
  '''Simulates the annealing process to search the solution space'''

  temperature: float
  inner_loop_counter: int
  # TODO: save best-so-far solution and present it to the user somehow

  def __init__(self, problem, neighborhood_definition: NeighborhoodDefinition = NeighborhoodDefinition.GEOMETRIC):
    super().__init__(problem)
    self.temperature = START_TEMP
    self.inner_loop_counter = 0
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

  def __accept_solution(self, new_solution: Solution):
    '''Checks whether a new solution shall be accepted or not'''
    # TODO: Is this a good idea?
    # If overall box count decreases, always accept
    if self.problem.current_solution.get_score()[0] > new_solution.get_score()[0]:
      self.problem.current_solution = new_solution
      return

    # If not strictly better, do the probabilistic acceptance on the incident edges
    score_delta = self.problem.current_solution.get_score()[1] - new_solution.get_score()[1]
    if score_delta <= 0:
      # New solution is better, update
      self.problem.current_solution = new_solution
    else:
      # Check for temperature chance
      if exp(-score_delta / self.temperature) > random.random():
        self.problem.current_solution = new_solution

  def __update_temperature(self):
    '''Can be called to update the temperature after each algorithm tick'''
    # Maybe we still need to do more steps at this temperature
    if self.inner_loop_counter < TEMP_STEPS:
      self.inner_loop_counter += 1
      return

    # If not, reset counter..
    self.inner_loop_counter = 0

    # .. and update the temperature according to the schedule
    # TODO: what's a good function here?
    self.temperature = self.temperature ** 0.995
    print(f"Temperature set to {self.temperature}")

  def tick(self):
     # Get all possible neighbors
    get_neighbors = self.neighborhood_definition.get_neighborhood_method()
    neighbors = get_neighbors(self.get_current_solution())

    if len(neighbors) == 0:
      print("Algorithm stuck! No neighbors could be found.")
      return

    # Get a random neighbor (but none that is invalid)
    neighbor = random.choice([n for n in neighbors if n.get_score() != (sys.maxsize, sys.maxsize)])

    # Possibly accept neighbor as new current solution
    self.__accept_solution(neighbor)

    # Update temperature
    self.__update_temperature()
