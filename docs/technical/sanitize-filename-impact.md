# `sanitize_filename` upstream impact analysis

Impact command used:

```text
node .gitnexus/run.cjs impact "sanitize_filename" --direction upstream --repo .
```

Assessed upstream call sites:

- `src/hydrograph_seatek_analysis/app.py`: sanitizes year, sensor, and river-mile values before constructing output paths.
- `src/hydrograph_seatek_analysis/core/logger.py`: sanitizes log filenames before creating log paths.

The ASCII normalization is appropriate for both path-producing consumers; no caller relies on preserving non-ASCII filename characters.
