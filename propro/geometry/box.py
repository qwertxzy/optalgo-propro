import logging
from collections import Counter
from itertools import product, chain

from .rectangle import Rectangle

logger = logging.getLogger(__name__)

class Box:
  '''
  One box of the box-rect problem.
  '''
  rects: dict[int, Rectangle]
  '''The rectangles currently in this box. Maps rectangle id to rectangle object.'''
  id: int
  '''ID of this box'''
  __incident_edge_count: int
  '''number of coordinates that at least 2 rectangles in this box share.'''
  __free_coords: set[tuple[int, int]]
  '''All free coordinates in this box. These are coordinates used for search space exploration.'''
  __adjacent_coordinates: set[tuple[int, int]]
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
    self.__free_coords = set(product(range(side_length), range(side_length)))
    self.__incident_edge_count = 0
    self.__adjacent_coordinates = set()
    self.dirty = True
    self.needs_redraw = True

    # Init with top and left edge
    self.adjacent_coordinates = set(chain(
      product(range(self.side_length + 1), [0]),
      product([0], range(self.side_length + 1))
    ))

    for rect in rects:
      self.add_rect(rect)

  def set_box_id(self, b_id: int):
    '''
    Sets the box id of this box.
    '''
    self.id = b_id
    for rect in self.rects.values():
      rect.set_box_id(b_id)


  def add_rect(self, rect: Rectangle, check_overlap = True) -> bool:
    '''Tries to place a rectangle within this box. Will return false if unsuccessful.'''
    self.recalculate_stats()
    # If rects coordinates are not part of free cords, this won't fit
    if check_overlap and not rect.get_all_coordinates() <= self.__free_coords:
      return False

    # Add rect to internal dict
    self.rects[rect.id] = rect

    # Set the dirty flag for incident edge stats
    self.dirty = True
    self.needs_redraw = True
    return True
  
  def fit_rect_compress(self, rect: Rectangle, apply_insertion: bool = True) -> bool:
    ''' Tries to place a rectangle within this box. Will return false if unsuccessful. 
        This method will try to fit a rectangle into the box and sets its coordinates
        accordingly if apply_insertion parameter is set to true.'''
    self.recalculate_stats()
    # get all the free coordinates
    free_coords = self.get_free_coordinates()
    # sort the free coordinates first by x and then y
    sorted_free_coords = sorted(free_coords, key=lambda coord: (coord[0], coord[1]))
    # check if the rectangle would fit. 
    for x, y in sorted_free_coords:
      # does free_coords contain all the coordinates of the rectangle?
      if all((x + i, y + j) in free_coords for i in range(rect.get_width()) for j in range(rect.get_height())):
        if apply_insertion:
          rect.move_to(x, y, box_id=self.id)
          self.add_rect(rect)
        return True
      # check the flipped version
      if all((x + i, y + j) in free_coords for i in range(rect.get_height()) for j in range(rect.get_width())):
        if apply_insertion:
          rect.flip()
          rect.move_to(x, y, box_id=self.id)
          self.add_rect(rect)
        return True
    return False

  def remove_rect(self, rect_id: int) -> Rectangle:
    '''Removes a rectangle from this box.'''
    self.recalculate_stats()

    # Update adjacent coordinate set
    self.__adjacent_coordinates ^= self.rects[rect_id].get_edges()

    self.dirty = True
    self.needs_redraw = True
    # Remove rect from internal dict
    return self.rects.pop(rect_id)

  def get_free_coordinates(self) -> set[tuple[int, int]]:
    '''Returns all currently free x/y coordinates in this box.'''
    self.recalculate_stats()
    return self.__free_coords
  

  def get_adjacent_coordinates(self) -> set[tuple[int, int]]:
    '''
    Returns all coordinates adjacent to the rectangles in this box.
    '''
    self.recalculate_stats()
    return self.__adjacent_coordinates

  def get_incident_edge_count(self) -> int:
    '''
    Returns the number of coordinates that at least 2 rectangles in this box share.
    '''
    if self.dirty:
      self.recalculate_stats()
    return self.__incident_edge_count
  
  def recalculate_stats(self):
    '''
    Recalculates the statistics of this box if the box is dirty.
    '''
    if self.dirty:
      self.__recalculate_adjacent_coordinates()
      self.__recalculate_free_coordinates()
      self.__recalculate_incident_edge_count()
      self.dirty = False

  def __recalculate_free_coordinates(self):
    '''
    Recalculates the free coordinates in this box.
    '''
    self.__free_coords = set(product(range(self.side_length), range(self.side_length)))
    for rect in self.rects.values():
      self.__free_coords = self.__free_coords - rect.get_all_coordinates()

  def __recalculate_adjacent_coordinates(self):
    '''
    Recalculates the coordinates adjacent to the rectangles in this box.
    '''
    # Clear the set
    self.__adjacent_coordinates.clear()

    # Add the left and top edge of the box
    self.__adjacent_coordinates |= set(chain(
      product(range(self.side_length + 1), [0]),
      product([0], range(self.side_length + 1))
    ))

    # Xor each rects edges to the box set, will remove covered edges between two rects
    for rect in self.rects.values():
      self.__adjacent_coordinates ^= rect.get_edges()
    # ..but that would falsely remove corners where 3 or 4 can intersect, so add these back
    for rect in self.rects.values():
      self.__adjacent_coordinates |= rect.get_corners()

  def __recalculate_incident_edge_count(self):
    '''
    Recalculates the number of adjacent edge coordinates of the rectangles in this box.
    '''
    self.__incident_edge_count = 0

    # Count edge coordinate occurrences in a map of (coordinate -> count)
    edge_count = Counter()
    for rect in self.rects.values():
      edge_count.update(rect.get_edges())
      # While we're at it, also count edges of rects that lie on the box border
      if rect.get_x() == 0 or rect.get_x() + rect.get_width() == self.side_length:
        self.__incident_edge_count += rect.get_height()
      if rect.get_y() == 0 or rect.get_y() + rect.get_height() == self.side_length:
        self.__incident_edge_count += rect.get_width()

    # Add all edges that are incident to more than one rectangle (have a count > 1)
    self.__incident_edge_count += sum(e for e in edge_count.values() if e > 1)
