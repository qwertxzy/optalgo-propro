'''
Runs benchmarks on the different algorithm varieties.
'''

import random
import time

from rich.table import Table
from rich.console import Console

from algorithms import OptimizationAlgorithm, get_mode
from problem import BoxProblem

# TODO: get these from args
num_rect = 10
x_range = range(1, 10)
y_range = range(1, 10)
box_len = 10
num_ticks = 2
rng_seed = 1

# Fix seed for deterministic problem generation
random.seed(rng_seed)

# Keep track of results for all variations
# (Algo / Mode / Time / Score)
results = []

# Loop over every algorithm
for Algorithm in OptimizationAlgorithm.__subclasses__():
  # Loop over every mode for this algorithm
  for Mode in get_mode(Algorithm):

    # Initialize problem
    optimization_problem = BoxProblem(
      box_length=box_len,
      n_rect=num_rect,
      w_range=x_range,
      h_range=y_range
    )
    optimization_algorithm = Algorithm(optimization_problem, Mode)

    # Run for num ticks
    start_time = time.perf_counter()
    for i in range(num_ticks):
      optimization_algorithm.tick()
    stop_time = time.perf_counter()

    # Insert result into list
    results.append((
      Algorithm.__name__,
      Mode.name,
      stop_time - start_time,
      optimization_algorithm.get_current_solution().get_score()
    ))

# Print results
table = Table("Algorithm", "Mode", "Time (s)", "Score (#Boxes)")
for (algo, mode, t, score) in results:
  table.add_row(algo, mode, f"{t:0.6f}", str(score[0]))

console = Console()
console.print(table)
