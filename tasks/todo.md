# ChartGenerator.create_chart Tests

- [x] Add pytest fixture for `ChartGenerator` and `Config` setup
- [x] Add pytest fixture for `sample_data` (happy path with both Seatek sensor and Hydrograph data)
- [x] Add test `test_create_chart_success` checking `Figure` & `ChartMetrics` types and values
- [x] Add test `test_create_chart_no_hydrograph` checking correct generation when hydrograph column is absent
- [x] Add test `test_create_chart_empty_data` checking handling of empty DataFrame inputs
- [x] Add test `test_create_chart_missing_columns` checking response when required columns are entirely missing
- [x] Add test `test_create_chart_exception_handling` validating try-except block by mocking `plt.subplots`
- [x] Fix module structure (remove old test `test_visualization.py` which had undefined import `DataVisualizationError`)
- [ ] Run pre-commit checks
- [ ] Submit PR
