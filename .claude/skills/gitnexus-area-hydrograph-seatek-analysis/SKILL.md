---
name: gitnexus-area-hydrograph-seatek-analysis
description: "Skill for the Hydrograph_seatek_analysis area of Hydrograph_Versus_Seatek_Sensors_Project. 8 symbols across 4 files."
---

# Hydrograph_seatek_analysis

8 symbols | 4 files | Cohesion: 63%

## When to Use

- Working with code in `src/`
- Understanding how is_safe_path, save_chart, run work
- Modifying hydrograph_seatek_analysis-related functionality

## Key Files

| File                                                              | Symbols                                                   |
| ----------------------------------------------------------------- | --------------------------------------------------------- |
| `src/hydrograph_seatek_analysis/app.py`                           | _create_chart_metadata, _save_generated_chart, run, setup |
| `tests/test_app.py`                                               | test_setup_exception, test_setup_success                  |
| `src/hydrograph_seatek_analysis/utils/security.py`                | is_safe_path                                              |
| `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | save_chart                                                |

## Entry Points

Start here when exploring this area:

- **`is_safe_path`** (Function) —
  `src/hydrograph_seatek_analysis/utils/security.py:82`
- **`save_chart`** (Method) —
  `src/hydrograph_seatek_analysis/visualization/chart_generator.py:301`
- **`run`** (Method) — `src/hydrograph_seatek_analysis/app.py:224`
- **`setup`** (Method) — `src/hydrograph_seatek_analysis/app.py:40`
- **`test_setup_exception`** (Method) — `tests/test_app.py:36`

## Key Symbols

| Symbol                   | Type     | File                                                              | Line |
| ------------------------ | -------- | ----------------------------------------------------------------- | ---- |
| `is_safe_path`           | Function | `src/hydrograph_seatek_analysis/utils/security.py`                | 82   |
| `save_chart`             | Method   | `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | 301  |
| `run`                    | Method   | `src/hydrograph_seatek_analysis/app.py`                           | 224  |
| `setup`                  | Method   | `src/hydrograph_seatek_analysis/app.py`                           | 40   |
| `test_setup_exception`   | Method   | `tests/test_app.py`                                               | 36   |
| `test_setup_success`     | Method   | `tests/test_app.py`                                               | 24   |
| `_create_chart_metadata` | Method   | `src/hydrograph_seatek_analysis/app.py`                           | 101  |
| `_save_generated_chart`  | Method   | `src/hydrograph_seatek_analysis/app.py`                           | 119  |

## Execution Flows

| Flow                             | Type            | Steps |
| -------------------------------- | --------------- | ----- |
| `Main → _check_is_regular_file`  | cross_community | 7     |
| `Main → _validate_columns`       | cross_community | 6     |
| `Main → _setup_sensors`          | cross_community | 6     |
| `Main → _validate_data`          | cross_community | 6     |
| `Main → _find_river_mile_files`  | cross_community | 5     |
| `Main → _compute_validity_masks` | cross_community | 5     |
| `Main → _extract_year_data`      | cross_community | 5     |
| `Main → Convert_to_navd88`       | cross_community | 5     |
| `Run → _get_merged_columns`      | cross_community | 5     |
| `Main → Setup`                   | cross_community | 3     |

## How to Explore

1. `context({name: "is_safe_path"})` — see callers and callees
2. `query({search_query: "hydrograph_seatek_analysis"})` — find related
   execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings
   (source→sink data flows), when indexed with `--pdg`
