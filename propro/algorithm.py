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

    if len(neighbors) == 0:
      print("Algorithm stuck! No neighbors could be found.")
      return

    # Get the best score from the neighbors
    best_score = min(neighbors, key=lambda n: n.get_score()).get_score()

    # Pick one of the best neighbors at random
    # NOTE: Tends to plateau on two alternating solutions, so shuffle pick one of the best ones instead?
    self.problem.current_solution = random.choice([n for n in neighbors if n.get_score() == best_score])
    print(f"Current score: {best_score}")


from problem import Rectangle

class GreedySearch(OptimizationAlgorithm):
  '''
  Implements a greedy selection scheme for the solution space
  '''

  # TODO: is this generic enough of an interface? How to generify this?
  unplaced_rects: list[Rectangle]

  # Override constructor to remove all initially placed rects
  def __init__(self, problem, selection_schema):
    self.unplaced_rects = []
    for box in problem.current_solution.boxes.values():
      for rect_id in list(box.rects.keys()):
        self.unplaced_rects.append(box.remove_rect(rect_id))

    # IDEA: sort rects by size to use big ones first
    self.unplaced_rects.sort(key=lambda r: r.get_area(), reverse=False)

    # Now call the base constructor
    super().__init__(problem)

  def tick(self):
    # If there are no unplaced rects we are done here
    if len(self.unplaced_rects) == 0:
      return

    # TODO: make this dynamic like neighborhoods
    selection_method = SelectionSchema.FIRST_FIT.get_selection_schema()
    # Pop a rect from the list and get the best move
    next_rect = self.unplaced_rects.pop()
    self.problem.current_solution = selection_method(self.problem.current_solution, next_rect)

def get_mode(algo: OptimizationAlgorithm):
  '''Returns either neighborhood definitions or selection schemas depending on the algorithm'''
  # Matching by name is a little weird, but type() would only return ABC for both cases..
  match algo.__name__:
    case "LocalSearch": return NeighborhoodDefinition
    case "GreedySearch": return SelectionSchema
