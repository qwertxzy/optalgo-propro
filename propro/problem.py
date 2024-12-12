'''
Module contains an abstract problem definition as well as the
concrete implementation for the box-rectangle problem given.
'''

from __future__ import annotations
from abc import ABC, abstractmethod
from random import choice
from itertools import product

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
  boxes: list[Box]
  score: float

  def __init__(self, box_list: list[Box]):
    '''
    Initialize the solution with a list of box objects
    '''
    self.boxes = box_list
    self.score = self.get_score()

  def __repr__(self):
    s = f"Score: {self.score}\n"
    s += '\n'.join([str(box) for box in self.boxes])
    return s

  def move_rect(self, rect_id: int, from_box_idx: int, new_x: int, new_y: int, new_box_idx: int, flip: bool):
    '''
    Moves a rectangle identified via its id from an old box to new coordinates in a new box
    '''
    # Get rect in old box
    current_box = self.boxes[from_box_idx]
    current_rect = next(filter(lambda r: r.id == rect_id, current_box.rects))

    # Update rect coordinates
    current_rect.x = new_x
    current_rect.y = new_y
    if flip:
      current_rect.width, current_rect.height = current_rect.height, current_rect.width

    # If the box stays the same we're done here
    if from_box_idx == new_box_idx:
      return

    # Otherwise, move the box from the old box's rect list to the new one
    current_box.rects.remove(current_rect)
    new_box = self.boxes[new_box_idx]
    new_box.rects.append(current_rect)

  # TODO: include some sort of factor for how tightly packed a box is?
  # TODO: refactor into own file to implement multiple options
  def get_score(self) -> float:
    # If solution is invalid, score it 0
    if not self.is_valid():
      return 0
    # Otherwise, count boxes with more than 0 rects in them
    return len(list(filter(lambda b: len(b.rects) > 0, self.boxes)))

  def is_valid(self):
    # Go over all rects in all boxes
    for box in self.boxes:
      # Easy case: Rect is out-of-bounds
      for rect in box.rects:
        if rect.x + rect.width > box.side_length or rect.y + rect.height > box.side_length:
          return False

      # Harder case: Rect may overlap with any other in this box
      for rect_a, rect_b in product(box.rects, box.rects):
        if rect_a.overlaps(rect_b):
          return False
    return True

class Box:
  '''
  One box of the box-rect problem.
  '''
  # TODO: a dict with rect id -> rect would probably be more performant here?
  rects: list[Rectangle]
  id: int
  side_length: int

  def __repr__(self):
    s = f"{self.id}: "
    s += ' '.join([str(r) for r in self.rects])
    return s

  def __init__(self, b_id: int, side_length: int, *rects: Rectangle):
    '''
    Initializes a new box with a number of rects
    '''
    self.id = b_id
    self.side_length = side_length
    self.rects = list(rects)

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
  