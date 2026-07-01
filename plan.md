1. **Optimize `_process_year_data` in `tests/data_processing/__init__.py`**
   - In `tests/data_processing/__init__.py` line ~197, we currently have:
     ```python
     valid_data = year_data[
         year_data[sensor].notna()
         & (year_data[sensor] > 0)
         & (year_data[sensor] != float("inf"))
     ]
     ```
   - According to the instructions `Performance optimization in Pandas: When applying multiple boolean filters to isolate strictly positive, finite numbers, the condition data > 0 naturally evaluates to False for NaN, 0, and negative values (including -inf). Redundant checks like .notna(), != 0, or != float('-inf') should be removed to prevent allocating unnecessary intermediate boolean Pandas Series, simplifying the filter to (data > 0) & (data < float('inf')).`
   - We will replace it with:
     ```python
     valid_data = year_data[
         (year_data[sensor] > 0) & (year_data[sensor] < float("inf"))
     ]
     ```
2. **Review other instances of `notna()` in the codebase**
   - The other usages in `validator.py` and `chart_generator.py` are already using the `isna().all()` optimization or extracting `pd.notna(years)`, which are okay.

3. **Complete pre-commit steps**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

4. **Submit the change**
   - Submit the PR with the required Bolt PR format.
