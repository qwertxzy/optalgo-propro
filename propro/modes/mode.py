from abc import ABC
from problem.solution import Solution

class Mode(ABC):
  '''Base class for different algorithm modes'''

  @classmethod
  def initialize(cls, solution: Solution) -> Solution:
    '''Hook which modes can call to initialize a solution to their liking'''
    return solution
