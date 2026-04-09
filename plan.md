1. Add a performance optimization to `utils/processor.py` for `sort_values`.
   - `merged.sort_values` executes an O(N log N) sorting algorithm, which can be computationally expensive on large dataframes.
   - However, time-series data is often already chronologically sorted.
   - By first checking if the data is already sorted in $O(N)$ using the `.is_monotonic_increasing` property, we can entirely skip the $O(N \log N)$ sorting operation when it is not needed.
   - I will modify `utils/processor.py` to check `merged["Time (Minutes)"].is_monotonic_increasing` before calling `merged.sort_values("Time (Minutes)", inplace=True)`.
2. Add a performance optimization to `utils/processor.py` for `.loc` assignments.
   - When using `sensor_keep_arr.all()` or similar methods, the `.loc` operation creates an object internally if missing, or does nothing if not.
   - We will review if De Morgan's optimization is correct, and I will also implement De Morgan's logic from `src/.../processor.py` to `utils/processor.py` or modify the array creations to be optimized.
