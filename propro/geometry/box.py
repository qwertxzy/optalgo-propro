from itertools import product

from .rectangle import Rectangle

class Box:
  '''
  One box of the box-rect problem.
  '''

  # class variables


  # instance variables

  # Lookup from rect id -> rect obj
  rects: dict[int, Rectangle]
  '''The rectangles currently in this box. Maps rectangle id to rectangle object.'''
  id: int

  incident_edge_count: int
  '''number of coordinates that at least 2 rectangles in this box share.'''

  # Quick way to get free coordinates in this box
  free_coords: set[tuple[int, int]]
  '''All free coordinates in this box. These are coordinates used for search space exploration.'''
  adjacent_coordinates: set[tuple[int, int]]
  '''All coordinates adjacent to the rectangles in this box.'''
  dirty: bool = True
  '''Flag to indicate that the adjacent coordinates need to be recalculated.'''

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
    self.free_coords = set(product(range(side_length), range(side_length)))
    self.unused_area = set(product(range(side_length), range(side_length)))
    self.unused_area_dirty = False
    self.incident_edge_count = 0
    self.adjacent_coordinates = set()
    self.dirty = True
    for rect in rects:
      self.add_rect(rect)

  def add_rect(self, rect: Rectangle):
    '''Places a rectangle within this box.'''
    # Add rect to internal dict
    self.rects[rect.id] = rect
    # Update free coordinate set
    # TODO: might need to exclude the coordinates on the edges.
    self.free_coords = self.free_coords - rect.get_all_coordinates()
    # Set the dirty flag
    self.dirty = True



  def remove_rect(self, rect_id: int) -> Rectangle:
    '''Removes a rectangle from this box.'''
    # Set coordinates as free again
    self.free_coords = self.free_coords | self.rects[rect_id].get_all_coordinates()
    self.dirty = True
    # Remove rect from internal dict
    return self.rects.pop(rect_id)

  def get_free_coordinates(self) -> set[tuple[int, int]]:
    '''Returns all currently free x/y coordinates in this box.'''
    # TODO: This will currently not work with the overlap neighborhood
    #       But it leaves a nice place for adjusting the search space
    # IDEA: only explore free coordinates next to other boxes or on the box edge
    return self.free_coords

  def recalculate_stats(self):
    '''
    Recalculates the statistics of this box.
    '''
    self.__recalculate_adjacent_coordinates()
    self.__recalculate_incident_edge_count()
    self.dirty = False

  def get_adjacent_coordinates(self) -> set[tuple[int, int]]:
    '''
    Returns all coordinates adjacent to the rectangles in this box.
    '''
    if self.dirty:
      self.recalculate_stats()
    return self.adjacent_coordinates

  def get_incident_edge_count(self) -> int:
    '''
    Returns the number of coordinates that at least 2 rectangles in this box share.
    '''
    if self.dirty:
      self.recalculate_stats()
    return self.incident_edge_count

  def __recalculate_adjacent_coordinates(self):
    '''
    Recalculates the coordinates adjacent to the rectangles in this box.
    '''
    # Clear the set
    self.adjacent_coordinates.clear()
    # add the left and top edge of the box
    self.adjacent_coordinates = self.adjacent_coordinates.union(
      set(product(range(self.side_length+1), [0]))).union(
      set(product([0], range(self.side_length+1))))
    # Go over
    for rect in self.rects.values():
      # Add all coordinates adjacent to this rect
      self.adjacent_coordinates = self.adjacent_coordinates | rect.get_edges()

  def __recalculate_incident_edge_count(self):
    '''
    Recalculates the number of adjacent edge coordinates of the rectangles in this box.
    '''
    self.incident_edge_count = 0

    # count edge coordinate occurrences in a map of (coordinate -> count)
    edge_count: dict[tuple[int, int], int] = dict()
    for rect in self.rects.values():
      for edge in rect.get_edges():
        edge_count[edge] = edge_count.get(edge, 0) + 1

    # count all edges that are incident to more than one rectangle
    for count in edge_count.values():
      if count > 1:
        self.incident_edge_count += 1
