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
  box_id: int
  '''ID of the box this rect belongs to'''
  # Hide these to force usage of move methods
  __x: int
  __y: int
  __is_dirty_coordinates: bool
  __is_dirty_edges: bool
  width: int
  height: int
  __coordinates: set[tuple[int, int]]
  '''Set of all coordinate point this rect covers'''
  __edges: set[tuple[int, int]]
  '''Set of all edges of this rect'''
  __placeable_edges: set[tuple[int, int]]
  '''Set of the bottom & right edges of this rect'''

  highlighted: bool
  '''Flag to draw this rect in a different color'''

  def __init__(self, x: int, y: int, w: int, h: int, i: int, box_id: int = None):
    self.__x = x
    self.__y = y
    self.width = w
    self.height = h
    self.id = i
    self.box_id = box_id
    self.highlighted = False
    self.__placeable_edges = set()
    self.__edges = set()
    self.__is_dirty_coordinates = True
    self.__is_dirty_edges = True
    

  def __repr__(self):
    return f"[{self.id}: ({self.__x}+{self.width}/{self.__y}+{self.height})]"

  def __eq__(self, value):
    '''Override equality with id check'''
    if not isinstance(value, Rectangle):
      return False
    return self.id == value.id

  def copy(self) -> 'Rectangle':
    '''Create a deep copy of this rectangle'''
    if self.__is_dirty():
      self.__recompute()
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
  
  def get_width(self) -> int:
    '''Returns the width of the rectangle'''
    return self.width
  
  def get_height(self) -> int:
    '''Returns the height of the rectangle'''
    return self.height
  

  def get_all_coordinates(self) -> set[tuple[int, int]]:
    '''Returns all possible points of this rect.'''
    if self.__is_dirty():
      self.__recompute()
    return self.__coordinates

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
  
  def contains_edge(self, x: int, y: int) -> bool:
    '''
    Checks whether a given x/y coordinate lies within this rect.
    !! Including the edges. !!
    '''
    checks = [
      self.__x <= x,
      self.__x + self.width >= x,
      self.__y <= y,
      self.__y + self.height >= y
    ]
    return all(checks)

  def overlaps(self, other: Rectangle, permissible_overlap: float = 0.0) -> bool:
    '''Checks whether two rectangles overlap, with a permissible amount.'''
    if self.__is_dirty():
      self.__recompute()
    # Check if these two are the same
    if self.id == other.id:
      return False

    # Prune by doing AABB check first
    if (self.__x >= other.get_x() + other.get_width() or
        other.get_x() >= self.__x + self.width or
        self.__y >= other.get_y() + other.get_height() or
        other.get_y() >= self.__y + self.height):
      return False

    # If permissible overlap is 0 and if above didn't return,
    # this must be an overlap
    if permissible_overlap == 0.0:
      return True

    # Calculate overlap area
    overlap_x = max(0, min(self.__x + self.width, other.get_x() + other.get_width()) - max(self.__x, other.get_x()))
    overlap_y = max(0, min(self.__y + self.height, other.get_y() + other.height) - max(self.__y, other.get_y()))

    return (overlap_x * overlap_y / (self.get_area() + other.get_area())) > permissible_overlap



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
    if self.__is_dirty():
      self.__recompute()
    return self.__edges

  def get_placeable_edges(self) -> set[tuple[int, int]]:
    '''Returns a set of the edge coordinates of the rectangle for right and bottom edges'''
    if self.__is_dirty():
      self.__recompute()
    return self.__placeable_edges

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


  def __recompute_edges(self):
    # Placeable edges
    self.__placeable_edges.clear()
    self.__placeable_edges |= self.get_edge(bot_right=True)
    # All edges are these + top and left
    self.__edges.clear()
    self.__edges |= self.__placeable_edges
    self.__edges |= self.get_edge(bot_right=False)
    self.__is_dirty_edges = False

  def __recompute_coordinates(self):
    '''Recompute the set of all coordinate points this rect covers'''
    assert self.width > 0 and self.height > 0, "Width and height must be positive"
    assert self.__x >= 0 and self.__y >= 0, "Coordinates must be non-negative"
    
    # #Usage of np array took 11 seconds with the profiler, while the list comprehension took 3.4 seconds
    # # Get coordinates per axis
    # x_coords = np.arange(self.__x, self.__x + self.width)
    # y_coords = np.arange(self.__y, self.__y + self.height)

    # # Reshape them into a grid
    # coordinates_array = np.array(np.meshgrid(x_coords, y_coords)).T.reshape(-1, 2)
    # self.__coordinates = set(map(tuple, coordinates_array))
   
    self.__coordinates = set(
      (x, y) for x in range(self.__x, self.__x + self.width)
              for y in range(self.__y, self.__y + self.height)
    )

    assert len(self.__coordinates) == self.width * self.height, "Number of coordinates does not match area"
    assert all(self.contains_edge(x, y) for x, y in self.__coordinates), "Some coordinates are out of bounds"
    self.__is_dirty_coordinates = False



  def flip(self):
    '''Flip the rectangle'''
    self.width, self.height = self.height, self.width
    self.__is_dirty_coordinates = True
    self.__is_dirty_edges = True

  # NOTE: Tried an alternative move_by method for relative offset, but it ended up being slower
  def move_to(self, new_x: int, new_y: int, box_id: int = None):
    '''Will move the rect to a new origin.'''
    self.__x = new_x
    self.__y = new_y
    self.box_id = box_id
    self.__is_dirty_coordinates = True
    self.__is_dirty_edges = True

  def __recompute(self):
    self.__recompute_edges()
    self.__recompute_coordinates()

  def __is_dirty(self):
    return self.__is_dirty_coordinates or self.__is_dirty_edges
