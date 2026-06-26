# Contributing

## Setup

This project uses a `src/` layout and is packaged via `pyproject.toml`.

Create an environment and install dependencies:

```bash
uv sync --group dev
```

## Running Tests

Run the full test suite:

```bash
uv run pytest
```

Run a single file:

```bash
uv run pytest tests/test_pyhedonic_impl.py
```

Run a focused subset:

```bash
uv run pytest tests/test_pyhedonic_impl.py -k unstable
```

## Development Notes

- Core implementation using Numba lives in `src/pyhedonic/hedonicgame_impl.py`.
- The object-oriented wrapper lives in `src/pyhedonic/hedonicgame.py`.
- `tests/test_pyhedonic_impl.py` is the main regression suite for low-level logic.
- Many core functions are decorated with Numba `@njit`; changes should preserve simple, stable numeric data flows.

## Testing Expectations

- Add or update tests for every behavioral change.
- Prefer narrow regression tests first.
- For structures containing NumPy arrays, compare arrays with `np.array_equal`.
- For rational values from `hgimpl.Rational`, compare through `fractions.Fraction`.

## Pull Request / Commit Guidance

- Keep commits scoped to one change.
- Include the verification command you ran in the commit message, PR description, or review notes.
- Separate refactors from behavior changes where possible.

## Agent-Friendly Notes

- This repository is suitable for use with ChatGPT, Codex, and similar coding agents.
- If you use an agent, ask it to:
  - read the target implementation and tests first;
  - avoid broad refactors unless requested;
  - update tests together with code changes;
  - report the exact commands used for verification.
