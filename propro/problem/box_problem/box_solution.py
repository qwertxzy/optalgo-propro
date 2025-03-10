

from __future__ import annotations
from itertools import combinations
from math import log2
from collections import deque


from ..solution import Solution
from .geometry import Box, Rectangle
from ..heuristic import AbstractHeuristic
from .box_heuristic import GenericHeuristic


class BoxSolution(Solution):
  '''
  Holds a current solution of the box-rect problem.
  Will get copied and constructed a lot, so should probably be as light-weight as possible.
  '''
  boxes: dict[int, Box]
  '''Lookup from box id to object'''
  side_length: int
  '''Side length of all boxes'''
  currently_permissible_overlap: float
  '''Fraction of overlap that is allowed between two rectangles'''

  last_moved_rect_ids: deque[int]
  '''Queue of last moved rect ids'''

  def __init__(self, side_length: int, box_list: list[Box]):
    '''
    Initialize the solution with a list of box objects
    '''
    self.currently_permissible_overlap = 0.0
    self.side_length = side_length
    self.boxes = {}
    # Initialize queue with max length = rect count / 4
    self.last_moved_rect_ids = deque(maxlen=int(sum(len(b.rects) for b in box_list) / 4))
    for box in box_list:
      self.boxes[box.id] = box

  def __repr__(self):
    s = f"Heuristic Score: {self.get_heuristic_score()}\n"
    s += f"Allowed Overlap: {self.currently_permissible_overlap}\n"
    s += '\n'.join([str(box) for box in self.boxes.values()])
    return s

  def calculate_heuristic_score(self, move) -> AbstractHeuristic:
    '''
    Calculates the heuristic score of the solution after a given move.
    '''
    # Perform move
    move_sucessful = move.apply_to_solution(self)

    # If move was unsuccessful, it resulted in an invalid solution
    if not move_sucessful:
      return GenericHeuristic(None, None, None)

    # If move is valid, construct a proper score,
    score = GenericHeuristic(len(self.boxes), self.compute_box_entropy(), self.compute_incident_edge_coordinates())

    # Undo the move operation
    move.undo(self)
    return score

  def compute_incident_edge_coordinates(self) -> int:
    '''number of coordinates that at least 2 rectangles share.'''
    edges = 0
    for box in self.boxes.values():
      edges += box.get_incident_edge_count()
    return edges

  def compute_box_entropy(self) -> float:
    '''Computes the entropy of all boxes with regard to their rect count'''
    rect_counts = [len(b.rects) for b in self.boxes.values()]
    total_rects = sum(rect_counts)
    if total_rects == 0:
      return 0.0
    probabilities = [count / total_rects for count in rect_counts]
    entropy = -sum(p * log2(p) if p > 0 else 0.0 for p in probabilities)
    return entropy

  def count_illegal_overlaps(self) -> int:
    '''Counts the number of rectangles that overlap illegally.'''
    n = 0
    for box in self.boxes.values():
      for rect_a, rect_b in combinations(box.rects.values(), 2):
        if rect_a.overlaps(rect_b, self.currently_permissible_overlap):
          n += 2
    return n

  # TODO: don't re-calculate this every time
  def get_heuristic_score(self) -> GenericHeuristic:
    if not self.is_valid():
      return GenericHeuristic(None, None, None)

    # Calculate all aspects of a score
    box_counts = len(self.boxes)
    box_entropy = self.compute_box_entropy()
    incident_edges = self.compute_incident_edge_coordinates()
    return GenericHeuristic(box_counts, box_entropy, incident_edges)

  def is_valid(self):
    # Go over all rects in all boxes
    for box in self.boxes.values():
      # Easy case: Rect is out-of-bounds
      for rect in box.rects.values():
        if rect.get_x() + rect.get_width() > self.side_length or rect.get_y() + rect.get_height() > self.side_length:
          return False

      # Harder case: Rect may overlap with any other in this box
      for rect_a, rect_b in combinations(box.rects.values(), 2):
        if rect_a.overlaps(rect_b, self.currently_permissible_overlap):
          return False
    return True

  def to_greedy_queue(self) -> list[Rectangle]:
    '''
    Empties all the rectangles from the solution
    and returns them in a list for a greedy algorithm to solve
    '''
    rects = []
    for box in self.boxes.values():
      for rect_id in list(box.rects.keys()):
        rects.append(box.remove_rect(rect_id))
    # Remove now empty boxes from solution
    self.boxes.clear()
    return rects
  
  def insert_new_box_at(self, box: Box, box_id: int):
    '''
    Inserts a new box at the given box_id.
    pushes all other boxes with id >= box_id back by one.
    '''
    # Shift all boxes with id >= box_id back by one
    for i in range(len(self.boxes), box_id, -1):
      self.boxes[i] = self.boxes[i - 1]
      self.boxes[i].set_box_id(i)
    self.boxes[box_id] = box
    box.set_box_id(box_id)
