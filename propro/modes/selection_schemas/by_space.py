from collections import defaultdict
from collections.abc import Iterator
from operator import itemgetter

from problem import BoxSolution
from geometry import Rectangle, Box

from .selections import SelectionSchema, SelectionMove

class BySpaceSelection(SelectionSchema):
  '''
  Selection schema will:
   - look for the minimal coordinate where a rect could be placed next
   - expand into the x direction as much as possible
   - expand into the y direction as much as possible
   - find rect from list which is closest to these dimensions
   - if none does, try with the next smallest coordinate
   - if all fail, return the largest rect in a new box
  '''

  @staticmethod
  def find_minimal_coordinates(box: Box) -> Iterator[tuple[int, int]]:
    '''Yields coordinates in a box to search from'''
    all_coords = box.get_free_coordinates()
    # Group free coordinates by x values to create vertical lines
    coords_by_x = defaultdict(list)
    for x, y in all_coords:
      coords_by_x[x].append((x, y))

    # From each of these groups, yield the one with minimal y coordinate since we pack down
    for coords in sorted(coords_by_x.values(), key=itemgetter(0)):
      yield min(coords, key=itemgetter(1))

  @staticmethod
  def expand_coordinate(origin: tuple[int, int], free_coordinates: set[tuple[int, int]]) -> tuple[int, int]:
    '''Will try to expand the given origin in x direction first and then y direction'''
    if origin not in free_coordinates:
      raise ValueError("Cannot expand a rectangle from a non-free origin")

    # First expand in x direction
    right_coordinate = origin
    while right_coordinate in free_coordinates:
      # Step by step so we don't skip a rect in between
      right_coordinate = (right_coordinate[0] + 1, right_coordinate[1])

    # Now expand in y direction (range stop is exclusive so overshooting by 1 is fine)
    line = [
      (x, origin[1])
      for x
      in range(origin[0], right_coordinate[0])
    ]
    while set(line) <= free_coordinates:
      line = list(map(lambda c: (c[0], c[1] + 1), line))

    # Bottom right corner is now x of right coordinate and y of line
    return (right_coordinate[0], line[0][1])

  @classmethod
  def select(cls, partial_solution: BoxSolution, unprocessed_rects: list[Rectangle]) -> SelectionMove:
    '''
     Will look for the first space in the solution that fits one of the provided rectangles.
     If none do, creates a new box.
    '''
    # Step 1: Go over all minimal coordinates
    for box in partial_solution.boxes.values():
      for coordinate in cls.find_minimal_coordinates(box):
        # Step 2: Expand coordinate in x/y directions to find a theoretically ideal rectangle
        bottom_right_coordinate = cls.expand_coordinate(coordinate, box.get_free_coordinates())
        width = bottom_right_coordinate[0] - coordinate[0]
        height = bottom_right_coordinate[1] - coordinate[1]

        # Step 3: Filter rects to those which fit between these points
        possible_rects = [
          r for r in unprocessed_rects
          if r.width <= width and r.height <= height
        ]
        # If no rects are possible here, continue with next coordinate
        if len(possible_rects) == 0:
          continue

        # Pick the one based on the minimal difference between width and height to the target
        rect = min(possible_rects, key=lambda r: (width - r.width, height - r.height))
        rect.move_to(*coordinate)
        return SelectionMove(rect.id, box.id)
    # If we get to here, no coordinate in any box returned a possible rect, so a new box must be created
    new_box = Box(len(partial_solution.boxes), partial_solution.side_length)
    partial_solution.boxes[new_box.id] = new_box
    # To fill this box, the easiest rect is the one with maximum area
    rect = max(unprocessed_rects, key=lambda r: r.get_area())
    rect.move_to(0, 0)
    return SelectionMove(rect.id, new_box.id)
