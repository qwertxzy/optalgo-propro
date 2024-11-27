use crate::problem::Problem;
use crate::neighborhoods::NeighborhoodType;

pub trait OptimizationAlgorithm {
    fn init(initial_problem: Problem) -> Self;
    fn tick(&mut self) -> &Problem;
    fn get_current_solution(&self) -> &Problem;
}

pub struct LocalSearch {
    problem: Problem
}

impl OptimizationAlgorithm for LocalSearch {
    fn init(initial_problem: Problem) -> Self{
        LocalSearch {
            problem: initial_problem
        }
    }

    fn tick(&mut self) -> &Problem {
        let mut neighbors = self.problem.get_neighbors(NeighborhoodType::Geometric);
        // Sort neighbors by score, pick best one
        neighbors.sort_by_key(|n| n.score);
        self.problem = neighbors.first().unwrap().clone();

        return &self.problem;
    }

    fn get_current_solution(&self) -> &Problem {
        &self.problem
    }
}
// TODO: implementations for greedy search