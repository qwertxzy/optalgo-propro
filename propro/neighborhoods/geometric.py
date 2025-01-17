from .neighborhood import Neighborhood
from problem import BoxSolution

from copy import deepcopy

class Geometric(Neighborhood):

  @classmethod
  def get_neighbors(cls, solution: BoxSolution) -> list:
    '''
    Calculates neighbors of a solution by geometric means
    Moves every rectangle in every box to every possible coordinate
    '''
    print("Claculating Geometric neighborhood")
    neighbors = []

    # Iterate over all rectangles in all boxes
    for current_box in sorted(solution.boxes.values(), key=lambda box: len(box.rects)):
      for current_rect in current_box.rects.values():
        # Now iterate over all possible moves! A rect can be placed
        # ... in any box
        for possible_box in solution.boxes.values():
          # ... in any free coordinate within this box
          for (x, y) in current_box.get_free_coordinates():
            # ... at any rotation
            for is_flipped in [True, False]:

              # Skip iteration if the rect would overflow to the right/bottom
              if x + current_rect.width > solution.side_length:
                continue
              if y + current_rect.height > solution.side_length:
                continue


              neighbor = deepcopy(solution) # <- spensy
              neighbor.move_rect(current_rect.id, current_box.id, x, y, possible_box.id, is_flipped)

              neighbors.append(neighbor)
              # Once a neighbor is found that reduces the main scoring criteria, early return?
              # Dramatically speeds up early convergence
              if neighbor.get_score()[0] < solution.get_score()[0]:
                print(f"Early returned with {len(neighbors)} neighbors")
                return neighbors
    print(f"Explored all {len(neighbors)} neighbors")
    return neighbors
        
    
    