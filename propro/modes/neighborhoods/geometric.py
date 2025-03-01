from __future__ import annotations
import logging
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
from copy import deepcopy

import numpy as np

from problem import BoxSolution
from geometry import Box
from utils import flatten


from .neighborhood import Neighborhood
from ..move import Move, ScoredMove

logger = logging.getLogger(__name__)

class Geometric(Neighborhood):
  '''Implementation for a geometry-based neighborhood'''

  # TODO: Add the option to move a rect into a new box? Might be needed for simulated annealing
  # TODO: places lots of small rects in the first box which could be used to fill gaps elsewhere
  # IDEA: Rects could be fixed to cut down on neighborhood size. Maybe large ones? All rects of a box when there are 0 free coords

  # TODO: new bottleneck is this method
  @classmethod
  def generate_neighbor_moves(cls, solution: BoxSolution) -> list[GeometricMove]:
    '''Generates a list of moves from the current solution to its neighbros'''
    # Construct a list of possible moves
    moves = []

    boxes_by_rect_count_asc = sorted(solution.boxes.values(), key=lambda box: len(box.rects))

    # Iterate over all rectangles in all boxes
    for current_box in boxes_by_rect_count_asc:
      # IDEA: switch from desc to asc sorting at some point (after the initial early-return phase?)
      # IDEA: Prioritize rects on generating valid moves?
      for current_rect in sorted(current_box.rects.values(), key=lambda rect: rect.get_area(), reverse=True):
        # Now iterate over all possible moves! A rect can be placed
        # ... in any box (by rect count descending -> prefer full boxes)
        for possible_box in reversed(boxes_by_rect_count_asc):
          # ... in any free coordinate within this box
          for (x, y) in possible_box.get_adjacent_coordinates():
            # ... at any rotation
            for is_flipped in [False, True]:

              # Rect would overflow
              if any([
                not is_flipped and (x + current_rect.width > possible_box.side_length),
                not is_flipped and (y + current_rect.height > possible_box.side_length),
                is_flipped and (y + current_rect.width > possible_box.side_length),
                is_flipped and (x + current_rect.height > possible_box.side_length),
              ]):
                continue

              # No move
              if all([
                current_box.id == possible_box.id,
                current_rect.get_x() == x,
                current_rect.get_y() == y,
                not is_flipped
              ]):
                continue

              # No flip if the rect is square
              if current_rect.width == current_rect.height and is_flipped:
                continue

              move = GeometricMove(current_rect.id, current_box.id, possible_box.id, x, y, is_flipped)
              moves.append(move)

              # If this was a box decreasing move, break the loop and continue with what we have
              # TODO: check if this is really a good idea..
              if move.is_boxcount_decreasing(solution):
                logger.info("Returned early with box-count decrease")
                return moves
    return moves

  @classmethod
  def get_neighbors(cls, solution: BoxSolution) -> list[ScoredMove]:
    '''
    Calculates neighbors of a solution by geometric means
    Moves every rectangle in every box to every possible coordinate
    '''
    logger.info("Calculating Geometric neighborhoods")

    moves = cls.generate_neighbor_moves(solution)

    logger.info("Generated %i moves", len(moves))

    # Now evaluate all these moves in parallel
    n_proc = max(6, cpu_count()) # How many do we want?

    # If we have more than 20 moves per chunk, go multithreaded
    if len(moves) >= n_proc * 20:
      # Copy the current solution so every thread can modify it independently
      # Expensive, but worth it (hopefully)
      solution_copies = [deepcopy(solution) for _ in range(n_proc)]

      # Split moves into chunks for pool to process
      chunks = np.array_split(moves, n_proc)

      # Evaluate all moves to scored moves concurrently
      with Pool(processes=n_proc) as pool:
        scored_moves = flatten(pool.starmap(cls.evaluate_moves, zip(solution_copies, chunks)))

    # Else just do it in this thread
    else:
      scored_moves = cls.evaluate_moves(solution, moves)

    logger.info("Explored %i neighbors", len(scored_moves))
    return scored_moves

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

  def is_boxcount_decreasing(self, solution: BoxSolution) -> bool:
    '''Checks whether this move would decrease the overall box count.'''
    # Get objects
    from_box = solution.boxes[self.from_box_id]
    to_box = solution.boxes[self.to_box_id]
    rect_copy = deepcopy(from_box.rects[self.rect_id])

    # Move rect to target location
    rect_copy.move_to(self.new_x, self.new_y)

    return all([
      # Must be last rect of the origin box
      len(from_box.rects) == 1,
      # Must be moved to a different box
      self.from_box_id != self.to_box_id,
      # Must have space in the target box
      rect_copy.get_all_coordinates() <= to_box.free_coords
    ])

  def apply_to_solution(self, solution: BoxSolution) -> bool:
    '''
    Tries to apply this move to a given box solution.
    Will return false if resulting solution is invalid.
    '''

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
    move_success = new_box.add_rect(current_rect)

    if not move_success:
      # Revert rect coordinates
      current_rect.move_to(self.old_x, self.old_y)
      if self.flip:
        current_rect.flip()
      # Add it back where it came from and return
      current_box.add_rect(current_rect)
      return False

    # Highlight it as changed
    current_rect.highlighted = True

    # If the current box is now empty, remove it from the solution
    if len(current_box.rects) == 0:
      solution.boxes.pop(self.from_box_id)

    return True

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
      # solution.boxes[self.from_box_id].needs_redraw = True
      solution.boxes[self.from_box_id].add_rect(rect)
