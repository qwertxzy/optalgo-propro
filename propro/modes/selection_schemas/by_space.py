from collections import defaultdict
from collections.abc import Iterator
from operator import itemgetter

import numpy as np

from geometry.box import compute_box_coordinates
from problem import BoxSolution

from .selections import SelectionSchema

class BySpaceSelection(SelectionSchema):
  '''
  Selection schema will:
   - look for the minimal coordinate where a rect could be placed next
   - expand into the x direction as much as possible
   - expand into the y direction as much as possible
   - find rect from list which is closest to these dimensions
   - if none does, try with the next smallest coordinate
   - if all fail, return the largest rect in a new box
  '''

  @staticmethod
  def find_minimal_coordinates(box_coordinates: np.ndarray) -> Iterator[tuple[int, int]]:
    '''
    Generates coordinates in a box to search from by grouping all free coordinates
    by x values and yielding the one with minimal y value of each group.
    '''
    # Iterate over coordinates per x
    for x in range(box_coordinates.shape[0]):
      row = box_coordinates[x, :]
      # If row is occupied, skip it
      if np.all(row == 1):
        continue
      free_y_idxs = np.where(row == 0)[0]
      if len(free_y_idxs) > 0:
        yield (x, free_y_idxs[0])

  @staticmethod
  def expand_coordinate(origin: tuple[int, int], box_coordinates: np.ndarray) -> tuple[int, int]:
    '''Will try to expand the given origin in x direction first and then y direction'''
    if box_coordinates[origin] == 1:
      raise ValueError("Cannot expand a rectangle from a non-free origin")

    x, y = origin
    max_x, max_y = box_coordinates.shape

    # Expand in x direction by finding first 1 in row
    row = box_coordinates[x:, y]
    if np.all(row == 0):
      # Entire row is free
      right_x = max_x
    else:
      right_x = x + np.argmax(row != 0)

    # Expand in y direction by checking each slice for 1s
    for bottom_y in range(y + 1, max_y + 1):
      if bottom_y == max_y:
        break

      if np.any(box_coordinates[x:right_x, bottom_y] != 0):
        break

    # Return resulting x/y
    return (right_x, bottom_y)

  @classmethod
  def select(cls, partial_solution: BoxSolution) -> BoxSolution:
    '''
     Will look for the first space in the solution that fits one of the provided rectangles.
     If none do, creates a new box.
    '''
    unprocessed_indices = np.where(partial_solution.rectangles[:, 4] == -1)[0]

    # Step 1: Go over all minimal coordinates
    for box_rects in partial_solution.iter_boxes():
      # Turn box into box of coordinates
      box_coordinates = compute_box_coordinates(box_rects, partial_solution.side_length)

      for coordinate in cls.find_minimal_coordinates(box_coordinates):
        # Step 2: Expand coordinate in x/y directions to find a theoretically ideal rectangle
        bottom_right_coordinate = cls.expand_coordinate(coordinate, box_coordinates)
        width = bottom_right_coordinate[0] - coordinate[0]
        height = bottom_right_coordinate[1] - coordinate[1]

        # Step 3: Filter rects to those which fit between these points
        possible_indices = [
          i for i in unprocessed_indices
          if partial_solution.rectangles[i, 2] <= width and
              partial_solution.rectangles[i, 3] <= height
        ]

        # If no rects are possible here, continue with next coordinate
        if len(possible_indices) == 0:
          continue

        # Pick the one based on the minimal difference between width and height to the target
        best_idx = min(
          possible_indices,
          key=lambda i: (
            width - partial_solution.rectangles[i, 2],
            height - partial_solution.rectangles[i, 3]
          )
        )

        # Get a reference to the rectangle
        rect = partial_solution.rectangles[best_idx]

        # Set coordinate
        rect[0:2] = coordinate
        # Steal box id from first other rect of this box
        rect[4] = box_rects[0][4]
        return partial_solution
    # If we get to here, no coordinate in any box returned a possible rect, so a new box must be created

    # Select the largest rect by area
    areas = [partial_solution.rectangles[i, 2] * partial_solution.rectangles[i, 3] for i in unprocessed_indices]
    largest_idx = unprocessed_indices[np.argmax(areas)]
    rect = partial_solution.rectangles[largest_idx]

    rect[0:2] = 0
    # New box id will just be the current max of ids + 1
    rect[4] = np.max(partial_solution.rectangles[:, 4]) + 1
    return partial_solution
