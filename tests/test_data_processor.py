"""Tests for the data processor module."""

import os
import tempfile
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest

from src.hydrograph_seatek_analysis.core.config import Config
from src.hydrograph_seatek_analysis.data.processor import (
    SeatekDataProcessor,
    ProcessingMetrics,
    RiverMileData
)


def test_processing_metrics():
    """Test ProcessingMetrics class."""
    metrics = ProcessingMetrics(
        original_rows=100,
        invalid_rows=10,
        zero_values=5,
        null_values=15,
        valid_rows=70
    )
    
    assert metrics.original_rows == 100
    assert metrics.invalid_rows == 10
    assert metrics.zero_values == 5
    assert metrics.null_values == 15
    assert metrics.valid_rows == 70


def test_river_mile_data_initialization():
    """Test RiverMileData initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "RM_42.5.xlsx"
        
        # Create a mock Excel file
        with mock.patch('pandas.read_excel', return_value=pd.DataFrame()):
            river_mile_data = RiverMileData(temp_path)
            assert river_mile_data.river_mile == 42.5


def test_river_mile_data_extraction():
    """Test river mile extraction from filename."""
    # Test valid filename
    with tempfile.TemporaryDirectory() as temp_dir:
        valid_path = Path(temp_dir) / "RM_42.5.xlsx"
        river_mile_data = RiverMileData(valid_path)
        assert river_mile_data.river_mile == 42.5
    
    # Test invalid filename
    with tempfile.TemporaryDirectory() as temp_dir:
        invalid_path = Path(temp_dir) / "InvalidFile.xlsx"
        with pytest.raises(ValueError):
            RiverMileData(invalid_path)


def test_seatek_data_processor_initialization():
    """Test SeatekDataProcessor initialization."""
    config = Config()
    summary_data = pd.DataFrame({
        'River_Mile': [54.0, 53.0],
        'Y_Offset': [10.5, 11.2],
        'Num_Sensors': [2, 2]
    })
    
    processor = SeatekDataProcessor(
        data_dir=config.processed_dir,
        summary_data=summary_data,
        config=config
    )
    
    assert processor.data_dir == config.processed_dir
    assert processor.config == config
    assert len(processor.offsets) == 2
    assert processor.offsets[54.0] == 10.5
    assert processor.offsets[53.0] == 11.2


def test_convert_to_navd88():
    """Test conversion to NAVD88 elevations."""
    config = Config()
    summary_data = pd.DataFrame({
        'River_Mile': [54.0],
        'Y_Offset': [10.5],
        'Num_Sensors': [2]
    })
    
    test_data = pd.DataFrame({
        'Time (Seconds)': [0, 60, 120],
        'Sensor_1': [5.0, 6.0, 7.0]
    })
    
    processor = SeatekDataProcessor(
        data_dir=config.processed_dir,
        summary_data=summary_data,
        config=config
    )
    
    # Process the data
    processed = processor.convert_to_navd88(test_data, 'Sensor_1', 54.0)
    
    # Check time conversion
    assert 'Time (Minutes)' in processed.columns
    assert processed['Time (Minutes)'].tolist() == [0.0, 1.0, 2.0]
    
    # Check sensor values were transformed
    assert processed['Sensor_1'].tolist() != test_data['Sensor_1'].tolist()
    
    # Ensure Y offset was applied
    constants = config.navd88_constants
    expected_formula = lambda x: -(x + constants.offset_a - constants.offset_b) * constants.scale_factor + 10.5
    
    for i, val in enumerate(test_data['Sensor_1']):
        assert processed['Sensor_1'].iloc[i] == pytest.approx(expected_formula(val))