'''
Module contains a base definition as well as several
different implementations of an optimization algorithm.
'''

from abc import ABC, abstractmethod
import random

from problem import Problem, Solution
from neighborhoods import NeighborhoodDefinition

class OptimizationAlgorithm(ABC):
  '''
  Abstract base class for an optimization algorithm.
  Expects to implement something to initialize the algorithm and something to compute one iteration.
  '''
  problem: Problem

  def __init__(self, problem):
    self.problem = problem

  @abstractmethod
  def tick(self) -> Solution:
    '''
    Runs the algorithm for one iteration.
    '''

  def get_current_solution(self) -> Solution:
    '''
    Getter for the current solution.
    '''
    return self.problem.current_solution

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

    # Get the best score from the neighbors
    best_score = min(neighbors, key=lambda n: n.get_score()).get_score()

    # Pick one of the best neighbors at random
    # NOTE: Tends to plateau on two alternating solutions, so shuffle pick one of the best ones instead?
    self.problem.current_solution = random.choice([n for n in neighbors if n.get_score() == best_score])


class GreedySearch(OptimizationAlgorithm):
  '''
  Implements a greedy selection scheme for the solution space
  '''
  # TODO: implement me
