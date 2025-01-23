'''
Utilities for the optimization algorithms
'''

from algorithms.base import OptimizationAlgorithm
from neighborhoods import NeighborhoodDefinition
from selections import SelectionSchema


def get_mode(algo: OptimizationAlgorithm):
  '''Returns either neighborhood definitions or selection schemas depending on the algorithm'''
  # Matching by name is a little weird, but type() would only return ABC for both cases..
  match algo.__name__:
    case "LocalSearch": return NeighborhoodDefinition
    case "GreedySearch": return SelectionSchema
    case "SimulatedAnnealing": return NeighborhoodDefinition
