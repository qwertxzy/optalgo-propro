'''
Implementation of a greedy search algorithm
'''

from modes import SelectionSchema
from problem import Rectangle
from .base import OptimizationAlgorithm

class GreedySearch(OptimizationAlgorithm):
  '''
  Implements a greedy selection scheme for the solution space
  '''

  # TODO: is this generic enough of an interface? How to generify this?
  unplaced_rects: list[Rectangle]

  # Override constructor to remove all initially placed rects
  def __init__(self, problem, selection_schema: SelectionSchema):
    self.unplaced_rects = []
    self.strategy = selection_schema

    for box in problem.current_solution.boxes.values():
      for rect_id in list(box.rects.keys()):
        self.unplaced_rects.append(box.remove_rect(rect_id))

    # IDEA: sort rects by size to use big ones first
    self.unplaced_rects.sort(key=lambda r: r.get_area(), reverse=False)

    # Remove now empty boxes from solution
    problem.current_solution.boxes.clear()

    # Now call the base constructor
    super().__init__(problem)

  def tick(self):
    # If there are no unplaced rects we are done here
    if len(self.unplaced_rects) == 0:
      return

    #selection_method = GreedySearch.strategy.get_selection_schema()
    # Pop a rect from the list and get the best move
    next_rect = self.unplaced_rects.pop()
    self.problem.current_solution = self.strategy.select(self.problem.current_solution, next_rect)
