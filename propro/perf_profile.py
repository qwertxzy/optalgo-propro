import cProfile
import pstats
import random

#pylint: disable=W0401,W0614
from problem import BoxProblem
from algorithms import *
from modes import *

# Fix rng seed to make runs comparable
random.seed(1337)

# Set your values here

RECT_NUMBER = 500
RECT_X = range(10)
RECT_Y = range(10)
BOX_LENGTH = 15

NUM_TICKS = 100

ALGO = LocalSearch
MODE = Geometric

# Construct basic objects

my_problem = BoxProblem(BOX_LENGTH, RECT_NUMBER, RECT_X, RECT_Y)
my_algo = ALGO(my_problem, MODE)

# Profile a few ticks of the algorithm

pr = cProfile.Profile()
pr.enable()

for _ in range(NUM_TICKS):
  my_algo.tick()

pr.disable()
ps = pstats.Stats(pr).sort_stats(pstats.SortKey.TIME)
ps.print_stats()
