'''
This module contains the run-configuration for the application
and provides a graphical way of prompting the user for these values
'''

from dataclasses import dataclass
from typing import Optional

import FreeSimpleGUI as sg

from neighborhoods import NeighborhoodDefinition
from selections import SelectionSchema
from algorithms.base import OptimizationAlgorithm
from algorithms.utils import get_mode
from algorithms.local_search import LocalSearch

@dataclass
class RunConfiguration:
  '''Encapsulates all nessecary information to run the application'''

  # Solver specific
  algorithm: OptimizationAlgorithm
  mode: NeighborhoodDefinition | SelectionSchema

  # Problem specific
  rect_number: int
  rect_x_size: range
  rect_y_size: range
  box_length: int


def show_config_picker(
    algo_default: Optional[str] = None,
    mode_default: Optional[str] = None,
    rect_number_default: Optional[int] = None,
    rect_x_default: Optional[range] = None,
    rect_y_default: Optional[range] = None,
    box_len_default: Optional[int] = None
  ) -> RunConfiguration:
  '''Shows a dialogue for the user to pick config values. Accepts optional default values'''
  # Try and parse default mode for correct pre-selection
  algo = next(filter(lambda a: a.__name__ == algo_default, OptimizationAlgorithm.__subclasses__()), LocalSearch)
  Mode = get_mode(algo)

  # Frame for the Solver specific options
  solver_layout = [
    [
      sg.Listbox([a.__name__ for a in OptimizationAlgorithm.__subclasses__()],
                 # Preselect the first in list
                 default_values=algo_default if algo_default else [OptimizationAlgorithm.__subclasses__()[0].__name__],
                 k="algo",
                 select_mode="LISTBOX_SELECT_MODE_SINGLE",
                 size=(25,5),
                 no_scrollbar=True,
                 enable_events=True
                 ),
      sg.Listbox([e.name for e in Mode],
                 # Just the first that python comes up with
                 default_values=mode_default if mode_default else [next(Mode.__iter__()).name],
                 k="mode",
                 select_mode="LISTBOX_SELECT_MODE_SINGLE",
                 size=(25, 5),
                 no_scrollbar=True
                 )
     ]
  ]
  solver_frame = sg.Frame("Optimization Algorithm", layout=solver_layout)

  # Frame for the problem specific options
  problem_layout = [
    [
      sg.Text("Number of rectangles"),
      sg.Input(f"{rect_number_default if rect_number_default else 10}", k="n_rect", size=3)
    ],
    [
      sg.Text("Range of x-sizes"),
      sg.Input(f"{min(rect_x_default) if rect_x_default else 1}", k="x_min", size=2),
      sg.Input(f"{max(rect_x_default) + 1 if rect_x_default else 10}", k="x_max", size=2)
    ],
    [
      sg.Text("Range of y-sizes"),
      sg.Input(f"{min(rect_y_default) if rect_y_default else 1}", k="y_min", size=2),
      sg.Input(f"{max(rect_y_default) + 1 if rect_y_default else 10}", k="y_max", size=2)
    ],
    [
      sg.Text("Box length"),
      sg.Input(f"{box_len_default if box_len_default else 10}", k="box_len", size=3)
    ]
  ]
  problem_frame = sg.Frame("Optimization Problem", layout=problem_layout)

  layout = [
    [solver_frame],
    [problem_frame],
    [sg.Button("Ok")]
  ]

  window = sg.Window("Configuration picker", layout)

  while True:
    event, values = window.read()

    match event:
      case "Exit" | sg.WIN_CLOSED:
        return None
      case "algo":
        # If algorithm selection changes, update the neighborhood/selection box accordingly
        match values["algo"][0]:
          case "LocalSearch":
            window["mode"].update(values=[e.name for e in NeighborhoodDefinition])
          case "GreedySearch":
            window["mode"].update(values=[e.name for e in SelectionSchema])
      case "Ok":
        # Get algorithm class from the name
        algo_name = values["algo"][0]
        algo = next(filter(lambda a: a.__name__ == algo_name, OptimizationAlgorithm.__subclasses__()))
        Mode = get_mode(algo)

        config = RunConfiguration(
          algo,
          Mode[values["mode"][0]],
          int(values["n_rect"]),
          range(int(values["x_min"]), int(values["x_max"])),
          range(int(values["y_min"]), int(values["y_max"])),
          int(values["box_len"])
        )
        window.close()
        return config

# If called directly, just show the dialogue and print the resulting value
if __name__ == "__main__":
  sg.theme("BrightColors")
  conf = show_config_picker()
  print(conf)
