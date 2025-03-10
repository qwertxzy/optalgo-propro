'''
Module contains a base definition of an optimization algorithm
'''

from abc import ABC, abstractmethod

from problem.problem import Problem, Solution
from modes import Mode

class OptimizationAlgorithm(ABC):
  '''
  Abstract base class for an optimization algorithm.
  Expects to implement something to initialize the algorithm and something to compute one iteration.
  '''
  problem: Problem
  '''The problem this algorithm was tasked to solve'''
  strategy: Mode
  '''The strategy chosen for this algorithm'''
  best_solution: Solution
  '''The best solution the algorithm has produced so far'''

  def __init__(self, problem: Problem):
    self.problem = problem
    self.best_solution = problem.current_solution

  def set_strategy(self, strategy: Mode):
    '''Sets the strategy for the algorithm.'''
    self.strategy = strategy

  @abstractmethod
  def tick(self) -> Solution:
    '''
    Runs the algorithm for one iteration.
    '''
