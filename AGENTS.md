# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

This is a Python scientific data processing tool for analyzing river bed dynamics. It processes Seatek sensor data alongside hydrograph measurements and generates visualizations. No external services, databases, or Docker containers are required.

### Running commands

Standard commands are documented in `CLAUDE.md`. Key references:

- **Tests**: `python3 -m pytest tests/`
- **Lint**: `flake8 src/ tests/`
- **Type check**: `mypy src/`
- **Run processor**: `python3 seatek_processor.py`
- **Run validator**: `python3 validate_data.py`

### Non-obvious caveats

- Use `python3` (not `python`) as the command — `python` is not available on the PATH in this environment.
- Set `MPLBACKEND=Agg` when running the processor or validator to avoid matplotlib display errors in the headless environment.
- Some test files under `tests/data_processing/`, `tests/utils/`, `tests/visualization/`, and `tests/enhanced_test_suite.py` reference a legacy module path (`src.data_processing`) that no longer exists in the refactored v3.0 codebase. These will fail to import. To run only the valid tests, use: `python3 -m pytest tests/test_config.py tests/test_logger.py tests/test_validator.py tests/test_data_loader.py tests/test_data_processor.py`
- The Excel data files (`data/raw/*.xlsx`, `data/processed/*.xlsx`) are gitignored. The applications will report errors about missing data files — this is expected behavior. Unit tests mock all data dependencies and pass without real data files.
- To run the processor end-to-end without polluting the repo, set `HYDROGRAPH_BASE_DIR` to a scratch directory and place input data there. The processor reads `<base>/data/raw/Data_Summary.xlsx` (columns `River_Mile`, `Y_Offset`, `Num_Sensors`), `<base>/data/raw/Hydrograph_Seatek_Data.xlsx` (sheets named `RM_*` with `Time (Seconds)`, `Year`, `Sensor_*`, `Hydrograph (Lagged)`), and `<base>/data/processed/RM_*.xlsx` (same per-river-mile columns), then writes PNG charts to `<base>/output/charts/`. Example: `MPLBACKEND=Agg HYDROGRAPH_BASE_DIR=/tmp/hydro_demo python3 seatek_processor.py`.
- `$HOME/.local/bin` must be on `PATH` for `flake8`, `mypy`, `black`, `pytest` CLI commands to work. Consider adding `black .` to the "Running commands" section if it's part of the standard workflow.

### CodeScene review/salvage trigger

During automated PR review or salvage sessions, if CodeScene is red on a PR, post:

```bash
/cs-agent skill:fix-code-health-degradations
```

Then wait for that run to complete before final defer/salvage disposition.
