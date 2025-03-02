from __future__ import annotations
import logging
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
from copy import deepcopy
import os

import numpy as np

from problem import BoxSolution
from geometry import Box
from utils import flatten


from .neighborhood import Neighborhood
from ..move import Move, ScoredMove

logger = logging.getLogger(__name__)

class Geometric(Neighborhood):
  '''Implementation for a geometry-based neighborhood'''

  n_proc = max(int(os.environ.get("OPTALGO_MAX_CPU", 0)), cpu_count())
  '''Number of processes the neighborhood searching should use'''

  # TODO: Add the option to move a rect into a new box? Might be needed for simulated annealing

  @classmethod
  def generate_moves_for_rects(cls, solution: BoxSolution, ids: list[tuple[int, int]]) -> list[ScoredMove]:
    '''
    Generates a list of scoreed moves for the given rects in `solution`.
    IDs must be given as a list `(bod_id, rect_id)`.
    '''
    current_score = solution.get_score()
    moves = []

    for (box_id, rect_id) in ids:
      current_box = solution.boxes[box_id]
      current_rect = current_box.rects[rect_id]

      # Iterate over every target box
      for possible_box in solution.boxes.values():
        # ... in any free coordinate within this box
        for (x, y) in list(possible_box.get_adjacent_coordinates()):
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
            score = solution.get_potential_score(move)

            # Skip invalid moves
            if score.box_count is None:
              continue

            moves.append(ScoredMove(move, score))

            # # If we have more than 5 rects to process, we are fine with finding a box-decreasing move
            if current_score.box_count > score.box_count:
              return moves
    return moves

  @classmethod
  def get_neighbors(cls, solution: BoxSolution) -> list[ScoredMove]:
    '''
    Calculates neighbors of a solution by geometric means
    Moves every rectangle in every box to every possible coordinate
    '''
    logger.info("Calculating Geometric neighborhoods")

    # Create list of tuples (box_id, rect_id)
    rects = []

    # Prio rect gets defined if there is a box with only one rect, if so try to place that
    prio_rect = None

    for box_id, box in solution.boxes.items():
      if prio_rect is not None:
        break
      # If we have a box with only one rect, go into quick mode
      for rect_id in box.rects.keys():
        if len(box.rects) == 1:
          prio_rect = (box_id, rect_id)
          break
        if rect_id not in solution.last_moved_rect_ids:
          rects.append((box_id, rect_id))

    # If we have a prio rect, generate moves only for this in hopes of
    # putting it into another box
    scored_moves = []
    if prio_rect is not None:
      scored_moves = cls.generate_moves_for_rects(solution, [prio_rect])

    # If scored moves are empty either because there was no prio rect or because
    # the method didn't return any valid neighbors, do the expensive shaboingboing
    if len(scored_moves) == 0:
      # Copy the current solution so every thread can modify it independently
      solution_copies = [deepcopy(solution) for _ in range(cls.n_proc)]

      # Split moves into chunks for pool to process
      chunks = np.array_split(rects, cls.n_proc)

      logger.info("Split move generation into chunks of sizes %s", [len(c) for c in chunks])

      # Evaluate all rects to scored moves concurrently
      with Pool(processes=cls.n_proc) as pool:
        scored_moves = flatten(pool.starmap(cls.generate_moves_for_rects, zip(solution_copies, chunks)))

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

    # Add rect id to problem's last moved queue
    solution.last_moved_rect_ids.append(current_rect.id)

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

    # Remove it from last moved rect ids again
    solution.last_moved_rect_ids.pop()
    rect.highlighted = False

    # Maybe the old box was deleted by the move? Otherwise just add it back
    if self.from_box_id not in solution.boxes.keys():
      solution.boxes[self.from_box_id] = Box(self.from_box_id, solution.side_length, rect)
    else:
      # solution.boxes[self.from_box_id].needs_redraw = True
      solution.boxes[self.from_box_id].add_rect(rect)
