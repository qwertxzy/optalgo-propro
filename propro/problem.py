'''
Module contains an abstract problem definition as well as the
concrete implementation for the box-rectangle problem given.
'''

from __future__ import annotations
from abc import ABC, abstractmethod
from random import choice
from dataclasses import dataclass

import numpy as np
import numba

from geometry.box import compute_box_incident_edges
from geometry.rectangle import check_rect_overlap

@numba.njit
def calc_entropy_fast(box_counts):
  """Numba time"""
  total_rects = sum(box_counts)
  if total_rects == 0:
    return 0.0

  probabilities = [count / total_rects for count in box_counts]
  entropy = 0.0
  for p in probabilities:
    if p > 0:
      entropy -= p * np.log2(p)

  return entropy

@dataclass
class Score:
  '''
  Represents the score of a solution.
  `None` as a box count will indicate an invalid solution.
  '''
  box_count: int
  '''Number of overall boxes in this solution. Lower is better.'''
  # Was planned as 'gain' but that can only work on a move, not on a solution
  box_entropy: int
  '''Measure of how distributed rects are among boxes. Lower is better.'''
  incident_edges: int
  '''Number of coordinates shared by two adjacent rects. Higher is better.'''

  def __iter__(self):
    return iter((self.box_count, self.box_entropy, self.incident_edges))

  def __repr__(self):
    return f"Score({self.box_count=}, {self.box_entropy=}, {self.incident_edges=})"

  def __lt__(self, other: Score):
    # Handle invalid solutions first
    if self.box_count is None and other.box_count is None:
      return True
    if other.box_count is None:
      return True
    if self.box_count is None:
      return False

    # Compare in order of priority
    if self.box_count != other.box_count:
      return self.box_count < other.box_count
    if self.box_entropy != other.box_entropy:
      return self.box_entropy < other.box_entropy
    return self.incident_edges > other.incident_edges

  def __eq__(self, other: Score):
    return all([
      self.box_count == other.box_count,
      self.box_entropy == other.box_entropy,
      self.incident_edges == other.incident_edges
    ])

  def __le__(self, other: Score):
    return self < other or self == other

class Problem(ABC):
  '''
  Abstract base class for a generic optimization problem.
  '''
  current_solution: Solution

  @abstractmethod
  def prepare_greedy(self):
    '''Prepares this solution for a greedy algorithm'''

  @abstractmethod
  def greedy_done(self) -> bool:
    '''Returns true once the greedy algorithm is done'''

class Solution(ABC):
  '''
  Abstract base class for a generic optimization solution.
  '''
  @abstractmethod
  def get_score(self) -> Score:
    '''
    Computes and returns the score of this solution.
    '''
  @abstractmethod
  def is_valid(self) -> bool:
    '''
    Checks whether this solution is valid in the first place.
    '''

class BoxProblem(Problem):
  '''
  Implementation for the box-rectangle problem.
  Contains the initial starting parameters and a current solution
  '''

  current_solution: BoxSolution
  score: Score

  def __init__(self, box_length: int, n_rect: int, w_range: range, h_range: range):
    '''
    Initializes the box problem with a trivial solution where each rectangle is in its own box.
    '''
    rectangles = np.ndarray((n_rect, 5), dtype=np.int16)
    for n in range(n_rect):
      # Get ourselves a nice rect tangle
      width = choice(w_range)
      height = choice(h_range)
      # TODO: named type?
      rect = [0, 0, width, height, n]
      rectangles[n] = rect

    # Finally, initialize the solution with list of boxes
    self.current_solution = BoxSolution(box_length, rectangles)

  def prepare_greedy(self):
    '''Unplaces all rects in the solution'''
    self.current_solution.rectangles[:, 4] = -1

  def greedy_done(self):
    return np.all(self.current_solution.rectangles[:, 4] != -1)

class BoxSolution(Solution):
  '''
  Holds a current solution of the box-rect problem.
  Will get copied and constructed a lot, so should probably be as light-weight as possible.
  '''
  rectangles: np.ndarray
  '''Array of rectangles of form `[x, y, w, h, b]` with `b` being the box number. (b=-1 for unplaced)'''
  side_length: int
  '''Side length of a box'''
  currently_permissible_overlap: float
  '''Value for the allowed overlap between rects that the solution may have'''

  __score: Score
  '''Score of this solution. Calculated on construction or when explicitly recalculated.'''

  def __init__(self, side_length: int, rectangles: np.ndarray):
    '''
    Initialize the solution with a list of box objects
    '''
    self.currently_permissible_overlap = 0.0
    self.side_length = side_length
    self.rectangles = rectangles
    self.__calc_score()

  def __repr__(self):
    s = f"Score: {self.get_score()}\n"
    s += f"Allowed Overlap: {self.currently_permissible_overlap}\n"
    s += '\n'.join(str(l) for l in self.iter_boxes())
    return s

  def iter_boxes(self):
    '''Iterator over all boxes and yields a list of rectangles'''
     # Iterate over all boxes
    box_ids = np.unique(self.rectangles[:, 4])
    for box_id in box_ids:
      # Skip the 'unplaced' box
      if box_id == -1:
        continue
      yield self.rectangles[np.where(self.rectangles[:, 4] == box_id)]

  def compute_incident_edges(self) -> int:
    '''
    Computes the number of coordinates shared by at least 2 rectangles or a rectangle and the box border.
    '''
    edges = 0
    for box in self.iter_boxes():
      edges += compute_box_incident_edges(box, self.side_length)

    return edges

  def compute_box_entropy(self) -> float:
    '''Computes entropy over the number of rects per box'''
    unique, counts = np.unique(self.rectangles[:, 4], return_counts=True)
    # Remove unplaced rectangles
    placed_mask = unique != -1
    counts = counts[placed_mask]

    return calc_entropy_fast(counts)

  def get_score(self) -> Score:
    '''Returns the score of this solution'''
    return self.__score

  def __calc_score(self):
    '''Calculates the score for this solution'''
    if not self.is_valid():
      self.__score = Score(None, None, None)
      return

    # Calculate all aspects of a score
    box_counts = len([i for i in np.unique(self.rectangles[:, 4]) if i != -1])
    box_entropy = self.compute_box_entropy()
    incident_edges = self.compute_incident_edges()
    self.__score = Score(box_counts, box_entropy, incident_edges)
    return

  def is_valid(self):
    # Check for overflows
    if self.check_overflow():
      return False

    # Check for overlaps
    if self.check_overlap():
      return False

    return True

  def check_overflow(self) -> bool:
    '''
    Checks boxes of this oslution for rects that overflow.
    Returns true if at least one overflow occurs.
    '''
    placed_mask = self.rectangles[:, 4] != -1
    rects = self.rectangles[placed_mask]
    return np.any((rects[:, 0] + rects[:, 2] > self.side_length) |
                  (rects[:, 1] + rects[:, 3] > self.side_length))

  def check_overlap(self) -> bool:
    '''Checks for overlapping rectangles in the current solution.'''
    for box in self.iter_boxes():
      if len(box) == 1:
        continue

      for i in range(len(box)):
        for j in range(i+1, len(box)):
          if check_rect_overlap(box[i], box[j], self.currently_permissible_overlap):
            return True
    return False
