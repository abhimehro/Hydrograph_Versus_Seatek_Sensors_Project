import os
import sys
import pandas as pd
import pytest
from unittest.mock import patch

# Constants
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
EXPECTED_COLUMNS = {"Year", "Sensor", "Hydrograph", "Sensor_Value"}

# Ensure the src directory is in the Python path
if not os.path.exists(SRC_DIR):
    raise FileNotFoundError(f"src directory not found at: {SRC_DIR}")
sys.path.insert(0, SRC_DIR)

from visualization.visualization import create_chart
from src import process_data


# Sample data provided as a reusable fixture
@pytest.fixture
def sample_data():
    """Fixture: Provides a sample dataset for testing."""
    data = pd.DataFrame({
        "Time (Seconds)": range(0, 60, 12),  # Example: Timestamp in seconds
        "Hydrograph (Lagged) for Y01": [1, 2, 3, 4, 5],
        "Sensor 1 for Y01": [5, 4, 3, 2, 1],
        "RM": [54.0] * 5,
    })
    # Validate fixture data shape
    assert not data.empty, "Sample data should not be empty"
    return data


# Reusable fixture for creating temporary paths
@pytest.fixture
def temp_dir(tmp_path):
    """
    Fixture: Provides a temporary directory for testing file operations
    and ensures cleanup after tests.
    """
    tmp_path.mkdir(parents=True, exist_ok=True)
    return tmp_path


# Test case for `process_data` with valid dataset
def test_process_data_with_valid_data(sample_data):
    """
    Test the `process_data` function with valid dataset:
    - Check all expected columns exist.
    - Validate year column calculation.
    """
    processed = process_data(sample_data)

    # Assert missing columns
    missing_columns = EXPECTED_COLUMNS - set(processed.columns)
    assert not missing_columns, f"Missing columns in processed data: {missing_columns}"

    # Validate "Year" column transformation
    expected_year = sample_data["Time (Seconds)"] // 12
    year_column_correct = (processed["Year"] == expected_year).all()
    assert year_column_correct, "Year column transformation is incorrect"


# Parameterized Test case for `create_chart`
@pytest.mark.parametrize(
    "rm_value, year",
    [
        (54.0, 1),  # Test case 1: RM is 54, Year is 1
        (45.0, 2),  # Test case 2: RM is 45, Year is 2
    ],
)
def test_create_chart_with_parameters(sample_data, temp_dir, rm_value, year):
    """
    Test `create_chart` function for various `RM` and `Year` combinations.
    - Check output files are created with correct names.
    """
    processed = process_data(sample_data)

    # Create the chart based on RM and Year values
    create_chart(processed, rm_value, year, temp_dir)

    # Check for expected output file
    expected_file = temp_dir / f"RM_{rm_value}_Year_{year}.png"
    assert expected_file.exists(), f"Expected chart file '{expected_file.name}' does not exist"


# Edge case: Testing `process_data` with an empty dataset
def test_process_data_with_empty_data():
    """
    Validate that `process_data` raises an exception when passed an empty dataset.
    """
    empty_data = pd.DataFrame()

    with pytest.raises(ValueError, match="Input data cannot be empty"):  # Assuming `process_data` raises ValueError
        process_data(empty_data)


# Edge case: Testing `process_data` with missing columns
def test_process_data_with_missing_columns():
    """
    Validate that `process_data` raises an exception when required columns are missing.
    """
    invalid_data = pd.DataFrame({"Invalid_Column": [1, 2, 3]})

    with pytest.raises(KeyError, match="Required column 'Time \\(Seconds\\)' missing"):
        process_data(invalid_data)


# Test case for `create_chart` using Mocking
@patch("visualization.visualization.create_chart")
def test_create_chart_with_mock(mock_create_chart, sample_data, temp_dir):
    """
    Test `create_chart` using a mock:
    - Validate that the function is called with expected parameters.
    """
    processed = process_data(sample_data)
    rm_value = 54.0
    year = 1

    # Invoke create_chart with mock
    create_chart(processed, rm_value, year, temp_dir)

    # Assert that the mock method was called with correct arguments
    mock_create_chart.assert_called_once_with(processed, rm_value, year, temp_dir)


# Edge case: Test `create_chart` with invalid RM and Year values
@pytest.mark.parametrize(
    "rm_value, year",
    [
        (-10.0, 1),  # Invalid RM value
        (54.0, -1),  # Invalid Year value
    ],
)
def test_create_chart_with_invalid_parameters(sample_data, temp_dir, rm_value, year):
    """
    Validate that `create_chart` gracefully handles invalid RM or Year values.
    Assume `create_chart` raises ValueError for invalid parameters.
    """
    processed = process_data(sample_data)

    with pytest.raises(ValueError, match="Invalid RM or Year value"):
        create_chart(processed, rm_value, year, temp_dir)