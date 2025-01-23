from copy import deepcopy

from neighborhoods.neighborhood import Neighborhood, ScoredMove
from problem import BoxSolution

class Permutation(Neighborhood):
  '''Implementation for a permutation-based neighborhood'''

  @classmethod
  def get_neighbors(cls, solution: BoxSolution) -> list[ScoredMove]:
    '''
    Encodes the solution into a long list of rects that get placed from top left-to bottom-right
    in each box. Then computes permutations of this list and turns them back to solutions.
    '''
    print("Claculating Permutation neighborhood")
    encoded_rects = Neighborhood._encode_solution(solution)

    neighbors = []

    # Do every possible pairwise swap
    for i in range(len(encoded_rects) - 1):
      encoded_neighbor = deepcopy(encoded_rects)
      encoded_neighbor[i], encoded_neighbor[i + 1] = encoded_neighbor[i + 1], encoded_neighbor[i]
      neighbor = Neighborhood._decode_rect_list(encoded_neighbor, solution.side_length)
      neighbors.append(neighbor)

    # Also flip every possible rect
    for i in range(len(encoded_rects)):
      encoded_neighbor = deepcopy(encoded_rects)
      this_rect = encoded_neighbor[i]
      this_rect.width, this_rect.height = this_rect.height, this_rect.width
      neighbor = Neighborhood._decode_rect_list(encoded_neighbor, solution.side_length)
      neighbors.append(neighbor)

    return neighbors
