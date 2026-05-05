1.  **Refactor `df['col'].notna().any()` checks**: Replace `not df['col'].notna().any()` with `df['col'].isna().all()` for performance. This is faster because it avoids intermediate `notna` series and `any` calls.
    *   I will use `run_in_bash_session` to run a python script that will use `str.replace` to replace the lines in `src/hydrograph_seatek_analysis/data/validator.py`: lines 120, 128.
2.  **Refactor `len(df['col']) > 0` checks**: Replace `len(df['col']) > 0` with `len(df) > 0` for performance. This avoids series creation overhead and column retrieval overhead.
    *   I will use `run_in_bash_session` to run a python script that will use `str.replace` to replace the lines in `src/hydrograph_seatek_analysis/visualization/chart_generator.py`: lines 111, 115, 121.
3.  **Run tests**: Run the test suite using `run_in_bash_session` with `python3 -m pytest tests/` to ensure no functionality is broken.
4.  **Complete pre-commit steps**: Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
5.  **Submit the change**: Create a PR titled "⚡ Bolt: [performance improvement]" with the required description format using `run_in_bash_session` with explicit `git` and `gh pr create` commands. The description should have the following sections:
    *   💡 What: Refactored DataFrame empty checks.
    *   🎯 Why: To improve performance.
    *   📊 Impact: Reduces overhead.
    *   🔬 Measurement: Can be verified with microbenchmarks.
