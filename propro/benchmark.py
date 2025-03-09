'''
Runs benchmarks on the different algorithm varieties.
'''

import logging
import random
import time
from argparse import ArgumentParser
from collections import deque

from rich.table import Table
from rich.console import Console

from algorithms import OptimizationAlgorithm
from modes import get_available_modes
from problem import BoxProblem

# TODO: Assignment calls for several runs to be executed in one call, is this important?

if __name__ == "__main__":
  parser = ArgumentParser()

  parser.add_argument(
    "--rect-number",
    type=int,
    help="Just a number",
    default=200
  )
  parser.add_argument(
    '--tick-number',
    type=int,
    help="Number of ticks to run the algorithms for",
    default=400
  )
  parser.add_argument(
    "--rect-x",
    type=str,
    help="Min-max range (e.g. 5-12)",
    default="1-10"
  )
  parser.add_argument(
    "--rect-y",
    type=str,
    help="Min-max range (e.g. 5-12)",
    default="1-10"
  )
  parser.add_argument(
    "--box-length",
    type=int,
    help="Just a number",
    default=15
  )
  parser.add_argument(
    "--seed",
    type=int,
    help="RNG seed"
  )
  parser.add_argument(
    "--log",
    type=str,
    help="Log level can be one of ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']",
    default="WARNING"
  )

  args = parser.parse_args()

  # Fix seed for deterministic problem generation if specified
  if args.seed is not None:
    random.seed(args.seed)

  # Set log level
  numeric_level = getattr(logging, args.log.upper(), None)
  if not isinstance(numeric_level, int):
    raise ValueError(f"Invalid log level: {args.log}")
  logging.basicConfig(level=numeric_level)

  # Keep track of results for all variations
  # (Algo / Mode / Time / Score)
  results = []

  # Loop over every algorithm
  for Algorithm in OptimizationAlgorithm.__subclasses__():
    # Loop over every mode for this algorithm
    for Mode in get_available_modes(Algorithm):
      logging.info(f"Running {Algorithm.__name__} with {Mode.__name__}")

      # Initialize problem
      optimization_problem = BoxProblem(
        box_length=args.box_length,
        n_rect=args.rect_number,
        w_range=range(*[int(i) for i in args.rect_x.split("-")]),
        h_range=range(*[int(i) for i in args.rect_x.split("-")])
      )
      optimization_algorithm = Algorithm(optimization_problem, Mode)

      # Initialize circular buffer in case the algorithm converges before # ticks is reached
      last_scores = deque(maxlen=5)

      # Run for num ticks
      start_time = time.perf_counter()
      for i in range(args.tick_number):
        logging.info(f"Iteration {i}")
        optimization_algorithm.tick()
        last_scores.append(optimization_algorithm.problem.current_solution.get_heuristic_score())
        # Break loop if algortihm has been stagnant for the last maxlen iterations
        if last_scores.count(last_scores[0]) == last_scores.maxlen:
          break
      stop_time = time.perf_counter()

      # Insert result into list
      results.append((
        Algorithm.__name__,
        Mode.__name__,
        stop_time - start_time,
        optimization_algorithm.problem.current_solution.get_heuristic_score()
      ))

      logging.info(f"Finished in {stop_time - start_time :0.6f} seconds")
      logging.info(f"Score: {optimization_algorithm.problem.current_solution.get_heuristic_score().box_count}")

  # Print results
  table = Table("Algorithm", "Mode", "Time (s)", "Score (#Boxes)")
  for (algo, mode, t, score) in results:
    table.add_row(algo, mode, f"{t:0.6f}", str(score.box_count))

  console = Console()
  console.print(table)
