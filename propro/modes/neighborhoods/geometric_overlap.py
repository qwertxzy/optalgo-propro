from itertools import product

from problem import Move, ScoredMove, BoxSolution
from .neighborhood import Neighborhood

class GeometricOverlap(Neighborhood):
  '''Implements a geometric neighborhood definition that allows for adjustable overlap between rects.'''

  @classmethod
  def get_neighbors(cls, solution: BoxSolution) -> list[ScoredMove]:
    '''
    Calculates neighbors of a solution by geometric means
    Moves every rectangle in every box to every possible coordinate
    '''
    print("Calculating Geometric neighborhoods with overlap")

    neighbors = []
    current_score = solution.get_score()

    # Iterate over all rectangles in all boxes
    for current_box in sorted(solution.boxes.values(), key=lambda box: len(box.rects)):
      for current_rect in list(current_box.rects.values()):
        # Now iterate over all possible moves! A rect can be placed
        # ... in any box
        for possible_box in solution.boxes.values():
          # ... in any coordinate within this box
          for (x, y) in product(range(possible_box.side_length), range(possible_box.side_length)):
            # ... at any rotation
            for is_flipped in [False, True]:

              # no move
              if current_box.id == possible_box.id and current_rect.x == x and current_rect.y == y and not is_flipped:
                continue

              # no flip if the rect is square
              if current_rect.width == current_rect.height and is_flipped:
                continue

              move = Move(current_rect.id, current_box.id, possible_box.id, x, y, is_flipped)

              # check if the solution would be valid
              if not solution.is_valid_move(move):
                continue

              # calculate the score of the new solution
              score = solution.get_potential_score(move)

              # if the score is worse or equal, skip this move. This evoids bouncing back and forth
              if current_score <= score:
                continue

              # add it to the neighbors
              neighbors.append(ScoredMove(move, score))

              # Once a solution found that removes one box entirely, early return
              if current_score.box_count > score.box_count:
                print(f"Early returned with {len(neighbors)} neighbors. Removed one Box.")
                return neighbors

              # Once a neighbor is found that reduces the main scoring criteria, early return?
              # # Dramatically speeds up early convergence
              # if score.box_count < solution.get_score().box_count:
              #    print(f"Early returned with {len(neighbors)} neighbors")
              #    return neighbors
              if len(neighbors) > cls.MAX_NEIGHBORS:
                print(f"Early returned with {len(neighbors)} neighbors")
                return neighbors
    print(f"Explored all {len(neighbors)} neighbors")
    return neighbors
