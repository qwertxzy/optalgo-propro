from itertools import product




class Rectangle:
  '''
  One rectangle to be fitted into boxes in the box-rect problem.
  '''

  # class variables

  # instance variables
  id: int
  x: int
  y: int
  width: int
  height: int
  maxSize: int 
  '''the maximum of width and height'''
  minSize: int 
  '''the minimum of width and height'''

  # could include overlapping properties here
  # overlapArea: int = 0
  # '''the area of overlap with other rectangles'''
  # overlapRatio: float = 0.0
  # '''the ratio of overlap with other rectangles'''
  # overlaps: dict[int, 'Rectangle'] = dict()
  # '''The rectangles this regtangle overlaps with. 
  # Maps rectangle id to rectangle object'''

  adjacents: dict[int, 'Rectangle'] = dict()
  '''The rectangles this rectangle is adjacent to. No overlap, but touching.
  Maps rectangle id to rectangle object'''
  
  
  def __init__(self, x: int, y: int, w: int, h: int, i: int):
    self.x = x
    self.y = y
    self.width = w
    self.height = h
    self.maxSize = max(w, h)
    self.minSize = min(w, h)
    self.id = i
  
  
  def __repr__(self):
    return f"[{self.id}: ({self.x}+{self.width}/{self.y}+{self.height})]"

  def __eq__(self, value):
    '''Override equality with id check'''
    if not isinstance(value, Rectangle):
      return False
    return self.id == value.id
  
  def copy(self) -> 'Rectangle':
    '''Create a deep copy of this rectangle'''
    return Rectangle(self.x, self.y, self.width, self.height, self.id)
  
  



  def get_area(self) -> int:
    '''Compute area of the rectangle'''
    return self.width * self.height

  def get_all_coordinates(self) -> set[tuple[int, int]]:
    '''Returns all possible points of this rect.'''
    return set(product(
      range(self.x, self.x + self.width),
      range(self.y, self.y + self.height)
    ))

  def contains(self, x: int, y:int) -> bool:
    '''Checks whether a given x/y coordinate lies within this rect.
    !! Excluding the edges.'''
    checks = [
      self.x < x,
      self.x + self.width > x,
      self.y < y,
      self.y + self.height > y
    ]
    return all(checks)

  def overlaps(self, other: 'Rectangle', permissible_overlap: float = 0.0) -> bool:
    '''Checks whether two rectangles overlap, with a permissible amount.'''
    # Check if these two are the same
    if self.id == other.id:
      return False

    # If permissible overlap is zero, do strict boundary checks only
    if permissible_overlap == 0.0:
      # checks = [  # This misses some edge cases i.e. when one rect is inside the other
      #   (self.x < other.x + other.width),
      #   (self.x + self.width > other.x),
      #   (self.y < other.y + other.height),
      #   (self.y + self.height > other.y)
      # ]
      # return all(checks)
      ####This does not seem to work either
      # for x1 in range(self.x, self.x + self.width+1):
      #   for y1 in range(self.y, self.y + self.height+1):
      #     if other.contains(x1, y1):
      #       return True
      # Calculate the intersection area
      x_overlap = max(0, min(self.x + self.width, other.x + other.width) - max(self.x, other.x))
      y_overlap = max(0, min(self.y + self.height, other.y + other.height) - max(self.y, other.y))
      intersection_area = x_overlap * y_overlap
      return intersection_area > 0
        

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


  def get_edges(self) -> set[tuple[int, int]]:
    '''Returns a set of the edge coordinates of the rectangle'''
    ret: set[tuple[int, int]] = set()
    ret = ret.union(self.get_edge("top"))
    ret = ret.union(self.get_edge("bottom"))
    ret = ret.union(self.get_edge("left"))
    ret = ret.union(self.get_edge("right"))
    return ret
  
  def get_placeable_edges(self) -> set[tuple[int, int]]:
    '''Returns a set of the edge coordinates of the rectangle for right and bottom edges'''
    ret: set[tuple[int, int]] = set()
    ret = ret.union(self.get_edge("bottom"))
    ret = ret.union(self.get_edge("right"))
    return ret

  def get_edge(self, dir: str) -> set[tuple[int, int]]:
    '''Returns a set of the edge coordinates of the rectangle for a certain direction.
    dir: "top", "bottom", "left", "right"'''
    if dir == "top":
      return set(product(
        range(self.x, self.x + self.width+1),
        [self.y]
      ))
    if dir == "bottom":
      return set(product(
        range(self.x, self.x + self.width+1),
        [self.y + self.height]
      ))
    if dir == "left":
      return set(product(
        [self.x],
        range(self.y, self.y + self.height+1)
      ))
    if dir == "right":
      return set(product(
        [self.x + self.width],
        range(self.y, self.y + self.height+1)
      ))
    raise ValueError("Invalid direction: " + dir)


  def add_adjacent(self, other: 'Rectangle') -> bool:
    '''Add a rectangle as adjacent to this one'''
    # TODO: check if this is a valid adjacency
    if other.id == self.id:
      return False
    self.adjacents[other.id] = other
    return True
  
  def remove_adjacent(self, other: 'Rectangle') -> bool:
    '''Remove a rectangle as adjacent to this one'''
    if other == self:
      return False
    if not other.id in self.adjacents:
      return False
    self.adjacents.pop(other.id)
    return True

  def is_adjacent(self, other: 'Rectangle') -> bool:
    '''Check if a rectangle is adjacent to this one.
    Must have been already added as adjacent before.'''
    return other.id in self.adjacents
  
  def update_overlap(self):
    '''Recalculate overlap with another rectangles'''
    overlap_coords : set[tuple[int, int]] = set();
    for other in self.overlaps.values():
      overlap_coords = overlap_coords.union(self.get_all_coordinates().intersection(other.get_all_coordinates()))
    self.overlapArea = len(overlap_coords)
    self.overlapRatio = self.overlapArea / self.get_area()

  def add_overlap_with(self, other: 'Rectangle'):
    '''Add a rectangle as overlapping with this one'''
    if other.id == self.id:
      return
    self.overlaps[other.id] = other
    self.update_overlap()

  def remove_overlap_with(self, other: 'Rectangle'):
    '''Remove a rectangle as overlapping with this one'''
    if other == self:
      return
    if not other.id in self.overlaps:
      return
    self.overlaps.pop(other.id)
    self.update_overlap()

  def flip(self):
    '''Flip the rectangle'''
    self.width, self.height = self.height, self.width

  def move(self, direction : str, distance: int):
    '''move the rectangle in a certain direction for a certain distance. 
    No validity checks are done here.'''
    if direction == "horizontal":
      # try to move it to the left      
      self.x = max(self.x - distance, 0)
    elif direction == "vertical":
      # try to move it up
      self.y = max(self.y - distance, 0)
    else:
      raise ValueError("Invalid direction: " + direction)