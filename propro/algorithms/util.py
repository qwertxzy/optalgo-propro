from typing import Optional

from .base import OptimizationAlgorithm

def get_algo_by_name(name) -> Optional[OptimizationAlgorithm]:
  '''Returns the mode class with a given name or none if no name matched'''
  return next(filter(lambda a: a.__name__ == name, OptimizationAlgorithm.__subclasses__()), None)
