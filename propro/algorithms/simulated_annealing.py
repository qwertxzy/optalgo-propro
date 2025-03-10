'''
Implementation for a simulated annealing algorithm
'''

import logging
import random
from math import exp

from modes import Neighborhood, Geometric, ScoredMove

from .base import OptimizationAlgorithm

START_TEMP = 100.0
TEMP_STEPS = 10

logger = logging.getLogger(__name__)

# A simulated annealing is basically local search with the off chance of
# choosing a worse neighbor every now and then
class SimulatedAnnealing(OptimizationAlgorithm):
  '''Simulates the annealing process to search the solution space'''

  temperature: float
  inner_loop_counter: int

  def __init__(self, problem, neighborhood_definition: type[Neighborhood] = Geometric):
    self.strategy = neighborhood_definition
    problem.current_solution = self.strategy.initialize(problem.current_solution)
    super().__init__(problem)
    self.temperature = START_TEMP
    self.inner_loop_counter = 0

  def set_strategy(self, strategy: type[Neighborhood]):
    '''Sets the neighborhood definition.'''
    logger.info("Set the neighborhood definition to %s", strategy)
    self.strategy = strategy


  def __accept_solution(self, scored_move: ScoredMove):
    '''Checks whether a new solution shall be accepted or not'''
    # NOTE: Not generic in the sense of the assignment, but needs to work on all score fields
    current_score = self.strategy.generate_heuristic(self.problem.current_solution)
    # If score is better, apply move
    if current_score > scored_move.score:
      scored_move.move.apply_to_solution(self.problem.current_solution)
      return

    # Draw a random number
    rand = random.random()

    curr_score_iter = iter(current_score)
    scored_score_iter = iter(scored_move.score)
    for curr, new in zip(curr_score_iter, scored_score_iter):
      delta = curr - new
      if exp(delta / self.temperature) > rand:
        scored_move.move.apply_to_solution(self.problem.current_solution)
        return

  def __update_temperature(self):
    '''Can be called to update the temperature after each algorithm tick'''
    # Maybe we still need to do more steps at this temperature
    if self.inner_loop_counter < TEMP_STEPS:
      self.inner_loop_counter += 1
      return

    # If not, reset counter..
    self.inner_loop_counter = 0

    # .. and update the temperature according to the schedule
    # Adaptive exponential cooling?
    cooling_rate = 0.99 - (0.1 * (self.inner_loop_counter / TEMP_STEPS))
    self.temperature *= cooling_rate
    logger.info("Temperature set to %f", self.temperature)

  def tick(self):
     # Get all possible neighbors
    neighbors = self.strategy.get_neighbors(self.problem.current_solution)

    if len(neighbors) == 0:
      logger.warning("Algorithm stuck! No neighbors could be found.")
      return

    logger.info("Found %i neighbors", len(neighbors))

    # Get a random move
    neighbor = random.choice(neighbors)

    # Possibly accept neighbor as new current solution
    self.__accept_solution(neighbor)

    # Update temperature
    self.__update_temperature()

    logger.info("Now at score %s", self.strategy.generate_heuristic(self.problem.current_solution))
