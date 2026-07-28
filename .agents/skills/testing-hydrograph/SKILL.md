---
name: Hydrograph Seatek Project Local Validation
description: |
  How to run the local test/lint/type-check validation suite for the
  `Hydrograph-Versus-Seatek-Sensors-Project` Python package and what
  non-obvious environment constraints to expect.
---

## When to use this skill

Use this skill when validating Python code changes in the
`Hydrograph-Versus-Seatek-Sensors-Project` repo locally before asking the
lead to merge a PR.

## Repository state this skill applies to

This skill reflects the repository after the `abhi-1586-quarantine-legacy-utils`
(PR #431) cleanup lands:

- `utils/security.py` has migrated to `src/hydrograph_seatek_analysis/utils/security.py`
- legacy `utils/`, `tests/data_processing/`, `tests/utils/`, `tests/enhanced_test_suite.py`, `data_validator.py`, and the broken notebook have been removed
- `tests/visualization/` is no longer excluded in `pyproject.toml`

If you are reviewing an older checkout, the paths and test collection may differ.

## Devin Secrets Needed

None.

## Environment assumptions

- The repo is a Python package managed through `pyproject.toml` (Poetry groups,
  `poetry-core` build backend).
- Use `python3` (not `python`) as the interpreter; `python` may not be on PATH.
- Add `$HOME/.local/bin` to `PATH` for `pytest`, `flake8`, `mypy`, etc.
- The environment is headless, so any matplotlib/processor execution needs
  `MPLBACKEND=Agg`.

## Standard validation commands

1. **Run all tests including visualization tests:**
   ```bash
   cd /path/to/repo
   MPLBACKEND=Agg python3 -m pytest tests/
   ```
   Expected: all tests pass; `tests/visualization/` is collected and executed
   because `pyproject.toml` no longer excludes it.

2. **Lint:**
   ```bash
   PATH="$HOME/.local/bin:$PATH" flake8 src/ tests/
   ```
   Expected: exit code 0, no output.

3. **Import check for migrated `security` utilities:**
   ```bash
   python3 -c "from src.hydrograph_seatek_analysis.utils.security import sanitize_filename, validate_file_size, is_safe_path"
   ```
   Expected: silent success.

4. **Editable install:**
   ```bash
   python3 -m pip install --user -e .
   ```
   Expected: `poetry-core` builds the editable wheel and installs cleanly.

5. **Type check:**
   ```bash
   PATH="$HOME/.local/bin:$PATH" mypy src/
   ```
   Expected: this may abort with pre-existing NumPy/pandas issues
   (missing `pandas-stubs`, NumPy 2.x `type` statement syntax under the
   `python_version = "3.10"` target in `pyproject.toml`). To isolate the
   migrated `security.py` module, run:
   ```bash
   PATH="$HOME/.local/bin:$PATH" mypy src/hydrograph_seatek_analysis/utils/security.py
   ```
   Expected: `Success: no issues found in 1 source file`.

## Known gotchas

- `pytest` may emit a `DeprecationWarning` from the installed `defusedxml`
  package (`cElementTree` is deprecated). This is a third-party warning and
  does not make tests fail.
- `mypy src/` can fail before reaching every source file because of the
  missing pandas stubs / NumPy stub syntax. To prove that `security.py` is clean,
  always type-check it in isolation as well.
- The default maintenance command `python3 -m pip install --user -e .` installs
  the package and its runtime dependencies, but may not install dev-only
  dependencies such as `pytest-mock` and `types-defusedxml`. Install them
  explicitly if they are missing:
  ```bash
  python3 -m pip install --user pytest-mock types-defusedxml
  ```
