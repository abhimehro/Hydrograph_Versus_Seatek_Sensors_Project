---
name: gitnexus-area-visualization
description: "Skill for the Visualization area of Hydrograph_Versus_Seatek_Sensors_Project. 12 symbols across 1 files."
---

# Visualization

12 symbols | 1 files | Cohesion: 87%

## When to Use

- Working with code in `src/`
- Understanding how create_chart work
- Modifying visualization-related functionality

## Key Files

| File                                                              | Symbols                                                                                                |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | _add_hydrograph, _add_sensor_data, _configure_primary_axis, _format_hydrograph_axis, create_chart (+7) |

## Entry Points

Start here when exploring this area:

- **`create_chart`** (Method) —
  `src/hydrograph_seatek_analysis/visualization/chart_generator.py:141`

## Key Symbols

| Symbol                    | Type   | File                                                              | Line |
| ------------------------- | ------ | ----------------------------------------------------------------- | ---- |
| `create_chart`            | Method | `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | 141  |
| `_add_hydrograph`         | Method | `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | 262  |
| `_add_sensor_data`        | Method | `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | 219  |
| `_configure_primary_axis` | Method | `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | 130  |
| `_format_hydrograph_axis` | Method | `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | 243  |
| `_calculate_metrics`      | Method | `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | 121  |
| `_update_counts`          | Method | `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | 78   |
| `_update_hydro_metrics`   | Method | `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | 112  |
| `_update_sensor_metrics`  | Method | `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | 101  |
| `_update_time_metrics`    | Method | `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | 92   |
| `__init__`                | Method | `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | 42   |
| `_setup_style`            | Method | `src/hydrograph_seatek_analysis/visualization/chart_generator.py` | 53   |

## Execution Flows

| Flow                                     | Type            | Steps |
| ---------------------------------------- | --------------- | ----- |
| `Process_data → _format_hydrograph_axis` | cross_community | 4     |
| `Process_data → _update_counts`          | cross_community | 4     |
| `Process_data → _update_hydro_metrics`   | cross_community | 4     |
| `Process_data → _update_sensor_metrics`  | cross_community | 4     |
| `Process_data → _update_time_metrics`    | cross_community | 4     |
| `Process_data → _add_sensor_data`        | cross_community | 3     |
| `Process_data → _configure_primary_axis` | cross_community | 3     |

## How to Explore

1. `context({name: "create_chart"})` — see callers and callees
2. `query({search_query: "visualization"})` — find related execution flows
3. Read key files listed above for implementation details
4. `explain({target: "<file or symbol>"})` — persisted taint findings
   (source→sink data flows), when indexed with `--pdg`
