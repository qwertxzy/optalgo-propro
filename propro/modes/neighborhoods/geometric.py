import logging
from dataclasses import dataclass

from problem import BoxSolution
from geometry import Box

from .neighborhood import Neighborhood
from ..move import Move, ScoredMove

logger = logging.getLogger(__name__)

class Geometric(Neighborhood):
  '''Implementation for a geometry-based neighborhood'''

  # TODO: Add the option to move a rect into a new box? Might be needed for simulated annealing

  # Incident edges will create local minima from which the neighborhood cannot escape
  # There needs to be a bonus for moving rects from an almost empty box to a crowded one maybe?
  # IDEA: Introduce a sort of box entropy to the score, would need to count empty boxes too
  # IDEA: Rects could be fixed to cut down on neighborhood size. Maybe large ones? All rects of a box when there are 0 free coords

  @classmethod
  def get_neighbors(cls, solution: BoxSolution) -> list[ScoredMove]:
    '''
    Calculates neighbors of a solution by geometric means
    Moves every rectangle in every box to every possible coordinate
    '''
    logger.info("Calculating Geometric neighborhoods")
    neighbors = []
    current_score = solution.get_score()

    # Iterate over all rectangles in all boxes
    for current_box in sorted(solution.boxes.values(), key=lambda box: len(box.rects)):
      # TODO: switch from desc to asc sorting at some point (after the initial early-return phase?)
      # IDEA: Prioritize rects on generating valid moves?
      for current_rect in sorted(current_box.rects.values(), key=lambda rect: rect.get_area(), reverse=True):
        # Now iterate over all possible moves! A rect can be placed
        # ... in any box
        for possible_box in solution.boxes.values():
          # ... in any free coordinate within this box
          for (x, y) in list(possible_box.get_adjacent_coordinates()):
            # ... at any rotation
            for is_flipped in [False, True]:

              # no move
              if all([
                current_box.id == possible_box.id,
                current_rect.get_x() == x,
                current_rect.get_y() == y,
                not is_flipped
              ]):
                continue

              # no flip if the rect is square
              if current_rect.width == current_rect.height and is_flipped:
                continue

              move = GeometricMove(current_rect.id, current_box.id, possible_box.id, x, y, is_flipped)

              # Calculate the score of the new solution
              score = solution.get_potential_score(move)

              # Skip invalid solutions
              if score.box_count is None:
                continue

              # add it to the neighbors
              neighbors.append(ScoredMove(move, score))

              # Once a solution found that removes one box entirely, early return
              if current_score.box_count > score.box_count:
                logger.info("Early returned with %i neighbors. Removed one Box.", len(neighbors))
                return neighbors

              if len(neighbors) > max(cls.MAX_NEIGHBORS, len(solution.boxes) ** 2):
                logger.info("Early returned with %i neighbors", len(neighbors))
                return neighbors
    logger.info("Explored all %i neighbors", len(neighbors))
    return neighbors

@dataclass
class GeometricMove(Move):
  '''Defines a move as a literal movement of a rectangle from one box to another'''
  rect_id: int
  from_box_id: int
  to_box_id: int
  new_x: int
  new_y: int
  flip: bool

  old_x: int
  old_y: int

  def __init__(self, rect_id: int, from_box_id: int, to_box_id:int, new_x: int, new_y: int, flip: bool):
    self.rect_id = rect_id
    self.from_box_id = from_box_id
    self.to_box_id = to_box_id
    self.new_x = new_x
    self.new_y = new_y
    self.flip = flip
    self.old_x = None
    self.old_y = None

  def apply_to_solution(self, solution: BoxSolution):
    '''Applies this move to a given box solution'''
    # Get rect in old box
    current_box = solution.boxes[self.from_box_id]
    current_rect = current_box.remove_rect(self.rect_id)

    # Save the old rect coordinates in case of undo
    self.old_x = current_rect.get_x()
    self.old_y = current_rect.get_y()

    # Update rect coordinates
    current_rect.move_to(self.new_x, self.new_y)
    if self.flip:
      current_rect.flip()

    new_box = solution.boxes[self.to_box_id]
    new_box.add_rect(current_rect)

    # If the current box is now empty, remove it from the solution
    if len(current_box.rects) == 0:
      solution.boxes.pop(self.from_box_id)

  def undo(self, solution: BoxSolution):
    '''Undoes whatever this move had done to the argument solution'''
    if self.old_x is None or self.old_y is None:
      raise ValueError("Undo called without the move being performed before!")

    # Remove rect from target box
    rect = solution.boxes.get(self.to_box_id).remove_rect(self.rect_id)

    # Restore attributes
    rect.move_to(self.old_x, self.old_y)
    if self.flip:
      rect.flip()

    # Maybe the old box was deleted by the move? Otherwise just add it back
    if self.from_box_id not in solution.boxes.keys():
      solution.boxes[self.from_box_id] = Box(self.from_box_id, solution.side_length, rect)
    else:
      solution.boxes[self.from_box_id].add_rect(rect)
