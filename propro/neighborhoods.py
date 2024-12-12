'''
Contains different neighborhood types for the solution space.
'''

from itertools import product
from copy import deepcopy

from problem import BoxSolution

def get_geometric_neighbors(solution: BoxSolution):
  '''
  Calculates neighbors of a solution by geometric means
  Moves every rectangle in every box to every possible coordinate
  '''
  neighbors = []

  # Iterate over all rectangles in all boxes
  for current_box in solution.boxes:
    for current_rect in current_box.rects:
      # Now iterate over all possible moves! A rect can be placed
      # ... in any box
      for possible_box in solution.boxes:
        # ... in any coordinate within this box
        for (x, y) in product(range(possible_box.side_length), range(possible_box.side_length)):
          # ... at any rotation
          for is_flipped in [True, False]:
            neighbor = deepcopy(solution)
            neighbor.move_rect(current_rect.id, current_box.id, x, y, possible_box.id, is_flipped)

            # Skip infeasible neighbors
            # TODO: maybe temporary infeasible solutions might still be worth exploring?
            if neighbor.get_score() == 0:
              continue

            neighbors.append(neighbor)
  return neighbors

def get_permutation_neighbors(solution: BoxSolution):
  '''
  Encodes the solution into a long list of rects that get placed from top left-to bottom-right
  in each box. Then computes permutations of this list and turns them back to solutions.
  '''
  raise NotImplementedError
