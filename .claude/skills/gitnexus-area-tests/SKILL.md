---
name: gitnexus-area-tests
description: "Skill for the Tests area of Hydrograph_Versus_Seatek_Sensors_Project. 78 symbols across 15 files."
---

# Tests

78 symbols | 15 files | Cohesion: 80%

## When to Use

- Working with code in `tests/`
- Understanding how main, test_convert_to_navd88, expected_formula work
- Modifying tests-related functionality

## Key Files

| File                                                 | Symbols                                                                                                                                                                                                                                                |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `tests/test_app.py`                                  | test_main_data_dir, test_main_exception, test_main_failure, test_main_help_exits_zero, test_main_success (+10)                                                                                                                                         |
| `tests/test_data_loader.py`                          | test_load_hydro_data_exception, test_load_hydro_data_skips_invalid_sheet_value_error, test_validate_columns_failure, test_validate_columns_success, test_get_available_river_miles (+6)                                                                |
| `tests/test_validator.py`                            | test_run_validation_failure, test_run_validation_inconsistent, test_run_validation_success, test_validate_hydro_file, test_validate_hydro_file_missing_columns (+3)                                                                                    |
| `tests/test_sanitize_filename.py`                    | test_sanitize_filename_allows_normal_chars, test_sanitize_filename_handles_numbers, test_sanitize_filename_limits_length, test_sanitize_filename_removes_path_traversal, test_sanitize_filename_replaces_invalid_chars (+1)                            |
| `src/hydrograph_seatek_analysis/data/validator.py`   | run_validation, validate_hydro_file, validate_processed_files, _calculate_missing_values, validate_summary_file                                                                                                                                        |
| `src/hydrograph_seatek_analysis/data/data_loader.py` | _load_hydro_data, _validate_columns, get_available_river_miles, _load_summary_data, load_all_data                                                                                                                                                      |
| `tests/test_refactoring_agent_workflow.py`           | load_workflow, test_prepare_command_extracts_first_cs_agent_line_from_multiline_comment, test_prepare_command_fails_when_no_cs_agent_line_present, test_refactoring_agent_enforces_concurrency_per_pr, test_refactoring_agent_retries_failed_push_once |
| `src/hydrograph_seatek_analysis/app.py`              | _build_parser, _package_version, main, process_data                                                                                                                                                                                                    |
| `tests/test_data_processor.py`                       | test_convert_to_navd88, expected_formula, test_process_data_internal_error, test_process_data_missing_river_mile                                                                                                                                       |
| `src/hydrograph_seatek_analysis/data/processor.py`   | _compute_validity_masks, _extract_year_data, convert_to_navd88, process_data                                                                                                                                                                           |

## Entry Points

Start here when exploring this area:

- **`main`** (Function) — `src/hydrograph_seatek_analysis/app.py:286`
- **`test_convert_to_navd88`** (Function) — `tests/test_data_processor.py:74`
- **`expected_formula`** (Function) — `tests/test_data_processor.py:102`
- **`test_process_data_internal_error`** (Function) —
  `tests/test_data_processor.py:146`
- **`test_process_data_missing_river_mile`** (Function) —
  `tests/test_data_processor.py:132`

## Key Symbols

| Symbol                                                | Type     | File                                               | Line |
| ----------------------------------------------------- | -------- | -------------------------------------------------- | ---- |
| `main`                                                | Function | `src/hydrograph_seatek_analysis/app.py`            | 286  |
| `test_convert_to_navd88`                              | Function | `tests/test_data_processor.py`                     | 74   |
| `expected_formula`                                    | Function | `tests/test_data_processor.py`                     | 102  |
| `test_process_data_internal_error`                    | Function | `tests/test_data_processor.py`                     | 146  |
| `test_process_data_missing_river_mile`                | Function | `tests/test_data_processor.py`                     | 132  |
| `sanitize_filename`                                   | Function | `src/hydrograph_seatek_analysis/utils/security.py` | 54   |
| `test_sanitize_filename_allows_normal_chars`          | Function | `tests/test_sanitize_filename.py`                  | 14   |
| `test_sanitize_filename_handles_numbers`              | Function | `tests/test_sanitize_filename.py`                  | 21   |
| `test_sanitize_filename_limits_length`                | Function | `tests/test_sanitize_filename.py`                  | 40   |
| `test_sanitize_filename_removes_path_traversal`       | Function | `tests/test_sanitize_filename.py`                  | 5    |
| `test_sanitize_filename_replaces_invalid_chars`       | Function | `tests/test_sanitize_filename.py`                  | 34   |
| `test_sanitize_filename_strips_leading_trailing_dots` | Function | `tests/test_sanitize_filename.py`                  | 27   |
| `test_run_validation_failure`                         | Function | `tests/test_validator.py`                          | 276  |
| `test_run_validation_inconsistent`                    | Function | `tests/test_validator.py`                          | 256  |
| `test_run_validation_success`                         | Function | `tests/test_validator.py`                          | 232  |
| `test_validate_hydro_file`                            | Function | `tests/test_validator.py`                          | 90   |
| `test_validate_hydro_file_missing_columns`            | Function | `tests/test_validator.py`                          | 143  |
| `configure_root_logger`                               | Function | `src/hydrograph_seatek_analysis/core/logger.py`    | 103  |
| `setup_logger`                                        | Function | `src/hydrograph_seatek_analysis/core/logger.py`    | 29   |
| `test_configure_root_logger`                          | Function | `tests/test_logger.py`                             | 44   |

## Execution Flows

| Flow                             | Type            | Steps |
| -------------------------------- | --------------- | ----- |
| `Main → _check_is_regular_file`  | cross_community | 7     |
| `Main → _validate_columns`       | cross_community | 6     |
| `Main → _setup_sensors`          | cross_community | 6     |
| `Main → _validate_data`          | cross_community | 6     |
| `Main → _extract_range`          | cross_community | 6     |
| `Main → _check_is_regular_file`  | cross_community | 6     |
| `Main → _find_river_mile_files`  | cross_community | 5     |
| `Main → _compute_validity_masks` | cross_community | 5     |
| `Main → _extract_year_data`      | cross_community | 5     |
| `Main → Convert_to_navd88`       | cross_community | 5     |

## How to Explore

1. `context({name: "main"})` — see callers and callees
2. `query({search_query: "tests"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings
   (source→sink data flows), when indexed with `--pdg`
