import logging
import cProfile
import subprocess
import pstats
import random

#pylint: disable=W0401,W0614
from problem import BoxProblem
from algorithms import *
from modes import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix rng seed to make runs comparable
random.seed(1337)

# Set your values here

RECT_NUMBER = 1000
RECT_X = range(1, 16)
RECT_Y = range(1, 16)
BOX_LENGTH = 15

NUM_TICKS = 1000

ALGO = LocalSearch
MODE = Geometric

if __name__ == "__main__":

  # print config information
  logger.info("Running with the following configuration:")
  logger.info("Rectangles: %i", RECT_NUMBER)
  logger.info("Rect X: %s", RECT_X)
  logger.info("Rect Y: %s", RECT_Y)
  logger.info("Box length: %i", BOX_LENGTH)
  logger.info("Number of ticks: %i", NUM_TICKS)
  logger.info("Algorithm: %s", ALGO.__name__)
  logger.info("Mode: %s", MODE.__name__)


  # Construct basic objects
  my_problem = BoxProblem(BOX_LENGTH, RECT_NUMBER, RECT_X, RECT_Y)
  my_algo = ALGO(my_problem, MODE)

  # Profile a few ticks of the algorithm
  pr = cProfile.Profile()
  pr.enable()

  try:
    for i in range(NUM_TICKS):
      logger.info("Iteration %i", i)
      my_algo.tick()
  except KeyboardInterrupt:
    pass

  pr.disable()
  pr.dump_stats("profile_data.prof")

  # Print the stats
  stats = pstats.Stats(pr)
  stats.sort_stats(pstats.SortKey.TIME)
  stats.print_stats(10)

  # Run gprof2dot to convert the profiling data to a dot file
  subprocess.run(["gprof2dot", "-f", "pstats", "profile_data.prof", "-o", "profile_data.dot"])

  # Run Graphviz to generate the call graph
  callgraph_filename = f"callgraph_{ALGO.__name__}_{MODE.__name__}_{RECT_NUMBER}rects_{NUM_TICKS}ticks.png"
  subprocess.run(["dot", "-Tpng", "profile_data.dot", "-o", callgraph_filename])

  logger.info("Call graph generated as %s", callgraph_filename)




  ### Results of the optimization steps
  ## callgraph_LocalSearch_Permutation_100rects_10ticks:
    # initial runtime: 40.6s
    # in parallel: 25.564 seconds
