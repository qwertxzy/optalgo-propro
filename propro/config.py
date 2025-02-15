'''
This module contains the run-configuration for the application
and provides a graphical way of prompting the user for these values
'''

from dataclasses import dataclass
from typing import Optional

import FreeSimpleGUI as sg

from algorithms import OptimizationAlgorithm, LocalSearch, get_algo_by_name
from modes import Mode, get_available_modes, get_mode_by_name

@dataclass
class RunConfiguration:
  '''Encapsulates all nessecary information to run the application. 
  This information stays the same during the run, to be able to restart the same configuration.'''

  # Solver specific
  algorithm: OptimizationAlgorithm
  mode: Mode

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
  mode = next(filter(lambda m: m.__name__ == mode_default, get_available_modes(algo)), get_available_modes(algo)[0])

  # Frame for the Solver specific options
  solver_layout = [
    [
      sg.Listbox([a.__name__ for a in OptimizationAlgorithm.__subclasses__()],
                 # Preselect the first in list
                 default_values=algo_default if algo_default else [algo.__name__],
                 k="algo",
                 select_mode="LISTBOX_SELECT_MODE_SINGLE",
                 size=(25,5),
                 no_scrollbar=True,
                 enable_events=True
                 ),
                 # Just get modes for the same random algo as above
      sg.Listbox([m.__name__ for m in get_available_modes(algo)],
                 default_values=mode.__name__ if mode else [mode.__name__],
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
        algo = get_algo_by_name(values["algo"][0])
        window["mode"].update([m.__name__ for m in get_available_modes(algo)])
      case "Ok":
        # Get algorithm class from the name
        algo = get_algo_by_name(values["algo"][0])
        mode = get_mode_by_name(algo, values["mode"][0])

        # None check
        if algo is None or mode is None:
          raise RuntimeError("Somehow choosing a name from a precomputed list yielded an unexpected result.")

        config = RunConfiguration(
          algo,
          mode,
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
