from algorithms.base import OptimizationAlgorithm
from selections import SelectionSchema
from problem import Rectangle
import random

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
