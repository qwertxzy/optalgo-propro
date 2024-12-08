use itertools::Itertools;
use crate::problem::{Problem, ProblemBox};

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
  // Idea: The solution is encoded in a long list of rectangles
  //       and we generate a valid solution by placing them top left to bottom right
  //       in the boxes. 
  let encoded_problem = encode_permutation_solution(problem_instance);

  // Compute *every* permutation
  let permutations = encoded_problem.iter().permutations(encoded_problem.len());

  // Decode them back to solutions
  let neighbors = permutations.map(|p| decode_permutation_solution(p));

  // Return
  return neighbors;
}

fn encode_permutation_solution(problem_instance :&Problem) -> Vec<ProblemBox> {
  // Make a long list of all problem rects
  let mut rects = Vec::new();
  for problem_box in problem_instance.boxes.iter() {
    for problem_rect in problem_box.rectangles.iter() {
      rects.push(problem_rect);
    }
  }
  // Sort them by box_id, x_coord, y_coord
  rects.sort_unstable_by_key(|r| (r.get_box_idx(), r.get_origin()));
  
  // Null the other values for these rects?

  // Return that list
  return rects;
}

fn decode_permutation_solution(boxes: Vec<ProblemBox>) -> Problem {
  // Initialize empty problem
  // Go through the rect list and place them in the lowest-possible box
  // Carry over other problem parameters?
  // Return new problem
}
