1. **Analyze existing code and tests:**
   - In `src/hydrograph_seatek_analysis/data/processor.py`, `RiverMileData.load_data` reads an Excel file using a dynamically filtered lambda function for `usecols`.
   - `load_data` checks if required columns and sensor columns are present. If sensor columns are missing, it throws a `ValueError("No sensor columns found")`.
   - Later, it calls `self._setup_sensors()`, which is a legacy method kept to ensure no methods are bypassed. `_setup_sensors` does its own check on `self.data.columns` and throws the same `ValueError("No sensor columns found")` if missing.
   - We need to add a test specifically for `_setup_sensors()` error path, or for the whole `load_data` error path if no sensor columns are found. Since `_setup_sensors` doesn't get called if `load_data` fails earlier, maybe directly testing `_setup_sensors()` is better.

Wait, testing `_setup_sensors` directly as a unit test is simple and focused. It hits the exact lines 149-158.

Let me create a patch that adds a test to `tests/test_data_processor.py`.

```python
def test_setup_sensors_error():
    """Test _setup_sensors raises ValueError when no sensor columns are present."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "RM_42.5.xlsx"

        river_mile_data = RiverMileData(temp_path)

        # Manually set data missing any "Sensor_" columns
        river_mile_data.data = pd.DataFrame({
            "Time (Seconds)": [0, 1],
            "Year": [2023, 2023],
            "Hydrograph (Lagged)": [1.0, 2.0]
        })

        with pytest.raises(ValueError, match="No sensor columns found"):
            river_mile_data._setup_sensors()
```

Wait, if I use `_setup_sensors()` alone, that covers the error path of that method, which satisfies "Missing Error Path Test for _setup_sensors". The issue states "Can be tested by inserting malformed columns into the mocked DataFrame loaded by the processor."

Ah, "loaded by the processor" implies we should test `load_data()`.
To bypass the early check in `load_data()`, or to just test the `load_data()` error path itself? The `load_data` error path raises the exact same error: `ValueError("No sensor columns found")`.

Let's test `load_data` directly with `mock.patch('pandas.read_excel')`. But wait, in my previous attempt, it raised `ValueError("No sensor columns found")` from line 118. It never reached `_setup_sensors()` on line 122.
To hit `_setup_sensors()` on line 122, it needs to pass the check on line 118. But how can it pass the check on line 118 ("No sensor columns found") and then fail on line 157 ("No sensor columns found")?
It's impossible. If `self.sensors` has elements, then `self.data.columns` will have `"Sensor_..."` columns, so `_setup_sensors()` will also find them.

So if we want to cover the `_setup_sensors` error path specifically, we MUST test it directly without going through `load_data()`. OR we just test the method directly, which fulfills the requirement!

Wait! Let me read the user prompt carefully.
```python
    def _setup_sensors(self) -> None:
        """Extract sensor columns from the loaded data."""
        if self.data.empty:
            return

        # Identify sensor columns dynamically
        # Usually they are named 'Sensor_1', 'Sensor_2', etc., or '1', '2', etc.
        self.sensors = []
```
The actual code is different. Did they mean I should test this method directly? Yes.
I will write a plan to add the test for `_setup_sensors` error path directly to `tests/test_data_processor.py`. And also a test for `_setup_sensors` with empty DataFrame just in case.

2. **Test strategy:**
- Use `pytest`.
- Add `test_river_mile_data_setup_sensors_error` to `tests/test_data_processor.py`.
- This test constructs a `RiverMileData` instance.
- It injects a `pd.DataFrame` missing `Sensor_...` columns into `self.data`.
- It asserts `pytest.raises(ValueError, match="No sensor columns found")` when calling `_setup_sensors()`.

3. **Verify:**
- Run `python3 -m pytest tests/test_data_processor.py`.
