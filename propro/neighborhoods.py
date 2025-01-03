'''
Contains different neighborhood types for the solution space.
'''

from itertools import product
from enum import Enum, auto
from copy import deepcopy

from problem import BoxSolution, Rectangle, Box

class NeighborhoodDefinition(Enum):
  '''Enumeration type for all different neighborhood definitions'''
  GEOMETRIC = auto()
  GEOMETRIC_OVERLAP = auto()
  PERMUTATION = auto()

  def get_neighborhood_method(self):
    '''Returns the according neighborhood definition method for this type'''
    match self:
      case NeighborhoodDefinition.PERMUTATION: return get_permutation_neighbors
      case NeighborhoodDefinition.GEOMETRIC: return get_geometric_neighbors
      case NeighborhoodDefinition.GEOMETRIC_OVERLAP: return get_geometric_neighbors

def flatten(xss):
  '''Flatten nested list'''
  return [x for xs in xss for x in xs]

def get_geometric_neighbors(solution: BoxSolution):
  '''
  Calculates neighbors of a solution by geometric means
  Moves every rectangle in every box to every possible coordinate
  '''
  neighbors = []

  # Iterate over all rectangles in all boxes
  for current_box in solution.boxes.values():
    for current_rect in current_box.rects.values():
      # Now iterate over all possible moves! A rect can be placed
      # ... in any box
      for possible_box in solution.boxes.values():
        # ... in any free coordinate within this box
        for (x, y) in current_box.get_free_coordinates():

          # Skip iteration if the rect would overflow to the right/bottom
          if x + current_rect.width >= current_box.side_length:
            continue
          if y + current_rect.height >= current_box.side_length:
            continue

          # ... at any rotation
          for is_flipped in [True, False]:

            neighbor = deepcopy(solution) # <- spensy
            neighbor.move_rect(current_rect.id, current_box.id, x, y, possible_box.id, is_flipped)

            # Skip infeasible neighbors
            # TODO: why does this still produce overflowing boxes?!
            # if neighbor.get_score() == (0, 0):
            #   continue

            neighbors.append(neighbor)
  print(f"Explored {len(neighbors)} neighbors")
  return neighbors

def get_permutation_neighbors(solution: BoxSolution):
  '''
  Encodes the solution into a long list of rects that get placed from top left-to bottom-right
  in each box. Then computes permutations of this list and turns them back to solutions.
  '''
  # Back up the box length from the first box (ugh)
  box_length = solution.boxes[0].side_length

  # Encode solution to list of rects
  encoded_rects = __encode_solution(solution)

  neighbors = []

  # Do every possible pairwise swap
  for i in range(len(encoded_rects) - 1):
    encoded_neighbor = deepcopy(encoded_rects)
    encoded_neighbor[i], encoded_neighbor[i + 1] = encoded_neighbor[i + 1], encoded_neighbor[i]
    neighbor = __decode_rect_list(encoded_neighbor, box_length)
    neighbors.append(neighbor)

  # Also flip every possible rect
  for i in range(len(encoded_rects)):
    encoded_neighbor = deepcopy(encoded_rects)
    this_rect = encoded_neighbor[i]
    this_rect.width, this_rect.height = this_rect.height, this_rect.width
    neighbor = __decode_rect_list(encoded_neighbor, box_length)
    neighbors.append(neighbor)

  return neighbors

def __encode_solution(solution: BoxSolution) -> list[Rectangle]:
  '''
  Turns the solution into a list of boxes
  '''
  return flatten([b.rects.values() for b in solution.boxes.values()])

def __decode_rect_list(rects: list[Rectangle], box_length: int) -> BoxSolution:
  '''
  Turns a list of rectangles into a valid solution to the box-rect problem.
  '''
  # Take rects one by one and put them into a new box..
  # Once one boundary is crossed, start with a new box
  boxes = [Box(0, box_length)]
  current_box = boxes[0]
  current_y = 0 # Current row's y index
  next_x = 0 # Next x coordinate for a box
  next_y = 0 # Next y index for a row
  # Go through rects until all have been processed
  for rect in rects:
    # Case 1: Rect fits into this row
    if next_x + rect.width < box_length and next_y + rect.height < box_length:
      # Update this rect's coordinates
      rect.x = next_x
      rect.y = current_y
      current_box.rects[rect.id] = rect
      # Also update the next corodinate
      next_x += rect.width
      next_y = max(next_y, current_y + rect.height)
      continue
    #  Case 2: Rects overflows to the right, but fits into a next row within this box
    if next_x + rect.width >= box_length and next_y + rect.height < box_length:
      # NOTE: By specification this must fit here, box_length is guaranteed to be larger than any rect side
      rect.x = 0
      rect.y = next_y
      current_box.rects[rect.id] = rect
      # Update coordinates for the next box
      next_x = rect.width
      current_y = next_y
      next_y = current_y + rect.height
      continue
    # Case 3: Rect does not fit into this box, create a new one and push it to boxes
    current_box = Box(len(boxes), box_length)
    rect.x = 0
    rect.y = 0
    current_box.rects[rect.id] = rect
    boxes.append(current_box)
    # And set the next coordinates again
    next_x = rect.width
    current_y = 0
    next_y = rect.height

  # Construct box solution from list of boxes
  return BoxSolution(boxes)
