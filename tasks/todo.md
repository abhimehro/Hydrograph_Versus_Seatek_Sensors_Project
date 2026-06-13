# TODO

[x] Reproduce CodeScene code duplication failure in CI
[x] Identify tests duplicating mock setup.
[x] Refactor duplicated setup into `_setup_mock_processor` helper in `tests/test_app.py`
[x] Replace mock assignments with `_setup_mock_processor` method.
[x] Consolidate repetitive process_data mocks into helper as well (if practical, yes it was).
[x] Realize PropertyMock issue and replace outer exception triggering with `del app.processor.river_mile_data` for a generic Mock instead.
[x] Run tests.
[x] Create learning entry.
