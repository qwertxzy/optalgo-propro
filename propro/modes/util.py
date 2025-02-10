from typing import Optional
from itertools import chain

from .mode import Mode
from .neighborhoods import Neighborhood
from .selection_schemas import SelectionSchema

def get_available_modes(algo) -> list[Mode]:
  '''Returns a list of possible modes for a given algorithm'''
  # If algo was none, just return all options
  if algo is None:
    return chain(Neighborhood.__subclasses__(), SelectionSchema.__subclasses__())

  # Matching by name is a little weird, but type() would only return ABC for both cases..
  match algo.__name__:
    case "LocalSearch": return Neighborhood.__subclasses__()
    case "GreedySearch": return SelectionSchema.__subclasses__()
    case _: raise ValueError("Algorithm not supported")

def get_mode_by_name(algo, name: str) -> Optional[Mode]:
  '''Returns the mode class with a given name or none if no name matched'''
  return next(filter(lambda m: m.__name__ == name, get_available_modes(algo)), None)
