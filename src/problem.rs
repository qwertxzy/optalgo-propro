use std::ops::Range;
use rand::Rng;
use itertools::Itertools;

// Holds info about a rectangle that can be fit into boxes
#[derive(Debug, Clone)]
pub struct ProblemRectangle {
  x: u32,
  y: u32,
  width: u32,
  height: u32,
  box_idx: usize,
  id: u32
}

impl ProblemRectangle {
  pub fn overlaps(&self, other: &ProblemRectangle) -> bool {
    // Check if the two are equal
    if self.id == other.id {
      return false;
    }
    // Check for overlap
    return
      (self.x < other.x + other.width) &&
      (self.x + self.width > other.x) &&
      (self.y < other.y + other.height) &&
      (self.y + self.height > other.y)
  }

  // TODO: anything nicer than these casts?
  pub fn get_origin(&self) -> [f32; 2] {
    [self.x as f32, self.y as f32]
  }

  pub fn get_size(&self) -> [f32; 2] {
    [self.width as f32, self.height as f32]
  }

  pub fn get_id(&self) -> u32 {
    self.id
  }
}

// Holds info about one box that has a number of rectangles in it
#[derive(Debug)]
pub struct ProblemBox {
  pub side_length: u32,
  pub rectangles: Vec<ProblemRectangle>
}

pub enum NeighborhoodType {
  Geometric,
  GeometricOverlap,
  Permutation
}


// Encapsulates the whole problem instance
#[derive(Debug)]
pub struct Problem {
  pub boxes: Vec<ProblemBox>,
  pub score: u32,
  pub last_moved_rec_id: Option<u32>
}

impl Problem {
    // Move rect to a new box and coordinate
    fn move_rect(&mut self, rect_id: u32, old_box_idx: usize, new_x: u32, new_y: u32, new_box_idx: usize, flip: bool) {
      // TODO: error handling
      // Get rect in self
      let old_box = self.boxes.get_mut(old_box_idx).unwrap();
      let rect_idx = old_box.rectangles.iter().position(|r| r.id == rect_id).unwrap();
      let rect = old_box.rectangles.get_mut(rect_idx).unwrap();

      // Update the coordinates
      rect.x = new_x;
      rect.y = new_y;
      if flip {
        (rect.height, rect.width) = (rect.width, rect.height);
      }
      
      // if the box stays the same we are done -> return
      if old_box_idx == new_box_idx {
        return
      }
      // else, move the box from the old box vec to the new one
      // Pop rect from old box's rect vec
      let mut new_rect = old_box.rectangles.swap_remove(rect_idx);
      // Don't forget to update the rects box idx 
      new_rect.box_idx = new_box_idx;
      // Push to new box vec
      let new_box: &mut ProblemBox = self.boxes.get_mut(new_box_idx).unwrap();
      new_box.rectangles.push(new_rect);

      // Also record last moved rect id in problem
      self.last_moved_rec_id = Some(rect_id);

    }

    // Score this current solution to the problem
    // TODO: include some sort of factor for how tightly packed a box is?
    fn calculate_score(&mut self) {
        if self.is_valid() {
          // Count boxes with more than 0 rectangles in them
          self.score = self.boxes.iter().filter(|b| b.rectangles.len() > 0).count() as u32;
        } else {
          self.score = 0;
        }
    }

    // Check whether the current solution is even valid
    pub fn is_valid(&self) -> bool {
      // Go over all rects in all boxes, check whether the coordinates are within the box length
      for problem_box in self.boxes.iter() {
        for problem_rect in problem_box.rectangles.iter() {
          // Easy check: Rect is out of bounds of box coordinates
          if (problem_rect.x + problem_rect.width > problem_box.side_length) || (problem_rect.y + problem_rect.height > problem_box.side_length) {
              return false;
          }
          // Harder check: Rect overlaps with other (overlaps() accounts for self overlap)
          if problem_box.rectangles.iter().any(|r| r.overlaps(problem_rect)) {
            return false;
          }
        }
      }
      return true;
    }

    // Generate a new random problem
    pub fn new(
      box_length: u32,
      num_rect: u32,
      x_range: Range<u32>,
      y_range: Range<u32>
    ) -> Problem {
      // Will generate the most trivial solution with each rect in its own box
      let mut p = Problem::default();
      
      for i in 0..num_rect {
        // TODO: these clones are stupid, also RNG should maybe be seeded manually?
        let rwidth = rand::thread_rng().gen_range(x_range.clone());
        let rheight = rand::thread_rng().gen_range(y_range.clone());
        let rect = ProblemRectangle {
          x: 0,
          y: 0,
          width: rwidth,
          height: rheight,
          box_idx: i as usize,
          id: i
        };

        let b = ProblemBox {
          side_length: box_length,
          rectangles: vec![rect]
        };
        p.boxes.push(b);
      }
      return p;
    }

    fn get_geometric_neighbors(&self) -> Vec<Problem> {
      let mut neighbors = Vec::new();

      // Iterate over all rectangles in all boxes
      for current_rect in self.boxes.iter().flat_map(|b| b.rectangles.iter()) {
        // Now iterate over all possible moves! A rect can be placed
        // ... in any box
        for (possible_box_idx, possible_box) in self.boxes.iter().enumerate() {
          // ... in any coordinate within this box
          for (x, y) in (0..possible_box.side_length).cartesian_product(0..possible_box.side_length) {
            // ... at any rotation
            for is_flipped in [true, false] {
              // Clone into a new neighbor
              let mut neighbor = self.clone();
              // Get the "current rect" in the new neighbor
              neighbor.move_rect(current_rect.id, current_rect.box_idx, x, y, possible_box_idx, is_flipped);
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

    fn get_gemoetric_overlap_neighbors(&self) ->  Vec<Problem> {
      return Vec::new();
    }

    fn get_permutation_neighbors(&self) -> Vec<Problem> {
      return Vec::new();
    }

    // Get neighboring solutions
    pub fn get_neighbors(&self, neighborhood_type: NeighborhoodType) -> Vec<Problem> {
      match neighborhood_type {
          NeighborhoodType::Geometric => self.get_geometric_neighbors(),
          NeighborhoodType::GeometricOverlap => self.get_gemoetric_overlap_neighbors(),
          NeighborhoodType::Permutation => self.get_permutation_neighbors()
      }
    }
}

impl Default for Problem {
    fn default() -> Self {
        Self {
          boxes: Vec::new(),
          score: 0,
          last_moved_rec_id: None
        }
    }
}

impl Clone for Problem {
  fn clone(&self) -> Self {
      Problem {
        boxes: self.boxes.clone(),
        score: self.score,
        last_moved_rec_id: self.last_moved_rec_id
      }
  }
}

impl Clone for ProblemBox {
  fn clone(&self) -> Self {
      ProblemBox {
        side_length: self.side_length,
        rectangles: self.rectangles.clone()
      }
  }
}