'''
Contains the Rectangle class for the box-rect problem
'''
from __future__ import annotations
from itertools import product, chain

import numpy as np

class Rectangle:
  '''
  One rectangle to be fitted into boxes in the box-rect problem.
  '''
  id: int
  # Hide these to force usage of move methods
  __x: int
  __y: int
  width: int
  height: int
  max_size: int
  '''the maximum of width and height'''
  min_size: int
  '''the minimum of width and height'''
  coordinates: set[tuple[int, int]]
  '''Set of all coordinate point this rect covers'''
  edges: set[tuple[int, int]]
  '''Set of all edges of this rect'''
  placeable_edges: set[tuple[int, int]]
  '''Set of the bottom & right edges of this rect'''

  # could include overlapping properties here
  # overlapArea: int = 0
  # '''the area of overlap with other rectangles'''
  # overlapRatio: float = 0.0
  # '''the ratio of overlap with other rectangles'''
  # overlaps: dict[int, 'Rectangle'] = dict()
  # '''The rectangles this regtangle overlaps with.
  # Maps rectangle id to rectangle object'''

  adjacents: dict[int, Rectangle] = {}
  '''
  The rectangles this rectangle is adjacent to. No overlap, but touching.
  Maps rectangle id to rectangle object
  '''

  def __init__(self, x: int, y: int, w: int, h: int, i: int):
    self.__x = x
    self.__y = y
    self.width = w
    self.height = h
    self.max_size = max(w, h)
    self.min_size = min(w, h)
    self.id = i
    self.placeable_edges = set()
    self.edges = set()
    self.__recompute_coordinates()
    self.__recompute_edges()

  def __repr__(self):
    return f"[{self.id}: ({self.__x}+{self.width}/{self.__y}+{self.height})]"

  def __eq__(self, value):
    '''Override equality with id check'''
    if not isinstance(value, Rectangle):
      return False
    return self.id == value.id

  def copy(self) -> 'Rectangle':
    '''Create a deep copy of this rectangle'''
    return Rectangle(self.__x, self.__y, self.width, self.height, self.id)

  def get_area(self) -> int:
    '''Compute area of the rectangle'''
    return self.width * self.height

  def get_x(self) -> int:
    '''Returns x coordinate of the rect's origin'''
    return self.__x

  def get_y(self) -> int:
    '''Returns y coordinate of the rect's origin'''
    return self.__y

  def get_all_coordinates(self) -> set[tuple[int, int]]:
    '''Returns all possible points of this rect.'''
    return self.coordinates

  def contains(self, x: int, y: int) -> bool:
    '''
    Checks whether a given x/y coordinate lies within this rect.
    !! Excluding the edges. !!
    '''
    checks = [
      self.__x < x,
      self.__x + self.width > x,
      self.__y < y,
      self.__y + self.height > y
    ]
    return all(checks)

  def overlaps(self, other: Rectangle, permissible_overlap: float = 0.0) -> bool:
    '''Checks whether two rectangles overlap, with a permissible amount.'''
    # Check if these two are the same
    if self.id == other.id:
      return False

    # Prune by doing AABB check first
    if (self.__x >= other.get_x() + other.width or
        other.get_x() >= self.__x + self.width or
        self.__y >= other.get_y() + other.height or
        other.get_y() >= self.__y + self.height):
      return False

    # If permissible overlap is 0 and if above didn't return,
    # this must be an overlap
    if permissible_overlap == 0.0:
      return True

    # Calculate overlap area
    overlap_x = max(0, min(self.__x + self.width, other.get_x() + other.width) - max(self.__x, other.get_x()))
    overlap_y = max(0, min(self.__y + self.height, other.get_y() + other.height) - max(self.__y, other.get_y()))

    return (overlap_x * overlap_y / (self.get_area() + other.get_area())) > permissible_overlap

  def __recompute_edges(self):
    # Placeable edges
    self.placeable_edges.clear()
    self.placeable_edges |= self.get_edge(bot_right=True)
    # All edges are these + top and left
    self.edges.clear()
    self.edges |= self.placeable_edges
    self.edges |= self.get_edge(bot_right=False)

  def get_corners(self) -> set[tuple[int, int]]:
    '''Returns a set of coordinates for each corner of the rectangle'''
    return set([
      (self.__x, self.__y),
      (self.__x, self.__y + self.height),
      (self.__x + self.width, self.__y),
      (self.__x + self.width, self.__y + self.height)
    ])

  def get_edges(self) -> set[tuple[int, int]]:
    '''Returns a set of the edge coordinates of the rectangle'''
    return self.edges

  def get_placeable_edges(self) -> set[tuple[int, int]]:
    '''Returns a set of the edge coordinates of the rectangle for right and bottom edges'''
    return self.placeable_edges

  def get_edge(self, bot_right: bool = False) -> set[tuple[int, int]]:
    '''
    Returns a set of the edge coordinates of the rectangle for a certain direction.
    If `bot_right = True`, returns only bottom and right edges, otherwise top and left ones.
    '''
    if bot_right:
      return set(chain(
        product(
          range(self.__x, self.__x + self.width + 1),
          [self.__y + self.height]
        ),
        product(
          [self.__x + self.width],
          range(self.__y, self.__y + self.height + 1)
        )
      ))

    return set(chain(
      product(
        range(self.__x, self.__x + self.width + 1),
        [self.__y]
      ),
      product(
        [self.__x],
        range(self.__y, self.__y + self.height + 1)
      )
    ))

  def __recompute_coordinates(self):
    # Get coordinates per axis
    x_coords = np.arange(self.__x, self.__x + self.width)
    y_coords = np.arange(self.__y, self.__y + self.height)

    # Reshape them into a grid
    coordinates_array = np.array(np.meshgrid(x_coords, y_coords)).T.reshape(-1, 2)
    self.coordinates = set(map(tuple, coordinates_array))

  def flip(self):
    '''Flip the rectangle'''
    self.width, self.height = self.height, self.width
    self.__recompute_coordinates()
    self.__recompute_edges()

  # NOTE: Tried an alternative move_by method for relative offset, but it ended up being slower
  def move_to(self, new_x: int, new_y: int):
    '''Will move the rect to a new origin.'''
    self.__x = new_x
    self.__y = new_y
    self.__recompute_coordinates()
    self.__recompute_edges()
