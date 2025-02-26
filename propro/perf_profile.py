import logging
import cProfile
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

RECT_NUMBER = 100
RECT_X = range(1, 16)
RECT_Y = range(1, 16)
BOX_LENGTH = 15

NUM_TICKS = 90

ALGO = LocalSearch
MODE = Geometric

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
ps = pstats.Stats(pr).sort_stats(pstats.SortKey.TIME)
ps.print_stats()
