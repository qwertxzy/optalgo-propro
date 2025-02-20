'''
Module contains an abstract problem definition as well as the
concrete implementation for the box-rectangle problem given.
'''

from __future__ import annotations
from abc import ABC, abstractmethod
from random import choice
from itertools import combinations
from dataclasses import dataclass

from geometry import Rectangle, Box

@dataclass
class Score:
  '''
  Represents the score of a solution.
  `None` as a box count will indicate an invalid solution.
  '''
  box_count: int
  incident_edges: int

  def __iter__(self):
    return iter((self.box_count, self.incident_edges))

  def __repr__(self):
    return f"Score({self.box_count=}, {self.incident_edges=})"

  def __lt__(self, other: Score):
    match (self.box_count, other.box_count):
      # Both solutions are invalid, don't care about ordering
      case (None, None): return True
      # Self is valid, other is invalid
      case (_, None): return True
      # Self is invalid, other is valid
      case (None, _): return False
      # Both are valid, self has less boxes than other
      case (sc, oc) if sc < oc: return True
      # Both are valid, self has more boxes than other
      case (sc, oc) if sc > oc: return False
      # Both are valid, both have the same boxes
      case (sc, oc) if sc == oc: return self.incident_edges > other.incident_edges

  def __eq__(self, other: Score):
    return self.box_count == other.box_count and self.incident_edges == other.incident_edges

  def __le__(self, other: Score):
    return self < other or self == other

class Problem(ABC):
  '''
  Abstract base class for a generic optimization problem.
  '''
  current_solution: Solution

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
  def __init__(self, box_length: int, n_rect: int, w_range: range, h_range: range):
    '''
    Initializes the box problem with a trivial solution where each rectangle is in its own box.
    '''
    boxes = []
    for n in range(n_rect):
      # Get ourselves a nice rect tangle
      width = choice(w_range)
      height = choice(h_range)
      rect = Rectangle(0, 0, width, height, n)

      # Now construct a new box and put just this one in it
      boxes.append(Box(n, box_length, rect))

    # Finally, initialize the solution with list of boxes
    self.current_solution = BoxSolution(box_length, boxes)

class BoxSolution(Solution):
  '''
  Holds a current solution of the box-rect problem.
  Will get copied and constructed a lot, so should probably be as light-weight as possible.
  '''
  # Lookup box id -> box obj
  boxes: dict[int, Box]
  side_length: int
  currently_permissible_overlap: float

  def __init__(self, side_length: int, box_list: list[Box]):
    '''
    Initialize the solution with a list of box objects
    '''
    self.currently_permissible_overlap = 0.0
    self.side_length = side_length
    self.boxes = dict()
    for box in box_list:
      self.boxes[box.id] = box

  def __repr__(self):
    s = f"Score: {self.get_score()}\n"
    s += f"Allowed Overlap: {self.currently_permissible_overlap}\n"
    s += '\n'.join([str(box) for box in self.boxes.values()])
    return s

  # TODO: Covered by get_score() now
  # def is_valid_move(self, move) -> bool:
  #   '''
  #   Checks whether a move of a rectangle to a new box and coordinates is valid
  #   '''
  #   # Get old box, new box and rect
  #   from_box = self.boxes[move.from_box_id]
  #   to_box = self.boxes[move.to_box_id]
  #   rect = from_box.rects[move.rect_id].copy()

  #   if move.flip:
  #     rect.flip()
  #   rect.move_to(move.new_x, move.new_y)

  #   # Check if the rect would overflow to the right/bottom
  #   if move.new_x + rect.width > self.side_length:
  #     return False
  #   if move.new_y + rect.height > self.side_length:
  #     return False

  #   # Check if the rect would overlap with any other rect in the new box
  #   for other_rect in to_box.rects.values():
  #     if rect.overlaps(other_rect, self.currently_permissible_overlap):
  #       return False
  #   return True

  def get_potential_score(self, move) -> Score:
    '''
    Calculates the potential score of the solution after a given move.
    Assumes validity of the move.
    '''
    # Perform move
    move.apply_to_solution(self)

    # If move is valid, construct a proper score,
    # if not, use None to signal invalidity
    if self.is_valid():
      score = Score(len(self.boxes), self.compute_incident_edge_coordinates())
    else:
      score = Score(None, None)

    # Undo the move operation
    move.undo(self)

    return score

  def compute_incident_edge_coordinates(self) -> int:
    '''number of coordinates that at least 2 rectangles share.'''
    edges = 0
    for box in self.boxes.values():
      edges += box.get_incident_edge_count()
    return edges

  def get_score(self) -> Score:
    # Very large number
    if not self.is_valid():
      return Score(None, None)

    # Count non-empty boxes and incident edges between rects as scoring criteria
    box_counts = len(self.boxes)
    incident_edges = self.compute_incident_edge_coordinates()
    return Score(box_counts, incident_edges)

  def is_valid(self):
    # Go over all rects in all boxes
    for box in self.boxes.values():
      # Easy case: Rect is out-of-bounds
      for rect in box.rects.values():
        if rect.get_x() + rect.width > self.side_length or rect.get_y() + rect.height > self.side_length:
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
