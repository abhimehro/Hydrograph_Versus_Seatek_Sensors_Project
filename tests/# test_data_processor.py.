# tests/test_data_processor.py

import os
import sys

import pandas as pd
import pytest

# Ensure the scripts directory is in the Python path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
)

try:
    try:
        from scripts.data_processor import process_data
    except ImportError:
        raise ImportError(
            "Ensure that 'data_processor.py' exists in the 'scripts' directory and the path is correctly added to sys.path."
        ) from None
except ImportError:
    raise ImportError(
        "Ensure that 'data_processor.py' exists in the 'scripts' directory and the path is correctly added to sys.path."
    ) from None
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
)
try:
    from scripts.visualizer import create_chart
except ImportError:
    raise ImportError(
        "Ensure that 'visualizer.py' exists in the 'scripts' directory and the path is correctly added to sys.path."
    ) from None


@pytest.fixture
def sample_data():
    return pd.DataFrame(
        {
            "Time (Seconds)": range(0, 60, 12),
            "Hydrograph (Lagged) for Y01": [1, 2, 3, 4, 5],
            "Sensor 1 for Y01": [5, 4, 3, 2, 1],
            "RM": [54.0] * 5,
        }
    )


def test_process_data(sample_data):
    processed = process_data(sample_data)
    if "Year" not in processed.columns:
        raise AssertionError("Expected 'Year' column in processed data")
    if "Sensor" not in processed.columns:
        raise AssertionError("Expected 'Sensor' column in processed data")
    if "Hydrograph" not in processed.columns:
        raise AssertionError("Expected 'Hydrograph' column in processed data")
    if "Sensor_Value" not in processed.columns:
        raise AssertionError("Expected 'Sensor_Value' column in processed data")


def test_create_chart(sample_data, tmp_path):
    processed = process_data(sample_data)
    create_chart(processed, 54.0, 1, tmp_path)
    if not (tmp_path / "RM_54.0_Year_1.png").exists():
        raise AssertionError("Expected chart file 'RM_54.0_Year_1.png' does not exist")
