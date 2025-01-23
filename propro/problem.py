'''
Module contains an abstract problem definition as well as the
concrete implementation for the box-rectangle problem given.
'''

from __future__ import annotations
from abc import ABC, abstractmethod
import sys
from random import choice
from itertools import combinations

from geometry.rectangle import Rectangle
from geometry.box import Box


class Score:
  '''
  Represents the score of a solution.
  '''
  def __init__(self, box_count: int, incident_edges: int):
    self.box_count = box_count
    self.incident_edges = incident_edges

  def __iter__(self):
    return iter((self.box_count, self.incident_edges))

  def __repr__(self):
    return f"Score(box_count={self.box_count}, incident_edges={self.incident_edges})"

  def __lt__(self, other: Score):
    #TODO: tweak this to make it more efficient
    return self.box_count < other.box_count or self.incident_edges > other.incident_edges

  def __eq__(self, other: Score):
    return self.box_count == other.box_count and self.incident_edges == other.incident_edges

  def __le__(self, other: Score):
    return self < other or self == other

class Move:
  '''
  Represents a move of a rectangle from one box to another.
  '''
  def __init__(self, rect_id: int, from_box_id: int, to_box_id: int, new_x: int, new_y: int, flip: bool):
    self.rect_id = rect_id
    self.from_box_id = from_box_id
    self.to_box_id = to_box_id
    self.new_x = new_x
    self.new_y = new_y
    self.flip = flip

  def __iter__(self):
    return iter((self.rect_id, self.from_box_id, self.to_box_id, self.new_x, self.new_y, self.flip))

  def __repr__(self):
    return f"Move(rect_id={self.rect_id}, from_box_id={self.from_box_id}, to_box_id={self.to_box_id}, new_x={self.new_x}, new_y={self.new_y}, flip={self.flip})"

class ScoredMove:
  '''
  Represents a move with its potential score.
  '''
  def __init__(self, move: Move, score: Score):
    self.move = move
    self.score = score

  def __iter__(self):
    return iter((self.move, self.score))

  def __repr__(self):
    return f"ScoredMove(move={self.move}, score={self.score})"

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

  @abstractmethod
  def apply_move(self, move: Move):
    '''
    Applies a move to the current solution.
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

  def apply_move(self, move: Move):
    '''
    Applies a move to the current solution
    '''
    print(f"Applying move: {move}")
    self.move_rect(move)

  def move_rect(self, move: Move):
    '''
    Moves a rectangle identified via its id from an old box to new coordinates in a new box
    '''
    # Get rect in old box
    current_box = self.boxes[move.from_box_id]
    current_rect = current_box.remove_rect(move.rect_id)

    # Update rect coordinates
    current_rect.x = move.new_x
    current_rect.y = move.new_y
    if move.flip:
      current_rect.flip()

    new_box = self.boxes[move.to_box_id]
    new_box.add_rect(current_rect)

    # If the current box is now empty, remove it from the solution
    if len(current_box.rects) == 0:
      self.boxes.pop(move.from_box_id)
      print(f"Removed box {move.from_box_id}")
      print(f"Now have {len(self.boxes)} boxes")



  def is_valid_move(self, move: Move) -> bool:
    '''
    Checks whether a move of a rectangle to a new box and coordinates is valid
    '''
    # Get old box, new box and rect
    from_box = self.boxes[move.from_box_id]
    to_box = self.boxes[move.to_box_id]
    rect = from_box.rects[move.rect_id].copy()

    if move.flip:
      rect.flip()
    rect.x = move.new_x
    rect.y = move.new_y

    # Check if the rect would overflow to the right/bottom
    if move.new_x + rect.width > self.side_length:
      return False
    if move.new_y + rect.height > self.side_length:
      return False

    # Check if the rect would overlap with any other rect in the new box
    for other_rect in to_box.rects.values():
      if rect.overlaps(other_rect, 0.00):
        return False
    return True

  def get_potential_score(self, move: Move) -> Score:
    '''
    Calculates the potential score of the solution after a given move.
    Assumes validity of the move.
    '''
    # Get old box, new box and rect
    from_box = self.boxes[move.from_box_id]
    to_box = self.boxes[move.to_box_id]
    rect = from_box.rects[move.rect_id]

    #store the old location
    old_x = rect.x
    old_y = rect.y

    box_count = len(self.boxes)
    # If the old box is now empty, we will have one box less
    if len(from_box.rects) == 1 and (move.from_box_id != move.to_box_id):
      box_count -= 1


    # first do the move operation, later redo.
    from_box.remove_rect(move.rect_id)
    if move.flip:
      rect.flip()
    rect.x = move.new_x
    rect.y = move.new_y
    to_box.add_rect(rect)

    #count incident edges
    incident_edges = self.compute_incident_edge_coordinates()

    # Undo the move operation
    to_box.remove_rect(move.rect_id)
    rect.x = old_x
    rect.y = old_y
    if move.flip:
      rect.flip()
    from_box.add_rect(rect)

    return Score(box_count, incident_edges)

  def compute_incident_edge_coordinates(self) -> int:
    '''number of coordinates that at least 2 rectangles share.'''
    edges = 0
    for box in self.boxes.values():
      edges += box.get_incident_edge_count()
    return edges



  def get_score(self) -> Score:
    # Very large number
    if not self.is_valid():
      return Score(sys.maxsize, -sys.maxsize - 1)

    # Count non-empty boxes and incident edges between rects as scoring criteria
    box_counts =  len(self.boxes)
    #incident_edges = self.compute_incident_edges() # In the score calculation we compute a maximization for incident edges.
    incident_edges = self.compute_incident_edge_coordinates()
    return Score(box_counts, incident_edges)


## DEPRECATED, now in box.py
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
        if rect.x + rect.width == self.side_length:
          edges += rect.height
        if rect.y == 0:
          edges += rect.width
        if rect.y + rect.height == self.side_length:
          edges += rect.width
    return edges


  def is_valid(self):
    # Go over all rects in all boxes
    for box in self.boxes.values():
      # Easy case: Rect is out-of-bounds
      for rect in box.rects.values():
        if rect.x + rect.width > self.side_length or rect.y + rect.height > self.side_length:
          return False

      # Harder case: Rect may overlap with any other in this box
      for rect_a, rect_b in combinations(box.rects.values(), 2):
        if rect_a.overlaps(rect_b, self.currently_permissible_overlap):
          return False
    return True
