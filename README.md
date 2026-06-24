# Computational Game Theory software repository

This repository contains software for experimenting with Hedonic Games. Contains both code of general interest, like the `pyhedonic` library, and code specifically written for a working paper:


Gianluca Amato, Gianpiero Monaco, Luca Moscardelli<br>
*Nash Stability in Fractional Hedonic Games with Bounded Size Coalitions*

It is partially supported by the PNRR project FAIR –- Future AI Research (PE00000013), Spoke 9 -- Green-aware AI, under the NRRP MUR program funded by the NextGenerationEU.

## Repository Structure

The project is organized as follows:

- `src/`: Main Python package source code.
	- `src/pyhedonic/`: Core library for modeling and analyzing hedonic games.
		- `hedonicgame_impl.py`: Low-level implementation and performance-sensitive routines.
		- `hedonicgame.py`: Higher-level object-oriented API.
		- `experimental/`: Alternative or in-progress implementations.
- `tests/`: Pytest test suite for both low-level and high-level APIs.
- `scripts/`: Standalone scripts for counting, reporting, and experiment checks.
	- `scripts/data/`: Input/output data files used by reporting scripts.
- `docs/`: Notes, experiment descriptions, and project documentation.
- `paper/`: Material related to the paper, figures and analysis notebooks.
