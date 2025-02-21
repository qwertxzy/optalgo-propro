from collections import Counter
from itertools import product

from .rectangle import Rectangle

class Box:
  '''
  One box of the box-rect problem.
  '''
  rects: dict[int, Rectangle]
  '''The rectangles currently in this box. Maps rectangle id to rectangle object.'''
  id: int
  '''ID of this rectangle'''
  incident_edge_count: int
  '''number of coordinates that at least 2 rectangles in this box share.'''
  free_coords: set[tuple[int, int]]
  '''All free coordinates in this box. These are coordinates used for search space exploration.'''
  adjacent_coordinates: set[tuple[int, int]]
  '''All coordinates adjacent to the rectangles in this box.'''
  dirty: bool = True
  '''Flag to indicate that the adjacent coordinates need to be recalculated.'''

  needs_redraw: bool
  '''Signifies the drawing method that this box has changed and needs to be redrawn'''

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
    self.rects = {}
    self.free_coords = set(product(range(side_length), range(side_length)))
    self.unused_area = set(product(range(side_length), range(side_length)))
    self.unused_area_dirty = False
    self.incident_edge_count = 0
    self.adjacent_coordinates = set()
    self.dirty = True
    self.needs_redraw = True
    for rect in rects:
      self.add_rect(rect)

  def add_rect(self, rect: Rectangle):
    '''Places a rectangle within this box.'''
    # Add rect to internal dict
    self.rects[rect.id] = rect
    # Update free coordinate set
    self.free_coords = self.free_coords - rect.get_all_coordinates()
    # Update adjacent coordinate set
    self.adjacent_coordinates ^= rect.get_edges()
    self.adjacent_coordinates |= rect.get_corners()

    # Set the dirty flag for incident edge stats
    self.dirty = True
    self.needs_redraw = True

  def remove_rect(self, rect_id: int) -> Rectangle:
    '''Removes a rectangle from this box.'''
    # Set coordinates as free again
    self.free_coords = self.free_coords | self.rects[rect_id].get_all_coordinates()

    # Update adjacent coordinate set
    self.adjacent_coordinates ^= self.rects[rect_id].get_edges()

    self.dirty = True
    self.needs_redraw = True
    # Remove rect from internal dict
    return self.rects.pop(rect_id)

  def get_free_coordinates(self) -> set[tuple[int, int]]:
    '''Returns all currently free x/y coordinates in this box.'''
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

    # Add the left and top edge of the box
    self.adjacent_coordinates |= set(product(range(self.side_length + 1), [0]))
    self.adjacent_coordinates |= set(product([0], range(self.side_length + 1)))

    # Xor each rects edges to the box set, will remove covered edges between two rects
    for rect in self.rects.values():
      self.adjacent_coordinates ^= rect.get_edges()
    # ..but that would falsely remove corners where 3 or 4 can intersect, so add these back
    # NOTE: Will have to go over all rects again,
    #       but we could probably also live without these 4 points if speed-up is nessecary?
    for rect in self.rects.values():
      self.adjacent_coordinates |= rect.get_corners()

  def __recalculate_incident_edge_count(self):
    '''
    Recalculates the number of adjacent edge coordinates of the rectangles in this box.
    '''
    self.incident_edge_count = 0

    # Count edge coordinate occurrences in a map of (coordinate -> count)
    edge_count = Counter()
    for rect in self.rects.values():
      edge_count.update(rect.get_edges())
      # While we're at it, also count edges of rects that lie on the box border
      if rect.get_x() == 0 or rect.get_x() + rect.width == self.side_length:
        self.incident_edge_count += rect.height
      if rect.get_y() == 0 or rect.get_y() + rect.height == self.side_length:
        self.incident_edge_count += rect.width

    # Add all edges that are incident to more than one rectangle (have a count > 1)
    self.incident_edge_count += sum(1 for e in edge_count.values() if e > 1)
