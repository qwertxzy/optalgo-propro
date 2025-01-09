'''
Module contains a base definition as well as several
different implementations of an optimization algorithm.
'''

from abc import ABC, abstractmethod
import random

from problem import Problem, Solution
from neighborhoods import NeighborhoodDefinition
from selections import SelectionSchema

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