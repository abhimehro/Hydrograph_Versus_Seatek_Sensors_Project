---
name: gitnexus-area-data
description: "Skill for the Data area of Hydrograph_Versus_Seatek_Sensors_Project. 30 symbols across 5 files."
---

# Data

30 symbols | 5 files | Cohesion: 87%

## When to Use

- Working with code in `src/`
- Understanding how test_validate_columns_failure,
  test_validate_columns_success, test_setup_sensors_error work
- Modifying data-related functionality

## Key Files

| File                                                 | Symbols                                                                                                                                         |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/hydrograph_seatek_analysis/data/processor.py`   | _setup_sensors, _validate_data, load_data, _find_river_mile_files, load_data (+10)                                                              |
| `src/hydrograph_seatek_analysis/data/validator.py`   | _create_stateful_col_filter, _extract_hydro_time_range, _extract_hydro_years, _extract_processed_time_range, _extract_processed_year_range (+3) |
| `src/hydrograph_seatek_analysis/data/data_loader.py` | _load_sheet_data, _process_hydro_sheet, _validate_and_store_sheet, _validate_columns                                                            |
| `tests/test_data_loader.py`                          | test_validate_columns_failure, test_validate_columns_success                                                                                    |
| `tests/test_data_processor.py`                       | test_setup_sensors_error                                                                                                                        |

## Entry Points

Start here when exploring this area:

- **`test_validate_columns_failure`** (Function) —
  `tests/test_data_loader.py:29`
- **`test_validate_columns_success`** (Function) —
  `tests/test_data_loader.py:20`
- **`test_setup_sensors_error`** (Function) — `tests/test_data_processor.py:112`
- **`load_data`** (Method) —
  `src/hydrograph_seatek_analysis/data/processor.py:79`
- **`load_data`** (Method) —
  `src/hydrograph_seatek_analysis/data/processor.py:498`

## Key Symbols

| Symbol                          | Type     | File                                                 | Line |
| ------------------------------- | -------- | ---------------------------------------------------- | ---- |
| `test_validate_columns_failure` | Function | `tests/test_data_loader.py`                          | 29   |
| `test_validate_columns_success` | Function | `tests/test_data_loader.py`                          | 20   |
| `test_setup_sensors_error`      | Function | `tests/test_data_processor.py`                       | 112  |
| `load_data`                     | Method   | `src/hydrograph_seatek_analysis/data/processor.py`   | 79   |
| `load_data`                     | Method   | `src/hydrograph_seatek_analysis/data/processor.py`   | 498  |
| `_create_stateful_col_filter`   | Method   | `src/hydrograph_seatek_analysis/data/validator.py`   | 30   |
| `_extract_hydro_time_range`     | Method   | `src/hydrograph_seatek_analysis/data/validator.py`   | 133  |
| `_extract_hydro_years`          | Method   | `src/hydrograph_seatek_analysis/data/validator.py`   | 109  |
| `_extract_processed_time_range` | Method   | `src/hydrograph_seatek_analysis/data/validator.py`   | 213  |
| `_extract_processed_year_range` | Method   | `src/hydrograph_seatek_analysis/data/validator.py`   | 210  |
| `_extract_range`                | Method   | `src/hydrograph_seatek_analysis/data/validator.py`   | 119  |
| `_process_hydro_sheet`          | Method   | `src/hydrograph_seatek_analysis/data/validator.py`   | 137  |
| `_process_processed_file`       | Method   | `src/hydrograph_seatek_analysis/data/validator.py`   | 216  |
| `_load_sheet_data`              | Method   | `src/hydrograph_seatek_analysis/data/data_loader.py` | 146  |
| `_process_hydro_sheet`          | Method   | `src/hydrograph_seatek_analysis/data/data_loader.py` | 128  |
| `_validate_and_store_sheet`     | Method   | `src/hydrograph_seatek_analysis/data/data_loader.py` | 167  |
| `_validate_columns`             | Method   | `src/hydrograph_seatek_analysis/data/data_loader.py` | 190  |
| `_setup_sensors`                | Method   | `src/hydrograph_seatek_analysis/data/processor.py`   | 152  |
| `_validate_data`                | Method   | `src/hydrograph_seatek_analysis/data/processor.py`   | 136  |
| `_find_river_mile_files`        | Method   | `src/hydrograph_seatek_analysis/data/processor.py`   | 526  |

## Execution Flows

| Flow                                 | Type            | Steps |
| ------------------------------------ | --------------- | ----- |
| `Main → _validate_columns`           | cross_community | 6     |
| `Main → _setup_sensors`              | cross_community | 6     |
| `Main → _validate_data`              | cross_community | 6     |
| `Main → _get_merged_columns`         | cross_community | 6     |
| `Main → _extract_range`              | cross_community | 6     |
| `Main → _check_is_regular_file`      | cross_community | 6     |
| `Main → _find_river_mile_files`      | cross_community | 5     |
| `Main → _create_stateful_col_filter` | cross_community | 5     |
| `Main → _extract_hydro_years`        | cross_community | 5     |
| `Load_all_data → _validate_columns`  | cross_community | 5     |

## How to Explore

1. `context({name: "test_validate_columns_failure"})` — see callers and callees
2. `query({search_query: "data"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings
   (source→sink data flows), when indexed with `--pdg`
