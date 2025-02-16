'''
Main application module of this project.
'''

import logging
from math import sqrt, floor
from argparse import ArgumentParser
import threading
from threading import Event
import random
import FreeSimpleGUI as sg

from problem import BoxSolution, BoxProblem
from algorithms import OptimizationAlgorithm, get_algo_by_name
from modes import get_available_modes, get_mode_by_name
from config import RunConfiguration, show_config_picker

BOX_SPACING = 0.5

# TODO: Assignment calls for gui to be able to re-generate instances and restart with other algo / mode
# TODO: highlight last move?

logger = logging.getLogger(__name__)

def draw_solution(graph: sg.Graph, solution: BoxSolution, scaling_factor: float, erase: bool = False):
  '''
  Draws the given box problem solution in the graph
  '''
  if erase:
    graph.erase()

  # Pre-calculate constants
  boxes_per_row = floor(sqrt(len(solution.boxes)))
  scaled_side_length = solution.side_length * scaling_factor
  scaled_spacing = BOX_SPACING * scaling_factor

  # Draw the boxes
  for box_idx, box in enumerate(list(solution.boxes.values())):

    # Skip box if it doesn't need to be drawn again
    #  unless we erased the whole graph before
    if not (box.needs_redraw or erase):
      continue
    box.needs_redraw = False

    row = box_idx % boxes_per_row
    col = floor(box_idx / boxes_per_row)

    box_left = col * (scaled_side_length + scaled_spacing)
    box_top = row * (scaled_side_length + scaled_spacing)

    # Draw box
    graph.draw_rectangle(
      top_left=(box_left, box_top),
      bottom_right=(box_left + scaled_side_length, box_top + scaled_side_length),
      fill_color='gray'
    )

    # Also paint the box's rectangles
    for rect in list(box.rects.values()):
      rect_left = box_left + rect.get_x() * scaling_factor
      rect_top = box_top + rect.get_y() * scaling_factor
      graph.draw_rectangle(
        top_left=(rect_left, rect_top),
        bottom_right=(rect_left + rect.width * scaling_factor, rect_top + rect.height * scaling_factor),
        fill_color='red'
      )

    # Paint the box's free coordinate search space
    for (x, y) in list(box.get_adjacent_coordinates()):
      dot_left = box_left + (x - 0.1) * scaling_factor
      dot_top = box_top + (y - 0.1) * scaling_factor
      graph.draw_rectangle(
        top_left=(dot_left, dot_top),
        bottom_right=(dot_left + 0.2 * scaling_factor, dot_top + 0.2 * scaling_factor),
        fill_color='blue'
      )

def tick_thread_wrapper(algo: OptimizationAlgorithm, window: sg.Window, tick_complete: Event, redraw_complete: Event):
  '''Wrapper for executing the tick method in its own thread'''
  # Disable the tick button
  window["tick_btn"].update(disabled=True, text="Working...")

  # Get number of ticks to run
  num_ticks = int(window["num_ticks"].get())
  for _ in range(num_ticks):
    algo.tick()
    # Set tick as complete and wait until redraw is finished
    tick_complete.set()
    redraw_complete.wait()
    redraw_complete.clear()

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

  draw_solution(graph, optimization_algorithm.get_current_solution(), scaling_factor=2, erase=True)

  # Events to signal the main thread to redraw the current solution
  tick_complete_event = Event()
  redraw_complete_event = Event()

  # Keep track of last drawn to erase only when boxcount changes
  last_box_count = optimization_algorithm.get_current_solution().get_score().box_count

  while True:
    event, values = window.read(timeout=5)

    match event:
      case "Exit" | sg.WIN_CLOSED:
        break
      case "tick_btn":
        threading.Thread(
          target=tick_thread_wrapper,
          args=(optimization_algorithm, window, tick_complete_event, redraw_complete_event),
          daemon=True
        ).start()
      case "mode":
        mode = get_mode_by_name(optimization_algorithm.__class__, values['mode'][0])
        if mode is not None:
          optimization_algorithm.set_strategy(mode)
      case "scaling":
        # Wait until a possible tick is complete and redraw the whole solution
        # tick_complete_event.wait()
        draw_solution(graph, optimization_algorithm.get_current_solution(), values['scaling'], erase=True)
        redraw_complete_event.set()

    # If the redraw event was set, draw & refresh gui
    if tick_complete_event.is_set():
      current_solution = optimization_algorithm.get_current_solution()
      # Check if we need to redraw the whole solution because box count changed
      if current_solution.get_score().box_count != last_box_count:
        erase = True
        last_box_count = current_solution.get_score().box_count
      else:
        erase = False
      # Actually draw
      draw_solution(graph, current_solution, values['scaling'], erase)
      window.refresh()
      tick_complete_event.clear()
      redraw_complete_event.set()

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
  parser.add_argument(
    "--log",
    type=str,
    help="Log level can be one of ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']",
    default="WARNING"
  )

  args = parser.parse_args()

  # Set random seed if specified
  if args.seed:
    random.seed(args.seed)

  # Set log level
  numeric_level = getattr(logging, args.log.upper(), None)
  if not isinstance(numeric_level, int):
    raise ValueError(f"Invalid log level: {args.log}")
  logging.basicConfig(level=numeric_level)

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
