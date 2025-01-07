'''
Main application module of this project.
'''

from math import sqrt, floor
from argparse import ArgumentParser
import threading

import FreeSimpleGUI as sg

from problem import BoxSolution, BoxProblem
from algorithm import OptimizationAlgorithm
from neighborhoods import NeighborhoodDefinition
from config import RunConfiguration, show_config_picker

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
  for box_idx, box in enumerate(solution.boxes.values()):
    box_row = box_idx % boxes_per_row
    box_idx_in_row = floor(box_idx / boxes_per_row)

    box_top_left = (
      box_idx_in_row * (solution.side_length + BOX_SPACING) * scaling_factor,
      box_row * (solution.side_length + BOX_SPACING) * scaling_factor
    )
    box_bot_right = (
      box_top_left[0] + solution.side_length * scaling_factor,
      box_top_left[1] + solution.side_length * scaling_factor
    )
    graph.draw_rectangle(top_left=box_top_left, bottom_right=box_bot_right, fill_color='gray')

    # Also paint the box's rectangles
    for rect in box.rects.values():
      rect_top_left = (
        box_top_left[0] + rect.x * scaling_factor,
        box_top_left[1] + rect.y * scaling_factor
      )
      rect_bot_right = (
        rect_top_left[0] + rect.width * scaling_factor,
        rect_top_left[1] + rect.height * scaling_factor
      )
      graph.draw_rectangle(rect_top_left, rect_bot_right, fill_color='red')

    # Debug or leave this in? Maybe as an option
    # Paint the box's free coordinate search space
    for (x, y) in box.get_free_coordinates():
      coord_top_left = (
        box_top_left[0] + (x + 0.25) * scaling_factor,
        box_top_left[1] + (y + 0.25) * scaling_factor
      )
      coord_bot_right = (
        box_top_left[0] + (x + 0.75) * scaling_factor,
        box_top_left[1] + (y + 0.75) * scaling_factor
      )
      graph.draw_rectangle(coord_top_left, coord_bot_right, fill_color='blue')

def tick_thread_wrapper(algo: OptimizationAlgorithm, window: sg.Window):
  '''Wrapper for executing the tick method in its own thread'''
  # Disable the tick button
  window["tick_btn"].update(disabled=True, text="Working...")

  # Get number of ticks to run
  # TODO: really needs a "run continuous" mode..
  num_ticks = int(window["num_ticks"].get())
  for _ in range(num_ticks):
    algo.tick()
    window.write_event_value("TICK DONE", "")

  # Enable button again
  window["tick_btn"].update(disabled=False, text="Tick")

# Main application part
def show_app(config: RunConfiguration):
  '''Shows the main application for algorithm visualization'''  
  # GUI initialization stuff
  layout = [
    [
      sg.Button("Tick", k="tick_btn"),
      sg.Text("Number of ticks"),
      sg.Input("1", k="num_ticks"),
      sg.Slider(range=(1, 10), default_value=2, resolution=0.5, key='scaling', enable_events=True, orientation='h'),
      sg.Listbox([e.name for e in NeighborhoodDefinition], select_mode='LISTBOX_SELECT_MODE_EXTENDED', enable_events=True, key='neighborhood', default_values=[config.neighborhood.name], size=(25, 3))
    ],
    [
      sg.Graph(background_color='white', canvas_size=(500, 500), graph_bottom_left=(-5, 105), graph_top_right=(105, -5), expand_x=True, expand_y=True, key='graph')
    ]
  ]
  window = sg.Window("Optimierungsalgorithmen Programmierprojekt", layout, resizable=True)
  graph = window['graph']
  window.finalize()
  values = {'scaling': 2} # Hacky way to keep draw_solution above window.read

  # OptAlgo stuff
  optimization_problem = BoxProblem(
    box_length=config.box_length,
    n_rect=config.rect_number,
    w_range=config.rect_x_size,
    h_range=config.rect_y_size
  )
  optimization_algorithm = config.algorithm(optimization_problem, config.neighborhood)

  while True:
    draw_solution(graph, optimization_algorithm.get_current_solution(), scaling_factor=values['scaling'])
    event, values = window.read()

    match event:
      case "Exit" | sg.WIN_CLOSED:
        # TODO: needs to kill the algorithm thread if its still running
        break
      case "tick_btn":
        threading.Thread(target=tick_thread_wrapper, args=(optimization_algorithm, window), daemon=True).start()
      case "neighborhood":
        optimization_algorithm.set_neighborhood_definition(NeighborhoodDefinition[values['neighborhood'][0]]) # Why is this a list
      case "TICK DONE":
        window.refresh()

# Entrypoint, will either get config as args or via gui dialogue
if __name__ == "__main__":
  # Start by parsing args
  parser = ArgumentParser()
  parser.add_argument("--algorithm", type=str)
  parser.add_argument("--neighborhood", type=str)
  parser.add_argument("--rect-number", type=int)
  parser.add_argument("--rect-x", type=str) # e.g. 5-12
  parser.add_argument("--rect-y", type=str)
  parser.add_argument("--box-length", type=int)

  args = parser.parse_args()

  # Try and construct run config from args,
  # and if it fails, show dialogue

  try:
    # Get algorithm class from the name
    algo = next(filter(lambda a: a.__name__ == args.algorithm, OptimizationAlgorithm.__subclasses__()))
    config = RunConfiguration(
      algorithm=algo,
      neighborhood=NeighborhoodDefinition[args.neighborhood],
      rect_number=args.rect_number,
      rect_x_size=range(*[int(i) for i in args.rect_x.split("-")]),
      rect_y_size=range(*[int(i) for i in args.rect_y.split("-")]),
      box_length=args.box_length
    )
  except Exception as e:
    print("Could not get configuration from args, showing config picker..")
    print(e)
    config = show_config_picker()

  # Launch main app with the config
  show_app(config)
