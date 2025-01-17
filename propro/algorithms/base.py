'''
Module contains a base definition of an optimization algorithm
'''

from abc import ABC, abstractmethod
from typing import Type

from problem import Problem, Solution
from neighborhoods.neighborhood import Neighborhood
from selection_schemas.selections import SelectionSchema

class OptimizationAlgorithm(ABC):
  '''
  Abstract base class for an optimization algorithm.
  Expects to implement something to initialize the algorithm and something to compute one iteration.
  '''
  problem: Problem
  strategy: Type[SelectionSchema] | Type[Neighborhood]

  def __init__(self, problem):
    self.problem = problem

  def set_strategy(self, strategy: Type[SelectionSchema] | Type[Neighborhood]):
    '''Sets the strategy for the algorithm.'''
    self.strategy = strategy

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
