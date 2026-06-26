# AGENTS

This repository contains Python code for experimenting with fractional hedonic games.

## Project Layout

- `src/pyhedonic/hedonicgame_impl.py`: low-level implementation and enumeration logic.
- `src/pyhedonic/hedonicgame.py`: higher-level object-oriented interface.
- `src/pyhedonic/experimental/hedonicgame_impl.py`: alternative experimental implementation.
- `tests/`: pytest test suite.
- `scripts/`: ad hoc reporting and counting scripts.
- `docs/`: notes and experiment documentation.

## Environment

- Python: `>=3.14`
- Main dependencies: `numpy`, `numba`, `pandas`, `PyYAML`, `networkx`, `pydot`
- Dev dependency: `pytest`, `ruff`, `docformatter`

Recommended setup:

```bash
uv sync --group dev
```

## Commands

Run the full test suite:

```bash
uv run pytest
```

Run one test module:

```bash
uv run pytest tests/test_pyhedonic_impl.py
```

Run a specific test:

```bash
uv run pytest tests/test_pyhedonic_impl.py -k test_count_unstable_games
```

## Code Guidelines

- Prefer module-qualified calls in tests, e.g. `hgimpl.count_unstable_games(...)`.
- When comparing named tuples that contain NumPy arrays, do not rely on direct tuple equality; compare scalar fields directly and arrays with `np.array_equal`.
- When comparing `hgimpl.Rational`, convert to `fractions.Fraction` first.
- Preserve the current style of keeping Numba based implementation-heavy logic in `hedonicgame_impl.py` and higher-level wrappers in `hedonicgame.py`.
- Be careful with Numba-decorated functions:
  - keep data shapes and types stable;
  - avoid introducing Python objects into hot paths unless the file already does so;
  - prefer small, test-backed changes.

## Workflow Guidance

- Before changing enumeration or equilibrium logic, run the most targeted tests you can.
- If you modify counting or price-computation code, verify both:
  - `tests/test_pyhedonic_impl.py`
  - any directly related scripts in `scripts/`
- Do not assume `Makefile` is the source of truth for setup; verify commands against `pyproject.toml` and the current repo layout.

## Recommended Change Pattern

1. Read the relevant implementation and tests first.
2. Make the smallest coherent change.
3. Add or tighten tests for the exact behavior changed.
4. Run targeted tests, then the full test module if practical.
5. Keep commits focused; avoid mixing script, library, and test changes unless they belong to the same behavior change.
