'''
Main application module of this project.
'''

from problem import BoxProblem
from algorithm import LocalSearch

# TODO: All of the visualization & front-end..

if __name__ == "__main__":
  print("Hello :)")
  my_problem = BoxProblem(5, 10, range(1, 5), range(1, 5))
  my_algorithm = LocalSearch(my_problem)

  for i in range(20):
    print(my_problem.current_solution)
    print("-----")
    my_algorithm.tick()
