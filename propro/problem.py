'''
Module contains an abstract problem definition as well as the
concrete implementation for the box-rectangle problem given.
'''

from __future__ import annotations
from abc import ABC, abstractmethod
from random import choice
from itertools import combinations

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
  def get_score(self) -> float:
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
    self.current_solution = BoxSolution(boxes)

class BoxSolution(Solution):
  '''
  Holds a current solution of the box-rect problem.
  Will get copied and constructed a lot, so should probably be as light-weight as possible.
  '''
  # Lookup box id -> box obj
  boxes: dict[Box]
  currently_permissible_overlap: float

  def __init__(self, box_list: list[Box]):
    '''
    Initialize the solution with a list of box objects
    '''
    self.currently_permissible_overlap = 0.0
    self.boxes = dict()
    for box in box_list:
      self.boxes[box.id] = box

  def __repr__(self):
    s = f"Score: {self.get_score()}\n"
    s += f"Allowed Overlap: {self.currently_permissible_overlap}\n"
    s += '\n'.join([str(box) for box in self.boxes.values()])
    return s

  def move_rect(self, rect_id: int, from_box_idx: int, new_x: int, new_y: int, new_box_idx: int, flip: bool):
    '''
    Moves a rectangle identified via its id from an old box to new coordinates in a new box
    '''
    # Get rect in old box
    current_box = self.boxes[from_box_idx]
    current_rect = current_box.rects[rect_id]

    # Update rect coordinates
    current_rect.x = new_x
    current_rect.y = new_y
    if flip:
      current_rect.width, current_rect.height = current_rect.height, current_rect.width

    # If the box stays the same we're done here
    if from_box_idx == new_box_idx:
      return

    # Otherwise, move the box from the old box's rect list to the new one
    current_rect = current_box.rects.pop(rect_id)
    new_box = self.boxes[new_box_idx]
    new_box.rects[rect_id] = current_rect

    # If the current box is now empty, remove it from the solution
    if len(current_box.rects) == 0:
      self.boxes.pop(from_box_idx)

  def get_score(self) -> tuple[int, int]:
    # If solution is invalid, score it 0
    if not self.is_valid():
      return 0

    # Count non-empty boxes and incident edges between rects as scoring criteria
    box_counts =  len(self.boxes)
    incident_edges = -self.compute_incident_edges() # Minus because we are trying to minimize
    return (box_counts, incident_edges)

  def compute_incident_edges(self) -> int:
    '''
    Computes the number of unit lengths of edges
    that overlap from adjacent rectangles
    '''
    edges = 0
    # Go over all boxes
    for box in self.boxes.values():
      # Go over all possible pairs of rects within this box
      for (rect_a, rect_b) in combinations(box.rects.values(), 2):
        # Call the one with smaller origin left, the other right rect
        left_rect, right_rect = sorted([rect_a, rect_b], key=lambda r: (r.x, r.y))

        # Check for incidence in x coordinate and add possible overlap
        if left_rect.x + left_rect.width == right_rect.x:
          overlap = min(left_rect.y + left_rect.height, right_rect.y + right_rect.height) - max(left_rect.y, right_rect.y)
          edges += max(overlap, 0)
        # Check for incidence in y coordinate and add possible overlap
        if left_rect.y + left_rect.height == right_rect.y:
          overlap = min(left_rect.x + left_rect.width, right_rect.x + right_rect.width) - max(left_rect.x, right_rect.x)
          edges += max(overlap, 0)

      # To weigh these more than the box edge, multiply current count by 2
      edges *= 2

      # Go over all rects (again?) to count edges on the box edge
      # ..any way to make this neater?
      for rect in box.rects.values():
        if rect.x == 0:
          edges += rect.height
        if rect.x + rect.width == box.side_length:
          edges += rect.height
        if rect.y == 0:
          edges += rect.width
        if rect.y + rect.height == box.side_length:
          edges += rect.width
    return edges


  def is_valid(self):
    # Go over all rects in all boxes
    for box in self.boxes.values():
      # Easy case: Rect is out-of-bounds
      for rect in box.rects.values():
        if rect.x + rect.width > box.side_length or rect.y + rect.height > box.side_length:
          return False

      # Harder case: Rect may overlap with any other in this box
      for rect_a, rect_b in combinations(box.rects.values(), 2):
        if rect_a.overlaps(rect_b, self.currently_permissible_overlap):
          return False
    return True

class Box:
  '''
  One box of the box-rect problem.
  '''
  # Lookup from rect id -> rect obj
  rects: dict[int, Rectangle]
  id: int
  side_length: int

  def __repr__(self):
    s = f"{self.id}: "
    s += ' '.join([str(r) for r in self.rects.values()])
    return s

  def __init__(self, b_id: int, side_length: int, *rects: Rectangle):
    '''
    Initializes a new box with a number of rects
    '''
    self.id = b_id
    self.side_length = side_length
    self.rects = dict()
    for rect in rects:
      self.rects[rect.id] = rect

  # memoize?
  # IDEA: A box could keep track of all the free spaces within it,
  #       so we can minimize the rects being placed invalidly
  def is_coord_free(self, x: int, y: int) -> bool:
    '''Checks whether a given coordinate is occupied by a rectangle'''
    for rect in self.rects.values():
      if rect.contains(x, y):
        return False
    return True

class Rectangle:
  '''
  One rectangle to be fitted into boxes in the box-rect problem.
  '''
  x: int
  y: int
  width: int
  height: int
  id: int

  def __repr__(self):
    return f"[{self.id}: ({self.x}+{self.width}/{self.y}+{self.height})]"

  def __eq__(self, value):
    '''Override equality with id check'''
    if not isinstance(value, Rectangle):
      return False
    return self.id == value.id

  def __init__(self, x: int, y: int, w: int, h: int, i: int):
    self.x = x
    self.y = y
    self.width = w
    self.height = h
    self.id = i

  def get_area(self) -> int:
    '''Compute area of the rectangle'''
    return self.width * self.height

  def contains(self, x: int, y:int) -> bool:
    '''Checks whether a given x/y coordinate lies within this rect'''
    return all([
      self.x <= x,
      self.x + self.width > x,
      self.y <= y,
      self.y + self.height > y
    ])

  def overlaps(self, other: Rectangle, permissible_overlap: float = 0.0) -> bool:
    '''Checks whether two rectangles overlap, with a permissible amount.'''
    # Check if these two are the same
    if self.id == other.id:
      return False

    # If permissible overlap is zero, do strict boundary checks only
    if permissible_overlap == 0.0:
      checks = [
        (self.x < other.x + other.width),
        (self.x + self.width > other.x),
        (self.y < other.y + other.height),
        (self.y + self.height > other.y)
      ]
      return all(checks)

    # If it's not, we need to compute the overlap area of the two rects
    # and compare it against the permissible value
    overlap_x1 = max(self.x, other.x)
    overlap_y1 = max(self.y, other.y)
    overlap_x2 = min(self.x + self.width, other.x + other.width)
    overlap_y2 = min(self.y + self.height, other.y + other.height)

    overlap_width = abs(overlap_x1 - overlap_x2)
    overlap_height = abs(overlap_y1 - overlap_y2)
    overlap_area = overlap_width * overlap_height
    return (overlap_area / (self.get_area() + other.get_area())) > permissible_overlap
