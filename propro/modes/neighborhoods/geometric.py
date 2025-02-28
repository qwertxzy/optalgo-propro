import logging

import numpy as np

from problem import BoxSolution

from geometry.box import compute_box_adjacent_coordinates
from .neighborhood import Neighborhood

logger = logging.getLogger(__name__)

class Geometric(Neighborhood):
  '''Implementation for a geometry-based neighborhood'''

  # TODO: Add the option to move a rect into a new box? Might be needed for simulated annealing
  #   -> should be easy now, just add a new id to box_ids

  # There needs to be a bonus for moving rects from an almost empty box to a crowded one maybe?
  # IDEA: Rects could be fixed to cut down on neighborhood size. Maybe large ones? All rects of a box when there are 0 free coords

  @classmethod
  def get_neighbors(cls, solution: BoxSolution) -> BoxSolution:
    '''
    Calculates neighbors of a solution by geometric means
    Moves every rectangle in every box to every possible coordinate
    '''
    logger.info("Calculating Geometric neighborhoods")
    neighbors = []

    # Get all possible box ids
    box_ids = np.unique(solution.rectangles[:, 4])

    # Get all possible adjacent coordinates
    box_adjacent_coords = {}
    for box_id in box_ids:
      box = solution.rectangles[solution.rectangles[:, 4] == box_id]
      box_adjacent_coords[box_id] = compute_box_adjacent_coordinates(box, solution.side_length)

    # Sort rects by area descending
    rect_areas = solution.rectangles[:, 2] * solution.rectangles[:, 3]
    sorted_indices = np.argsort(-rect_areas)

    # Iterate over all rectangles
    for rect_idx in sorted_indices:
      (cx, cy, cw, ch, cb) = solution.rectangles[rect_idx]
      # Now iterate over all possible moves! A rect can be placed
      # .. in any box
      for box_id in box_ids:
        box = solution.rectangles[np.where(solution.rectangles[:, 4] == box_id)]
        # .. at any coordinate
        for (x, y) in box_adjacent_coords[box_id]:
          # .. at any rotation
          for is_flipped in [False, True]:

            # Nonsense movea
            if any([
              cx == x and cy == y and not is_flipped and cb == box_id,
              cx + cw > solution.side_length and not is_flipped,
              cy + ch > solution.side_length and not is_flipped
            ]):
              continue

            # Create copy of all rectangles
            neighbor = np.copy(solution.rectangles)

            # Modify rect at that index
            current_rect = neighbor[rect_idx]
            current_rect[0:2] = x, y
            if is_flipped:
              current_rect[[2, 3]] = current_rect[[3, 2]]
            current_rect[4] = box_id

            neighbor_solution = BoxSolution(solution.side_length, neighbor)
            neighbor_score = neighbor_solution.get_score()

            # Skip invalid
            if neighbor_score.box_count is None:
              continue

            # If box count is smaller than current, early return
            if neighbor_score.box_count < solution.get_score().box_count:
              neighbors.append(neighbor_solution)
              logger.info("Found box-decreasing move, returning early")
              return neighbors

            # Append to neighbors
            neighbors.append(neighbor_solution)
    logger.info("Found %i neighbors", len(neighbors))
    return neighbors
