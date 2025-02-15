'''
Main application module of this project.
'''

import logging
from math import sqrt, floor
from argparse import ArgumentParser
import threading
import random
import FreeSimpleGUI as sg

from problem import BoxSolution, BoxProblem
from algorithms import OptimizationAlgorithm, get_algo_by_name
from modes import get_available_modes, get_mode_by_name
from config import RunConfiguration, show_config_picker

BOX_SPACING = 2

# TODO: Assignment calls for gui to be able to re-generate instances and restart with other algo / mode
# TODO: With moves modifying the solution in-place, the gui sometimes shows garbled graphics when drawing during get_potential_score()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) # TODO: make log level a parameter

def draw_solution(graph: sg.Graph, solution: BoxSolution, scaling_factor: float):
  '''
  Draws the given box problem solution in the graph
  '''
  graph.erase()
  # Figure out how many boxes fit into one row
  boxes_per_row = floor(sqrt(len(solution.boxes)))

  # Draw the boxes
  for box_idx, box in enumerate(list(solution.boxes.values())):
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
    for rect in list(box.rects.values()):
      rect_top_left = (
        box_top_left[0] + rect.get_x() * scaling_factor,
        box_top_left[1] + rect.get_y() * scaling_factor
      )
      rect_bot_right = (
        rect_top_left[0] + rect.width * scaling_factor,
        rect_top_left[1] + rect.height * scaling_factor
      )
      graph.draw_rectangle(rect_top_left, rect_bot_right, fill_color='red')

    # Paint the box's free coordinate search space
    for (x, y) in list(box.get_adjacent_coordinates()):
      coord_top_left = (
        box_top_left[0] + (x - 0.1) * scaling_factor,
        box_top_left[1] + (y - 0.1) * scaling_factor
      )
      coord_bot_right = (
        box_top_left[0] + (x + 0.1) * scaling_factor,
        box_top_left[1] + (y + 0.1) * scaling_factor
      )
      graph.draw_rectangle(coord_top_left, coord_bot_right, fill_color='blue')

def tick_thread_wrapper(algo: OptimizationAlgorithm, window: sg.Window):
  '''Wrapper for executing the tick method in its own thread'''
  # Disable the tick button
  window["tick_btn"].update(disabled=True, text="Working...")

  # Get number of ticks to run
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
      sg.Input("10", k="num_ticks"),
      sg.Slider(range=(1, 10), default_value=2, resolution=0.5, key='scaling', enable_events=True, orientation='h'),
      sg.Listbox(
        [e.__name__ for e in get_available_modes(config.algorithm)],
        select_mode='LISTBOX_SELECT_MODE_EXTENDED',
        enable_events=True,
        key='mode',
        default_values=[config.mode.__name__],
        size=(25, 3)
      )
    ],
    [
      sg.Graph(
        background_color='white',
        canvas_size=(500, 500),
        graph_bottom_left=(-5, 105),
        graph_top_right=(105, -5),
        expand_x=True,
        expand_y=True,
        key='graph'
      )
    ]
  ]
  window = sg.Window("Optimierungsalgorithmen Programmierprojekt", layout, resizable=True)
  graph = window['graph']
  window.finalize()

  # OptAlgo stuff
  optimization_problem: BoxProblem = BoxProblem(
    box_length=config.box_length,
    n_rect=config.rect_number,
    w_range=config.rect_x_size,
    h_range=config.rect_y_size
  )
  optimization_algorithm: OptimizationAlgorithm = config.algorithm(optimization_problem, config.mode)

  draw_solution(graph, optimization_algorithm.get_current_solution(), scaling_factor=2)

  while True:
    event, values = window.read()

    match event:
      case "Exit" | sg.WIN_CLOSED:
        break
      case "tick_btn":
        threading.Thread(target=tick_thread_wrapper, args=(optimization_algorithm, window), daemon=True).start()
      case "mode":
        mode = get_mode_by_name(optimization_algorithm.__class__, values['mode'][0])
        if mode is not None:
          optimization_algorithm.set_strategy(mode)
      case "TICK DONE":
        draw_solution(graph, optimization_algorithm.get_current_solution(), scaling_factor=values['scaling'])
        window.refresh()

# Entrypoint, will either get config as args or via gui dialogue
if __name__ == "__main__":
  # Start by parsing args
  parser = ArgumentParser()
  parser.add_argument(
    "--algorithm",
    type=str,
    help=f"Possible values: {[a.__name__ for a in OptimizationAlgorithm.__subclasses__()]}"
  )
  parser.add_argument(
    "--mode",
    type=str,
    help=f"Possible values: {[m.__name__ for m in get_available_modes(None)]}"
  )
  parser.add_argument(
    "--rect-number",
    type=int,
    help="Just a number"
  )
  parser.add_argument(
    "--rect-x",
    type=str,
    help="Min-max range (e.g. 5-12)"
  )
  parser.add_argument(
    "--rect-y",
    type=str,
    help="Min-max range (e.g. 5-12)"
  )
  parser.add_argument(
    "--box-length",
    type=int,
    help="Just a number"
  )
  parser.add_argument(
    "--seed",
    type=int,
    help="RNG seed"
  )

  args = parser.parse_args()

  if args.seed:
    random.seed(args.seed)

  # Try and construct run config from args,
  # and if it fails, show dialogue

  try:
    # Get algorithm class from the name
    algo = get_algo_by_name(args.algorithm)
    mode = get_mode_by_name(algo, args.mode)
    config = RunConfiguration(
      algorithm=algo,
      mode=mode,
      rect_number=args.rect_number,
      rect_x_size=range(*[int(i) for i in args.rect_x.split("-")]),
      rect_y_size=range(*[int(i) for i in args.rect_y.split("-")]),
      box_length=args.box_length
    )
  #pylint: disable=W0718
  except Exception as e:
    logger.info("Could not get complete configuration from args, showing config picker..")
    config = show_config_picker(
      algo_default=args.algorithm,
      mode_default=args.mode,
      rect_number_default=args.rect_number,
      rect_x_default=range(*[int(i) for i in args.rect_x.split("-")]) if args.rect_x else None,
      rect_y_default=range(*[int(i) for i in args.rect_y.split("-")]) if args.rect_y else None,
      box_len_default=args.box_length
    )

  # Launch main app with the config
  show_app(config)
