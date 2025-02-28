import logging
from itertools import product

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from problem import BoxSolution
from .neighborhood import Neighborhood

logger = logging.getLogger(__name__)

class Permutation(Neighborhood):
  '''Implementation for a permutation-based neighborhood'''

  @staticmethod
  def reconstruct_boxes(box_length: int, rectangles: np.ndarray) -> np.ndarray:
    '''
    Goes over all rectangles in-order and fixes coordinates and box ids
    such that no two rectangles are overlapping
    '''
    # Keep a list of boxes with 0 and 1 values for each coordinate
    box_coordinates = [np.zeros((box_length, box_length))]

    # Go over all rects
    for rect in rectangles:
      # Try to fit it in each box
      for box_idx, box in enumerate(box_coordinates):
        _, _, w, h, _ = rect
        rect_placed = False
        # Construct sliding window
        window = sliding_window_view(box, (w, h))
        # Slide window over coordinates and check if we find a spot of all 0s
        for (x, y) in product(range(window.shape[0]), range(window.shape[1])):
          if np.all(window[x, y, ...] == 0):
            # Found it!
            rect_placed = True
            # Set rect values
            rect[0:2] = x, y
            rect[4] = box_idx
            # Add rect coordinates to the box
            box[x:x+w, y:y+h] = 1
            break
        if rect_placed:
          break
      # If none fit, put it in a new one
      else:
        # Set rect values
        rect[0:2] = 0
        rect[4] = len(box_coordinates)
        # Set box coordinates
        new_box = np.zeros((box_length, box_length))
        new_box[0:rect[2], 0:rect[3]] = 1
        box_coordinates.append(new_box)

    # Return modified rectangles
    return rectangles

  @classmethod
  def get_neighbors(cls, solution: BoxSolution) -> list[BoxSolution]:
    '''
    Ignores the box_id of a given solution and permutates the order of rectangles.
    Will then re-create boxes, placing them one by one.
    '''
    logger.info("Claculating Permutation neighborhood")

    neighbors = []

    # Do every possible pairwise swap
    for i in range(len(solution.rectangles) - 1):
      neighbor = np.copy(solution.rectangles)

      neighbor[[i, i + 1]] = neighbor[[i + 1, i]]
      neighbor_solution = BoxSolution(
        solution.side_length,
        Permutation.reconstruct_boxes(solution.side_length, neighbor)
      )
      if neighbor_solution.get_score().box_count is not None:
        neighbors.append(neighbor_solution)

    # Also flip every possible rect
    for i in range(len(solution.rectangles)):
      neighbor = np.copy(solution.rectangles)
      rect = neighbor[i]
      rect[[2, 3]] = rect[[3, 2]]
      neighbor_solution = BoxSolution(
        solution.side_length,
        Permutation.reconstruct_boxes(solution.side_length, neighbor)
      )
      if neighbor_solution.get_score().box_count is not None:
        neighbors.append(neighbor_solution)

    return neighbors
