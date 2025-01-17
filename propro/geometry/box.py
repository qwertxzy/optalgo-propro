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
  # Quick way to get free coordinates in this box
  free_coords: set[tuple[int, int]]
  '''All free coordinates in this box. These are coordinates used for search space exploration.'''
  adjacent_coordinates: set[tuple[int, int]]
  '''All coordinates adjacent to the rectangles in this box.'''

  def __repr__(self):
    s = f"{self.id}: "
    s += ' '.join([str(r) for r in self.rects.values()])
    return s

  def __init__(self, b_id: int, side_length: int, *rects: Rectangle):
    '''
    Initializes a new box with a number of rects
    '''
    self.id = b_id
    self.rects = dict()
    self.free_coords = set(product(range(side_length), range(side_length)))
    self.unused_area = set(product(range(side_length), range(side_length)))
    self.unused_area_dirty = False
    for rect in rects:
      self.add_rect(rect)

  def add_rect(self, rect: Rectangle):
    '''Places a rectangle within this box.'''
    # Add rect to internal dict
    self.rects[rect.id] = rect
    # Update free coordinate set
    # TODO: might need to exclude the coordinates on the edges.
    self.free_coords = self.free_coords - rect.get_all_coordinates()



  def remove_rect(self, rect_id: int) -> Rectangle:
    '''Removes a rectangle from this box.'''
    # Set coordinates as free again
    self.free_coords = self.free_coords | self.rects[rect_id].get_all_coordinates()
    # Remove rect from internal dict
    return self.rects.pop(rect_id)

  def get_free_coordinates(self) -> set[tuple[int, int]]:
    '''Returns all currently free x/y coordinates in this box.'''
    # TODO: This will currently not work with the overlap neighborhood
    #       But it leaves a nice place for adjusting the search space
    # IDEA: only explore free coordinates next to other boxes or on the box edge
    return self.free_coords
  

  def get_adjacent_coordinates(self) -> set[tuple[int, int]]:
    '''
    Returns all coordinates adjacent to the rectangles in this box.
    '''

  def recalculate_adjacent_coordinates(self):
    '''
    Recalculates the coordinates adjacent to the rectangles in this box.
    '''
    # Clear the set
    self.adjacent_coordinates.clear()
    # Go over
    for rect in self.rects.values():
      # Add all coordinates adjacent to this rect
      self.adjacent_coordinates = self.adjacent_coordinates | rect.get_edges()

