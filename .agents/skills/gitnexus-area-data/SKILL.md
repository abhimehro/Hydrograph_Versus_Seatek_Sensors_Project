---
name: gitnexus-area-data
description: "Skill for the Data area of Hydrograph_Versus_Seatek_Sensors_Project. 26 symbols across 5 files."
---

# Data

26 symbols | 5 files | Cohesion: 83%

## When to Use

- Working with code in `src/`
- Understanding how test_setup_sensors_error, load_data, load_data work
- Modifying data-related functionality

## Key Files

| File                                               | Symbols                                                                                                                                         |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/hydrograph_seatek_analysis/data/processor.py` | _apply_hydro_sentinels, _apply_sensor_sentinels, _apply_sentinels_and_merge, _create_empty_merged, _get_merged_columns (+10)                    |
| `src/hydrograph_seatek_analysis/data/validator.py` | _create_stateful_col_filter, _extract_hydro_time_range, _extract_hydro_years, _extract_processed_time_range, _extract_processed_year_range (+3) |
| `tests/test_data_processor.py`                     | test_setup_sensors_error                                                                                                                        |
| `src/hydrograph_seatek_analysis/app.py`            | load_data                                                                                                                                       |
| `tests/test_app.py`                                | test_load_data_exception                                                                                                                        |

## Entry Points

Start here when exploring this area:

- **`test_setup_sensors_error`** (Function) — `tests/test_data_processor.py:112`
- **`load_data`** (Method) —
  `src/hydrograph_seatek_analysis/data/processor.py:79`
- **`load_data`** (Method) — `src/hydrograph_seatek_analysis/app.py:68`
- **`load_data`** (Method) —
  `src/hydrograph_seatek_analysis/data/processor.py:498`
- **`test_load_data_exception`** (Method) — `tests/test_app.py:46`

## Key Symbols

| Symbol                          | Type     | File                                               | Line |
| ------------------------------- | -------- | -------------------------------------------------- | ---- |
| `test_setup_sensors_error`      | Function | `tests/test_data_processor.py`                     | 112  |
| `load_data`                     | Method   | `src/hydrograph_seatek_analysis/data/processor.py` | 79   |
| `load_data`                     | Method   | `src/hydrograph_seatek_analysis/app.py`            | 68   |
| `load_data`                     | Method   | `src/hydrograph_seatek_analysis/data/processor.py` | 498  |
| `test_load_data_exception`      | Method   | `tests/test_app.py`                                | 46   |
| `_create_stateful_col_filter`   | Method   | `src/hydrograph_seatek_analysis/data/validator.py` | 30   |
| `_extract_hydro_time_range`     | Method   | `src/hydrograph_seatek_analysis/data/validator.py` | 131  |
| `_extract_hydro_years`          | Method   | `src/hydrograph_seatek_analysis/data/validator.py` | 107  |
| `_extract_processed_time_range` | Method   | `src/hydrograph_seatek_analysis/data/validator.py` | 211  |
| `_extract_processed_year_range` | Method   | `src/hydrograph_seatek_analysis/data/validator.py` | 208  |
| `_extract_range`                | Method   | `src/hydrograph_seatek_analysis/data/validator.py` | 117  |
| `_process_hydro_sheet`          | Method   | `src/hydrograph_seatek_analysis/data/validator.py` | 135  |
| `_process_processed_file`       | Method   | `src/hydrograph_seatek_analysis/data/validator.py` | 214  |
| `_apply_hydro_sentinels`        | Method   | `src/hydrograph_seatek_analysis/data/processor.py` | 366  |
| `_apply_sensor_sentinels`       | Method   | `src/hydrograph_seatek_analysis/data/processor.py` | 351  |
| `_apply_sentinels_and_merge`    | Method   | `src/hydrograph_seatek_analysis/data/processor.py` | 383  |
| `_create_empty_merged`          | Method   | `src/hydrograph_seatek_analysis/data/processor.py` | 265  |
| `_get_merged_columns`           | Method   | `src/hydrograph_seatek_analysis/data/processor.py` | 282  |
| `_get_na_value`                 | Method   | `src/hydrograph_seatek_analysis/data/processor.py` | 254  |
| `_setup_sensors`                | Method   | `src/hydrograph_seatek_analysis/data/processor.py` | 152  |

## Execution Flows

| Flow                                 | Type            | Steps |
| ------------------------------------ | --------------- | ----- |
| `Main → _check_is_regular_file`      | cross_community | 7     |
| `Main → _validate_columns`           | cross_community | 6     |
| `Main → _setup_sensors`              | cross_community | 6     |
| `Main → _validate_data`              | cross_community | 6     |
| `Main → _extract_range`              | cross_community | 6     |
| `Main → _check_is_regular_file`      | cross_community | 6     |
| `Main → _find_river_mile_files`      | cross_community | 5     |
| `Main → _create_stateful_col_filter` | cross_community | 5     |
| `Main → _extract_hydro_years`        | cross_community | 5     |
| `Run → _get_merged_columns`          | cross_community | 5     |

## How to Explore

1. `context({name: "test_setup_sensors_error"})` — see callers and callees
2. `query({search_query: "data"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings
   (source→sink data flows), when indexed with `--pdg`
