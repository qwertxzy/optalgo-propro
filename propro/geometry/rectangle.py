'''
Contbins several helper methods for computing rectangle-related values
'''

import numpy as np
import numba

@numba.njit
def get_edge_coordinates(rect: np.ndarray) -> np.ndarray:
  '''Get edges of this rect'''
  x, y, w, h, _ = rect
  edges = []

  # Horizontal edges
  for i in range(w):
    edges.append((x + i, y))      # Top edge
    edges.append((x + i, y + h))  # Bottom edge

  # Vertical edges
  for i in range(h):
    edges.append((x, y + i))      # Left edge
    edges.append((x + w, y + i))  # Right edge

  return edges

def check_contains(rect: np.ndarray, x, y) -> bool:
  '''Checks if a given x/y coordinate is inside this rectangle'''
  return all([
    # Check x coordinate
    x >= rect[0],
    x < rect[0] + rect[2],
    # Check y coordinate
    y >= rect[1],
    y < rect[1] + rect[3]
  ])

def get_corners(rect: np.ndarray) -> set[tuple[int, int]]:
  '''Returns coordinates of all four corners of this rectangle.'''
  x, y, w, h, _ = rect
  return set([
      (x, y),
      (x, y + h),
      (x + w, y),
      (x + w, y + h)
  ])

@numba.njit
def check_rect_overlap(rect_a, rect_b, overlap_threshold) -> bool:
  '''Checks for overlap between two rectangles given a permitted threshold'''
  x1, y1, w1, h1, _ = rect_a
  x2, y2, w2, h2, _ = rect_b

  # If overlap_threshold is 0, use strict boundary check
  if overlap_threshold == 0:
    # Check if rectangles overlap at all
    if (x1 < x2 + w2 and x1 + w1 > x2 and
      y1 < y2 + h2 and y1 + h1 > y2):
      return True
  else:
    # Calculate the intersection area
    x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
    y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
    intersection_area = x_overlap * y_overlap

    # Calculate areas of both rectangles
    area1 = w1 * h1
    area2 = w2 * h2

    # Calculate the overlap ratio
    sum_areas = area1 + area2
    overlap = intersection_area / sum_areas

    if overlap > overlap_threshold:
      return True

  return False
