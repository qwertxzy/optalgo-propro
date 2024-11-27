use itertools::Itertools;
use crate::problem::Problem;

pub enum NeighborhoodType {
  Geometric,
  GeometricOverlap,
  Permutation
}

pub fn get_geometric_neighbors(problem_instance :&Problem) -> Vec<Problem> {
  let mut neighbors = Vec::new();

  // Iterate over all rectangles in all boxes
  for current_rect in problem_instance.boxes.iter().flat_map(|b| b.rectangles.iter()) {
    // Now iterate over all possible moves! A rect can be placed
    // ... in any box
    for (possible_box_idx, possible_box) in problem_instance.boxes.iter().enumerate() {
      // ... in any coordinate within this box
      for (x, y) in (0..possible_box.side_length).cartesian_product(0..possible_box.side_length) {
        // ... at any rotation
        for is_flipped in [true, false] {
          // Clone into a new neighbor
          let mut neighbor = problem_instance.clone();
          // Get the "current rect" in the new neighbor
          neighbor.move_rect(current_rect.get_id(), current_rect.get_box_idx(), x, y, possible_box_idx, is_flipped);
          neighbor.calculate_score();

          // TODO: skip infeasible neighbors for now
          if neighbor.score == 0 {
            continue;
          }

          neighbors.push(neighbor);
        }
      }
    }
  }
  
  return neighbors;
}

pub fn get_permutation_neighbors(problem_instance: &Problem) -> Vec<Problem> {
  // TODO: implement
  return Vec::new();
}