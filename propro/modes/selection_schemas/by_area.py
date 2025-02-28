import logging
from itertools import product
from typing import Optional

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from problem import BoxSolution
from geometry.box import compute_box_coordinates

from .selections import SelectionSchema

logger = logging.getLogger(__name__)

class ByAreaSelection(SelectionSchema):
  '''
  Simple concept: At every step, take the rectangle which has the minimal area.
  This will use up the big ones first and the smaller ones can fit into the gaps
   which are created in the process.
  '''

  # NOTE: Kind of redundant to permutation.reconstruct_boxes() but not quite??
  @staticmethod
  def find_rect_space(box_coordinates: np.ndarray, rect_w, rect_h) -> Optional[tuple[int, int]]:
    '''Checks if a given rect fits somewhere in a box and returns the origin coordinates if possible'''
    window = sliding_window_view(box_coordinates, (rect_w, rect_h))
    # Loop over all origins
    for (x, y) in product(range(window.shape[0]), range(window.shape[1])):
      # Check if this space is free
      if np.all(window[x, y, ...] == 0):
        # If it is, this fits the rect!
        return (x, y)

    # If loop never returned then nothing fits -> Return None
    return None

  @staticmethod
  def place_rect(partial_solution: BoxSolution, rect: np.ndarray) -> BoxSolution:
    '''
    Finds a place for a given rectangle in the partial solution.
    If no fit was found, a new box is created to accomodate it.
    '''
    for box in partial_solution.iter_boxes():
      # Turn box into array of coordinates with 0 free 1 occupied
      box_coordinates = compute_box_coordinates(box, partial_solution.side_length)
      _, _, w, h, _ = rect
      possible_fit = ByAreaSelection.find_rect_space(box_coordinates, w, h)
      if possible_fit is not None:
        # Place rect there
        rect[0:2] = possible_fit
        # Get box id from first rect of this box
        rect[4] = box[0][4]
        logger.debug("Placed rect at x=%i, y=%i, b=%i", *possible_fit, box[0][4])
        return partial_solution

    # If no box had room, set rect to 0, 0 of a new box
    rect[0:2] = 0
    # New box id will just be the current max of ids + 1
    rect[4] = np.max(partial_solution.rectangles[:, 4]) + 1
    logger.debug("Placed rect into new box b=%i", rect[4])
    return partial_solution

  @classmethod
  def select(cls, partial_solution: BoxSolution) -> BoxSolution:
    '''
     Will always choose the unplaced rectangle with the largest area
     and place it at the smallest possible coordinate.
    '''
    # Find indices of unplaced rects first
    unplaced_indices = np.where(partial_solution.rectangles[:, 4] == -1)[0]
    if len(unplaced_indices) == 0:
      return partial_solution  # Nothing to place

    # Calculate areas, find index with max area from these
    areas = [partial_solution.rectangles[i, 2] * partial_solution.rectangles[i, 3] for i in unplaced_indices]
    max_area_idx = unplaced_indices[np.argmax(areas)]

    # Get a reference to the rectangle
    rect = partial_solution.rectangles[max_area_idx]
    logger.debug("Trying to place rect %s", rect)

    # Find a placement
    return cls.place_rect(partial_solution, rect)
