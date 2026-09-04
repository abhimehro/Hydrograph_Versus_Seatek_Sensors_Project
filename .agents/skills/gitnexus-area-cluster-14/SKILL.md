---
name: gitnexus-area-cluster-14
description: "Skill for the Cluster_14 area of Hydrograph_Versus_Seatek_Sensors_Project. 6 symbols across 1 files."
---

# Cluster_14

6 symbols | 1 files | Cohesion: 77%

## When to Use

- Understanding how main, parse_args work
- Modifying cluster_14-related functionality

## Key Files

| File               | Symbols                                                                                                                        |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `validate_data.py` | _print_consistency_validation, _print_hydrograph_validation, _print_processed_validation, _print_summary_validation, main (+1) |

## Entry Points

Start here when exploring this area:

- **`main`** (Function) — `validate_data.py:152`
- **`parse_args`** (Function) — `validate_data.py:25`

## Key Symbols

| Symbol                          | Type     | File               | Line |
| ------------------------------- | -------- | ------------------ | ---- |
| `main`                          | Function | `validate_data.py` | 152  |
| `parse_args`                    | Function | `validate_data.py` | 25   |
| `_print_consistency_validation` | Function | `validate_data.py` | 127  |
| `_print_hydrograph_validation`  | Function | `validate_data.py` | 65   |
| `_print_processed_validation`   | Function | `validate_data.py` | 94   |
| `_print_summary_validation`     | Function | `validate_data.py` | 44   |

## Execution Flows

| Flow                                 | Type            | Steps |
| ------------------------------------ | --------------- | ----- |
| `Main → _extract_range`              | cross_community | 6     |
| `Main → _check_is_regular_file`      | cross_community | 6     |
| `Main → _create_stateful_col_filter` | cross_community | 5     |
| `Main → _extract_hydro_years`        | cross_community | 5     |
| `Main → _calculate_missing_values`   | cross_community | 4     |
| `Main → Sanitize_filename`           | cross_community | 3     |

## How to Explore

1. `context({name: "main"})` — see callers and callees
2. `query({search_query: "cluster_14"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings
   (source→sink data flows), when indexed with `--pdg`
