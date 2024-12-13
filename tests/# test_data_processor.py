import os
import sys
import pandas as pd
import pytest

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from data_processor import process_data
from visualization import create_chart

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "Time (Seconds)": range(0, 60, 12),
        "Hydrograph (Lagged) for Y01": [1, 2, 3, 4, 5],
        "Sensor 1 for Y01": [5, 4, 3, 2, 1],
        "RM": [54.0] * 5,
    })

def test_process_data(sample_data):
    processed = process_data(sample_data)
    assert "Year" in processed.columns, "Expected 'Year' column in processed data"
    assert "Sensor" in processed.columns, "Expected 'Sensor' column in processed data"
    assert "Hydrograph" in processed.columns, "Expected 'Hydrograph' column in processed data"
    assert "Sensor_Value" in processed.columns, "Expected 'Sensor_Value' column in processed data"

def test_create_chart(sample_data, tmp_path):
    processed = process_data(sample_data)
    create_chart(processed, 54.0, 1, tmp_path)
    assert (tmp_path / "RM_54.0_Year_1.png").exists(), "Expected chart file 'RM_54.0_Year_1.png' does not exist"
