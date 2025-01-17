from .neighborhood import Neighborhood, Move, ScoredMove
from problem import BoxSolution

from copy import deepcopy

class Geometric(Neighborhood):

  @classmethod
  def get_neighbors(cls, solution: BoxSolution) -> list[ScoredMove]:
    '''
    Calculates neighbors of a solution by geometric means
    Moves every rectangle in every box to every possible coordinate
    '''
    print("Calculating Geometric neighborhoods")
    neighbors = []

    # Iterate over all rectangles in all boxes
    for current_box in sorted(solution.boxes.values(), key=lambda box: len(box.rects)):
      for current_rect in list(current_box.rects.values()):
        # Now iterate over all possible moves! A rect can be placed
        # ... in any box
        for possible_box in solution.boxes.values():
          # ... in any free coordinate within this box
          for (x, y) in list(possible_box.get_adjacent_coordinates()):
            # ... at any rotation
            for is_flipped in [False, True]:

              # no move
              if current_box.id == possible_box.id and current_rect.x == x and current_rect.y == y and is_flipped == False:
                continue
              

              move = Move(current_rect.id, current_box.id, possible_box.id, x, y, is_flipped)

              # check if the solution would be valid
              if not solution.is_valid_move(move):
                continue

              # calculate the score of the new solution
              score = solution.get_potential_score(move)

              # add it to the neighbors
              neighbors.append(ScoredMove(move, score))

              # Once a neighbor is found that reduces the main scoring criteria, early return?
              # # Dramatically speeds up early convergence
              # if score.box_count < solution.get_score().box_count:
              #    print(f"Early returned with {len(neighbors)} neighbors")
              #    return neighbors
              # if len(neighbors) > cls.max_neighbors:
              #   print(f"Early returned with {len(neighbors)} neighbors")
              #   return neighbors
    print(f"Explored all {len(neighbors)} neighbors")
    return neighbors
        
    
    