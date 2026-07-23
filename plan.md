1. **Optimize Dictionary Creation in `validate_summary_file`**
   - The current implementation in `src/hydrograph_seatek_analysis/data/validator.py` calls `missing_values = self._calculate_missing_values(df, required_cols)` which returns a Pandas Series.
   - It then checks `if missing_values.any():` and later converts the Series back to a dictionary with `dict(missing_values)` under the `missing_values` key in the return dictionary.
   - Based on `.jules/bolt.md`, creating a Pandas Series introduces overhead and memory allocation. We can avoid `pd.Series` instantiation by directly returning a standard python dictionary in `_calculate_missing_values` and checking values using Python native logic (`any(v > 0 for v in dict.values())`).
   - Action: Modify `_calculate_missing_values` in `src/hydrograph_seatek_analysis/data/validator.py` to return a `dict` instead of a `pd.Series`.
   - Update `validate_summary_file` to handle `missing_values` as a dictionary, checking `any(val > 0 for val in missing_values.values())` and simply assigning `missing_values: missing_values` rather than `dict(missing_values)`.

2. **Complete Pre-Commit Steps**
   - Run `pre_commit_instructions` tool and complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

3. **Submit PR**
   - Use `request_code_review` if needed and submit with an appropriate Bolt PR title.
