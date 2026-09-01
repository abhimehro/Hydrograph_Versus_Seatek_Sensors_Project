# Hydrograph–Seatek correlation notes

This file previously held a corrupted paste of exploratory Python (broken
imports, invalid identifiers such as `calculate*pearson`). That dump was not
part of the maintained processor.

**Current visualization path:**
`src/hydrograph_seatek_analysis/visualization/chart_generator.py`
(`ChartGenerator`). Charts overlay Seatek sensor series against
`Hydrograph (Lagged)` via matplotlib/seaborn.

Pearson-style correlation of hydrograph vs Seatek readings is **not** a
processor output today. If you need that analysis, add it next to
`ChartGenerator` rather than restoring the old dump.

Related runtime entry: `src/hydrograph_seatek_analysis/app.py`.
