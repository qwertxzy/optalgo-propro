import logging

import numpy as np
import numba

from .rectangle import get_edge_coordinates

logger = logging.getLogger(__name__)

@numba.njit
def compute_box_incident_edges(box: np.ndarray, side_length: int) -> int:
  '''
  Computes the number of adjacent edge coordinates of the rectangles in this box.
  A box in this case is just a list of rectangles with the same value at index 4.
  '''
  edge_counts = {}
  border_count = 0

  for rect in box:
    x, y, w, h, _ = rect

    # Count box border incidents
    if x == 0 or x + w == side_length:
      border_count += h
    if y == 0 or y + h == side_length:
      border_count += w

    # Add edges to counter
    edges = get_edge_coordinates(rect)
    for edge in edges:
      if edge in edge_counts:
        edge_counts[edge] += 1
      else:
        edge_counts[edge] = 1

    # Count edges with more than 1 rect
    duplicate_count = 0
    for count in edge_counts.values():
      if count > 1:
        duplicate_count += 1

  return border_count + duplicate_count

def compute_box_adjacent_coordinates(box: np.ndarray, side_length: int) -> set[tuple[int, int]]:
  '''
  Computes coordinates adjacent to the rectangles in this box
  '''
  # Init box coordinates as empty array
  box_coordinates = np.zeros((side_length + 10, side_length + 10), dtype=bool)

  # Add top & left edge of box
  box_coordinates[0:side_length, 0] = True
  box_coordinates[0, 0:side_length] = True

  # Loop over all rects and mark edges
  for rect in box:
    x, y, w , h, _ = rect

    # Toggle horizontal edges
    box_coordinates[x:x+w, y] ^= True
    box_coordinates[x:x+w, y+h] ^= True
    # Toggle vertical edges
    box_coordinates[x, y:y+h] ^= True
    box_coordinates[x+w, y:y+h] ^= True

  # Loop over rects *again* for corners
  for rect in box:
    x, y, w , h, _ = rect
    # Always mark rect corners
    box_coordinates[x, y] = True
    box_coordinates[x+w, y] = True
    box_coordinates[x+w, y+h] = True
    box_coordinates[x, y+h] = True

  # Return bools into set of tuples
  return { tuple(coord) for coord in np.argwhere(box_coordinates) }

@numba.jit
def compute_box_coordinates(rectangles: np.ndarray, side_length: int) -> np.ndarray:
  '''
  Will take the given rectangles and return an array of shape side_length x side_length
  with `1` where a rect is placed and `0` where there is free space
  '''
  box_coordinates = np.zeros((side_length, side_length))

  for rect in rectangles:
    x, y, w, h, _ = rect
    box_coordinates[x:x+w, y:y+h] = 1
  return box_coordinates
