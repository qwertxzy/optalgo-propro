# Programmierprojekt Optimierungsalgorithmen

## Setup

```bash
pip install -r requirements.txt
```

## Usage

The program can be run in one of two ways:
Interactive mode will show a configuration picker and a visual representation of what the algorithm is doing.
Benchmark mode will run all known algorithms and modes with the same parameters and output a short overview of each performance.

### Interactive mode

To run the program in interactive mode, execute `python propro/main.py` from the repository's root folder. By adding `-h`, an overview of all possible parameters is given to the user. If all nessecary parameters are specified, the configuration picker will be skipped and the user will be taken to the visualization immeadiately.

In the gui, the user can then let the algorithm run for a number of iterations, adjust the rendering size and change the algorithm's mode on the fly.

### Benchmark Mode

The benchmark mode will run all implemented algorithms and all their respective modes with the same set of parameters. To run it, call `python propro/benchmark.py` from the repository root. It will record the solution quality and runtimes and present them to the user in a table after it finishes execution. To specify the problem parameters, `-h` will give you an overview of all the possible options.

Each benchmark run will finish after either the specified number of iterations is reached or if the algorithm has had the same score for the last five iterations.

## Structure

Main entrypoints for the script are `main.py` for the gui application and `benchmark.py` for the benchmark mode. Furthermore a config module exists to encapsulate possible configuration values the user can set.

### Algorithms

Each algorithm will sit in the `algorithms` module and inherit from `algorithms/base.py`'s OptimizationAlgorithm class. Two such implementations are given with the greedy algorithm, as well as a local search.
Algorithms are expected to be created with a given problem. Afterwards `tick()` can be called to advance the algorithm for one step / one iteration.

### Modes

Modes define different ways an algorithm can run. In the case of the local search, different neighborhood definitions are implemented, while the greedy algorithm has two different schemas on which to select the next rectangle and coordinate where it should be placed in the solution.

Modes are split into Neighborhoods for the local search and SelectionSchemas for the greedy algorithm. Each Mode must thus inherit from one of these two base classes. With each mode, a Move definition must also be implemented. A Move describes the changes needed to get from one (partial) solution to the next. Moves can be applied and undone on a given solution to explore their changes in-place, without having to copy the whole solution object.

Each Mode implementation will only return one or more Moves for a current solution. It is then the task of the algorithm at hand to choose one of these solutions to proceed.
