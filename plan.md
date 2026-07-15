1. **Optimize max fractional deviation calculation in `chart_generator.py`**
   - Replace the intermediate pandas object allocation when calculating max fractional deviation of hydrograph values.
   - We will write a python script to read `src/hydrograph_seatek_analysis/visualization/chart_generator.py` and replace `max_frac_deviation = (hydro_values - hydro_values.round()).abs().max()` with `hydro_vals_arr = hydro_values.values; max_frac_deviation = np.nanmax(np.abs(hydro_vals_arr - np.round(hydro_vals_arr)))`
   - We will add `# ⚡ Bolt Optimization: Replace pandas max/round overhead with numpy equivalents` comment.
   - Verify changes using `git diff`.
2. **Optimize `missing_values.to_dict()` in `validator.py`**
   - The method `to_dict()` on Pandas Series creates intermediate index/dataframe representations.
   - We will run `sed -i 's/"missing_values": missing_values.to_dict()/"missing_values": dict(missing_values)  # ⚡ Bolt Optimization: Avoid Series.to_dict() overhead/' src/hydrograph_seatek_analysis/data/validator.py` to optimize this.
   - Verify changes using `git diff`.
3. **Verify testing**
   - Run `python3 -m pytest tests/` to verify tests pass.
4. **Run Pre-Commit Checks**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
5. **Submit PR**
   - Submit the PR with the performance improvements.
