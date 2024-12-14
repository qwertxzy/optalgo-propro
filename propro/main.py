'''
Main application module of this project.
'''

from math import sqrt, floor

import FreeSimpleGUI as sg

from problem import BoxSolution, BoxProblem
from algorithm import LocalSearch
from neighborhoods import NeighborhoodDefinition

# TODO: All of the visualization & front-end..

# fine-tuning constants
# TODO: should probably be exposed via the GUI?
BOX_SPACING = 2

def draw_solution(graph: sg.Graph, solution: BoxSolution, scaling_factor: float):
  '''
  Draws the given box problem solution in the graph
  '''
  graph.erase()
  # Figure out how many boxes fit into one row
  boxes_per_row = floor(sqrt(len(solution.boxes)))

  # Draw the boxes
  # NOTE: could use itertools.batched() if we switch to python 3.13
  for box_idx, box in enumerate(solution.boxes):
    box_row = box_idx % boxes_per_row
    box_idx_in_row = floor(box_idx / boxes_per_row)

    box_top_left = (
      box_idx_in_row * (box.side_length + BOX_SPACING) * scaling_factor,
      box_row * (box.side_length + BOX_SPACING) * scaling_factor
    )
    box_bot_right = (
      box_top_left[0] + box.side_length * scaling_factor,
      box_top_left[1] + box.side_length * scaling_factor
    )
    graph.draw_rectangle(top_left=box_top_left, bottom_right=box_bot_right, fill_color='gray')

    # Also paint the box's rectangles
    for rect in box.rects:
      rect_top_left = (
        box_top_left[0] + rect.x * scaling_factor,
        box_top_left[1] + rect.y * scaling_factor
      )
      rect_bot_right = (
        rect_top_left[0] + rect.width * scaling_factor,
        rect_top_left[1] + rect.height * scaling_factor
      )
      graph.draw_rectangle(rect_top_left, rect_bot_right, fill_color='red')


# Main application part
if __name__ == "__main__":
  # GUI initialization stuff
  layout = [
    [sg.Button("Tick"), sg.Slider(range=(1, 10), default_value=2, resolution=0.5, key='scaling', enable_events=True, orientation='h')],
    [sg.Listbox([e.name for e in NeighborhoodDefinition], select_mode='LISTBOX_SELECT_MODE_EXTENDED', enable_events=True, key='neighborhood')],
    [sg.Graph(background_color='white', canvas_size=(500, 500), graph_bottom_left=(-5, 105), graph_top_right=(105, -5), expand_x=True, expand_y=True, key='graph')]
  ]
  window = sg.Window("Optimierungsalgorithmen Programmierprojekt", layout, resizable=True)
  graph = window['graph']
  window.finalize()
  values = {'scaling': 2} # Hacky way to keep draw_solution above window.read

  # OptAlgo stuff
  my_problem = BoxProblem(15, 20, range(1, 10), range(1, 10))
  my_algorithm = LocalSearch(my_problem)

  while True:
    draw_solution(graph, my_algorithm.get_current_solution(), scaling_factor=values['scaling'])
    event, values = window.read()

    match event:
      case "Exit" | sg.WIN_CLOSED:
        break
      case "Tick":
        # TODO: make this non-blocking
        # https://docs.pysimplegui.com/en/latest/cookbook/original/multi_threading/#the-thread-based-solution
        my_algorithm.tick()
      case "neighborhood":
        my_algorithm.set_neighborhood_definition(NeighborhoodDefinition[values['neighborhood'][0]]) # Why is this a list
