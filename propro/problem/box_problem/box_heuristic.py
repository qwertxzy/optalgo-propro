from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .geometry.rectangle import Rectangle
from ..heuristic import AbstractHeuristic
from ..solution import Solution


@dataclass
class GenericHeuristic(AbstractHeuristic):
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

  def is_valid(self) -> bool:
    return self.box_count is not None

  def __iter__(self):
    return iter((self.box_count, self.box_entropy, self.incident_edges))

  def __repr__(self):
    return f"GenericHeuristic({self.box_count=}, {self.box_entropy=}, {self.incident_edges=})"

  def __lt__(self, other: GenericHeuristic):
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

  def __eq__(self, other: GenericHeuristic):
    return all([
      self.box_count == other.box_count,
      self.box_entropy == other.box_entropy,
      self.incident_edges == other.incident_edges
    ])

  def __le__(self, other: GenericHeuristic):
    return self < other or self == other


@dataclass
class PermutationHeuristic(AbstractHeuristic):
  '''
  Specific heuristic implementation for the permutation neighborhood
  '''
  __size_difference: int
  __is_fillup: bool = False
  __fillup_box_id: int = 0

  '''Difference in size between the two rectangles that are swapped. The Higher the better.'''

  def __init__(self, *args):
    if len(args) == 1:
      self.__init_with_solution(args[0])
    elif len(args) == 2 or len(args) == 3 or len(args) == 4:
      self.__init_with_rects(*args)
    else:
      raise ValueError("PermutationHeuristic can only be initialized with 1 or 3 arguments.")

  def __init_with_solution(self, solution: Solution):
    self.__size_difference = 0


  def __init_with_rects(self, rect_A: 'Rectangle', rect_B: 'Rectangle', is_fillup: bool = False, box_size: int = 0):
    ''' Rectangles A and B are swapped. 
    The larger the difference, the better. 
    Benefits only if the smaller rectangle is moved to the box with the smaller ID. 
    A negative value indicates that the swap is not beneficial.'''
    if rect_A.box_id > rect_B.box_id:
      rect_A, rect_B = rect_B, rect_A
    self.__size_difference = rect_B.get_area() - rect_A.get_area()
    if is_fillup:
      self.__is_fillup = True
      self.__fillup_box_id = rect_A.box_id
      self.__size_difference = box_size**2 + rect_B.get_area()

  def __iter__(self):
    return iter((self.__size_difference, self.__is_fillup, self.__fillup_box_id))

  def __repr__(self):
    return f"PermutationHeuristic({self.__size_difference=}, {self.__is_fillup=}, {self.__fillup_box_id=})"

  def __lt__(self, other: PermutationHeuristic):
    '''
    The higher the size difference, the better.
    If fillup is true, the lower the box id, the better.
    If box id is equal, the higher the size difference, the better.
    '''
    if self.__is_fillup:
      if other.__is_fillup:
        if self.__fillup_box_id == other.__fillup_box_id:
          return self.__size_difference > other.__size_difference
        return self.__fillup_box_id < other.__fillup_box_id
      return True
    return self.__size_difference > other.__size_difference

  def __eq__(self, other: PermutationHeuristic):
    return all([
      self.__size_difference == other.__size_difference,
      self.__is_fillup == other.__is_fillup,
      self.__fillup_box_id == other.__fillup_box_id
    ])

  def __le__(self, other: PermutationHeuristic):
    '''The higher the size difference, the better.
    If fillup is true, the lower the box id, the better.
    If box id is equal, the higher the size difference, the better.'''
    if self.__is_fillup:
      if other.__is_fillup:
        if self.__fillup_box_id == other.__fillup_box_id:
          return self.__size_difference >= other.__size_difference
        return self.__fillup_box_id <= other.__fillup_box_id
      return True
    return self.__size_difference >= other.__size_difference

  def is_valid(self) -> bool:
    return True
