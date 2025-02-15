'''
Module for all algorithm related stuff
'''

from .base import OptimizationAlgorithm
from .greedy_search import GreedySearch
from .local_search import LocalSearch
from .simulated_annealing import SimulatedAnnealing
from .util import get_algo_by_name
