'''
Utilities for the optimization algorithms
'''
from typing import Type

from algorithms.base import OptimizationAlgorithm
from neighborhoods.neighborhood import Neighborhood
from selection_schemas.selections import SelectionSchema


def get_modes(algo: OptimizationAlgorithm) -> (list[Type[Neighborhood]] | list[Type[SelectionSchema]]):
  '''Returns either neighborhood definitions or selection schemas depending on the algorithm'''
  # Matching by name is a little weird, but type() would only return ABC for both cases..
  match algo.__name__:
    case "LocalSearch": return [m for m in Neighborhood.__subclasses__()]
    case "GreedySearch": return SelectionSchema.__subclasses__()
    case _: raise ValueError("Algorithm not supported")

def get_mode(algo: Type[OptimizationAlgorithm], mode_name: str) -> Type[Neighborhood] | Type[SelectionSchema]:
  '''Returns the correct mode class based on the algorithm'''
  if not mode_name:
    match algo.__name__:
      case "LocalSearch": return Neighborhood.__subclasses__()[0]
      case "GreedySearch": return SelectionSchema.__subclasses__()[0]
      case _: raise ValueError("Algorithm not supported")
  match algo.__name__:
    case "LocalSearch": return next(filter(lambda m: m.__name__ == mode_name, Neighborhood.__subclasses__()))
    case "GreedySearch": return next(filter(lambda m: m.__name__ == mode_name, SelectionSchema.__subclasses__()))
    case _: raise ValueError("Algorithm not supported")

def get_mode_superclass(algo: Type[OptimizationAlgorithm]) -> Type[Neighborhood] | Type[SelectionSchema]:
  '''Returns the superclass of the modes based on the algorithm'''
  match algo.__name__:
    case "LocalSearch": return Neighborhood
    case "GreedySearch": return SelectionSchema
    case _: raise ValueError("Algorithm not supported")
