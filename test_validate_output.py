import sys
from io import StringIO
from unittest import mock

# Mock pandas module before importing validate_data
sys.modules['pandas'] = mock.MagicMock()

from validate_data import main

@mock.patch("src.hydrograph_seatek_analysis.data.validator.DataValidator.run_validation")
def test_cli_output(mock_run_validation):
    mock_run_validation.return_value = {
        "summary": {
            "file": "Data_Summary.xlsx",
            "rows": 1000,
            "columns": ["River_Mile", "Y_Offset", "Num_Sensors"],
            "required_columns_present": True,
            "river_miles": [54.0, 53.0]
        },
        "hydrograph": {
            "file": "Hydrograph_Seatek_Data.xlsx",
            "river_mile_sheets": ["RM_54.0"],
            "sheets": [{
                "name": "RM_54.0",
                "rows": 100000,
                "required_columns_present": True,
                "years": [2021, 2022],
                "time_range": [0, 50000]
            }]
        },
        "processed": [{
            "file": "RM_54.0.xlsx",
            "river_mile": 54.0,
            "rows": 100000,
            "required_columns_present": True,
            "sensor_columns": ["Sensor_1"],
            "year_range": [2021, 2022],
            "time_range": [0, 50000]
        }],
        "river_mile_consistency": {
            "all_summary_rms_processed": False,
            "missing_processed_rms": [53.0],
            "extra_processed_rms": [55.0]
        },
        "overall_valid": True
    }

    # Redirect stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    # Run main with mocked args to avoid parsing real sys.argv
    with mock.patch("sys.argv", ["validate_data.py"]):
        main()

    # Reset stdout
    sys.stdout = sys.__stdout__

    output = captured_output.getvalue()

    # Assertions for formatting changes
    assert "River miles: 54.0, 53.0" in output
    assert "Years: 2021, 2022" in output
    assert "Time range: 0 to 50,000" in output
    assert "Year range: 2021 to 2022" in output
    assert "Missing processed data for river miles: 53.0" in output
    assert "Extra processed data for river miles: 55.0" in output
    print("All tests passed!")

if __name__ == "__main__":
    test_cli_output()
