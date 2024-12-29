'''
This module contains the run-configuration for the application
and provides a graphical way of prompting the user for these values
'''

from dataclasses import dataclass

import FreeSimpleGUI as sg

from neighborhoods import NeighborhoodDefinition
from algorithm import OptimizationAlgorithm

@dataclass
class RunConfiguration:
  '''Encapsulates all nessecary information to run the application'''

  # Solver specific
  algorithm: OptimizationAlgorithm
  neighborhood: NeighborhoodDefinition

  # Problem specific
  rect_number: int
  rect_x_size: range
  rect_y_size: range
  box_length: int


def show_config_picker() -> RunConfiguration:
  '''Shows a dialogue for the user to pick config values'''
  # Frame for the Solver specific options
  solver_layout = [
    [
      sg.Listbox([a.__name__ for a in OptimizationAlgorithm.__subclasses__()],
                 # Preselect the first in list
                 default_values=[OptimizationAlgorithm.__subclasses__()[0].__name__],
                 k="algo",
                 select_mode="LISTBOX_SELECT_MODE_SINGLE",
                 size=(25,5),
                 no_scrollbar=True
                 ),
      sg.Listbox([e.name for e in NeighborhoodDefinition],
                 # Just the first that python comes up with
                 default_values=[next(NeighborhoodDefinition.__iter__()).name],
                 k="neigh",
                 select_mode="LISTBOX_SELECT_MODE_SINGLE",
                 size=(25, 5),
                 no_scrollbar=True
                 )
     ]
  ]
  solver_frame = sg.Frame("Optimization Algorithm", layout=solver_layout)

  # Frame for the problem specific options
  problem_layout = [
    [sg.Text("Number of rectangles"), sg.Input("10", k="n_rect", size=3)],
    [sg.Text("Range of x-sizes"), sg.Input("1", k="x_min", size=2), sg.Input("10", k="x_max", size=2)],
    [sg.Text("Range of y-sizes"), sg.Input("1", k="y_min", size=2), sg.Input("10", k="y_max", size=2)],
    [sg.Text("Box length"), sg.Input("10", k="box_len", size=3)]
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
      case "Ok":
        # Get algorithm class from the name
        algo_name = values["algo"][0]
        algo = next(filter(lambda a: a.__name__ == algo_name, OptimizationAlgorithm.__subclasses__()))

        config = RunConfiguration(
          algo,
          NeighborhoodDefinition[values["neigh"][0]],
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
