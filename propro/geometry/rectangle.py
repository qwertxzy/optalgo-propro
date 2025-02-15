'''
Contains the Rectangle class for the box-rect problem
'''
from __future__ import annotations
from itertools import product

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

  adjacents: dict[int, Rectangle] = dict()
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

    # If permissible overlap is zero, do strict boundary checks only
    if permissible_overlap == 0.0:
      # Calculate the intersection area
      x_overlap = max(0, min(self.__x + self.width, other.get_x() + other.width) - max(self.__x, other.get_x()))
      y_overlap = max(0, min(self.__y + self.height, other.get_y() + other.height) - max(self.__y, other.get_y()))
      intersection_area = x_overlap * y_overlap
      return intersection_area > 0

    # If it's not, we need to compute the overlap area of the two rects
    # and compare it against the permissible value
    overlap_x1 = max(self.__x, other.get_x())
    overlap_y1 = max(self.__y, other.get_y())
    overlap_x2 = min(self.__x + self.width, other.get_x() + other.width)
    overlap_y2 = min(self.__y + self.height, other.get_y() + other.height)

    overlap_width = abs(overlap_x1 - overlap_x2)
    overlap_height = abs(overlap_y1 - overlap_y2)
    overlap_area = overlap_width * overlap_height
    return (overlap_area / (self.get_area() + other.get_area())) > permissible_overlap

  def __recompute_edges(self):
    # Placeable edges
    self.placeable_edges = set()
    self.placeable_edges |= self.get_edge("bottom")
    self.placeable_edges |= self.get_edge("right")
    # All edges are these + top and left
    self.edges = set(self.placeable_edges)
    self.edges |= self.get_edge("top")
    self.edges |= self.get_edge("left")

  def get_edges(self) -> set[tuple[int, int]]:
    '''Returns a set of the edge coordinates of the rectangle'''
    return self.edges

  def get_placeable_edges(self) -> set[tuple[int, int]]:
    '''Returns a set of the edge coordinates of the rectangle for right and bottom edges'''
    return self.placeable_edges

  def get_edge(self, direction: str) -> set[tuple[int, int]]:
    '''
    Returns a set of the edge coordinates of the rectangle for a certain direction.
    Valid directions: "top", "bottom", "left", "right"
    '''
    match direction:
      case "top": return set(product(
          range(self.__x, self.__x + self.width + 1),
          [self.__y]
        ))
      case "bottom": return set(product(
          range(self.__x, self.__x + self.width + 1),
          [self.__y + self.height]
      ))
      case "left": return set(product(
          [self.__x],
          range(self.__y, self.__y + self.height + 1)
      ))
      case "right": return set(product(
          [self.__x + self.width],
          range(self.__y, self.__y + self.height + 1)
      ))
      case d: raise ValueError(f"Invalid direction: {d}")

  # def add_adjacent(self, other: Rectangle) -> bool:
  #   '''Add a rectangle as adjacent to this one'''
  #   # TODO: check if this is a valid adjacency
  #   if other.id == self.id:
  #     return False
  #   self.adjacents[other.id] = other
  #   return True

  # def remove_adjacent(self, other: Rectangle) -> bool:
  #   '''Remove a rectangle as adjacent to this one'''
  #   if other == self:
  #     return False
  #   if not other.id in self.adjacents:
  #     return False
  #   self.adjacents.pop(other.id)
  #   return True

  # def is_adjacent(self, other: Rectangle) -> bool:
  #   '''Check if a rectangle is adjacent to this one.
  #   Must have been already added as adjacent before.'''
  #   return other.id in self.adjacents

  # Commented out since overlaps field  was also commented out
  # def update_overlap(self):
  #   '''Recalculate overlap with another rectangles'''
  #   overlap_coords : set[tuple[int, int]] = set()
  #   for other in self.overlaps.values():
  #     overlap_coords = overlap_coords.union(self.get_all_coordinates().intersection(other.get_all_coordinates()))
  #   self.overlapArea = len(overlap_coords)
  #   self.overlapRatio = self.overlapArea / self.get_area()

  # def add_overlap_with(self, other: 'Rectangle'):
  #   '''Add a rectangle as overlapping with this one'''
  #   if other.id == self.id:
  #     return
  #   self.overlaps[other.id] = other
  #   self.update_overlap()

  # def remove_overlap_with(self, other: 'Rectangle'):
  #   '''Remove a rectangle as overlapping with this one'''
  #   if other == self:
  #     return
  #   if not other.id in self.overlaps:
  #     return
  #   self.overlaps.pop(other.id)
  #   self.update_overlap()

  def __recompute_coordinates(self):
    self.coordinates = set(product(
      range(self.__x, self.__x + self.width),
      range(self.__y, self.__y + self.height)
    ))

  def flip(self):
    '''Flip the rectangle'''
    self.width, self.height = self.height, self.width
    self.__recompute_coordinates()
    self.__recompute_edges()

  # NOTE: Tried an alternative move_by method for relative offset, but it ended up being slower
  def move_to(self, new_x: int, new_y: int):
    '''Will move the rect to a new origin. Expensive, consider using move_by() instead'''
    self.__x = new_x
    self.__y = new_y
    self.__recompute_coordinates()
    self.__recompute_edges()

  # Is this still needed?
  # def move(self, direction: str, distance: int):
  #   '''move the rectangle in a certain direction for a certain distance.
  #   No validity checks are done here.'''
  #   if direction == "horizontal":
  #     # try to move it to the left
  #     self.__x = max(self.__x - distance, 0)
  #   elif direction == "vertical":
  #     # try to move it up
  #     self.__y = max(self.__y - distance, 0)
  #   else:
  #     raise ValueError("Invalid direction: " + direction)
