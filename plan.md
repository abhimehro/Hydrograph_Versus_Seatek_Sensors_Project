1. **Optimize DataFrame subsetting in Processor**
   - In `src/hydrograph_seatek_analysis/data/processor.py` and `utils/processor.py`, when extracting `year_data` from `cached_year_data`, replace `year_data = cached_year_data[cols].copy()` with `year_data = cached_year_data.loc[:, cols].copy()` or explicitly extract columns before `.copy()`. Note: I am currently observing the optimization strategy that requires extracting a subset of data explicitly before calling copy (`cols = ['Time', sensor]; processed = df[cols].copy()`). Wait, the codebase currently already has:
   ```python
   cols = ['Time (Seconds)', sensor]
   if 'Hydrograph (Lagged)' in cached_year_data.columns:
       cols.append('Hydrograph (Lagged)')
   year_data = cached_year_data[cols].copy()
   ```
   So this is already implemented!

2. **Wait, let's look closely at `hydrograph_seatek_analysis/data/processor.py` for other optimizations.**
   Wait, is `usecols` parameter a list or a function in `DataValidator`?
   In `src/hydrograph_seatek_analysis/data/data_loader.py` and `utils/data_loader.py`, `required_cols` is defined as a `set`. `seen_cols` is a `list`.
   ```python
   seen_cols = []
   def filter_cols(col):
       seen_cols.append(col)
       return col in required_cols
   ```
   Wait, checking `col in required_cols` against a set is O(1).
