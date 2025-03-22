"""Tests for the data loader module."""

import os
import tempfile
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest

from src.hydrograph_seatek_analysis.core.config import Config
from src.hydrograph_seatek_analysis.data.data_loader import DataLoader


def test_data_loader_initialization():
    """Test DataLoader initialization."""
    config = Config()
    data_loader = DataLoader(config)
    assert data_loader.config == config


def test_validate_columns_success():
    """Test _validate_columns with valid columns."""
    data_loader = DataLoader(Config())
    df = pd.DataFrame(columns=['Time (Seconds)', 'Year', 'Value'])
    
    # Should not raise an exception
    data_loader._validate_columns(df, ['Time (Seconds)', 'Year'], "test")


def test_validate_columns_failure():
    """Test _validate_columns with missing columns."""
    data_loader = DataLoader(Config())
    df = pd.DataFrame(columns=['Time (Seconds)', 'Value'])
    
    with pytest.raises(ValueError) as exc_info:
        data_loader._validate_columns(df, ['Time (Seconds)', 'Year'], "test")
    
    assert "Missing required columns in test" in str(exc_info.value)
    assert "Year" in str(exc_info.value)


def test_get_available_river_miles():
    """Test get_available_river_miles function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create mock river mile files
        (temp_path / "RM_54.0.xlsx").touch()
        (temp_path / "RM_53.0.xlsx").touch()
        (temp_path / "OtherFile.xlsx").touch()  # Should be ignored
        
        result = DataLoader.get_available_river_miles(temp_path)
        assert result == [53.0, 54.0]  # Should be sorted


def test_get_available_river_miles_empty():
    """Test get_available_river_miles with no files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        result = DataLoader.get_available_river_miles(temp_path)
        assert result == []


@mock.patch('pandas.read_excel')
def test_load_summary_data(mock_read_excel):
    """Test _load_summary_data with mocked Excel file."""
    mock_df = pd.DataFrame({
        'River_Mile': [54.0, 53.0],
        'Y_Offset': [10.5, 11.2],
        'Num_Sensors': [2, 2]
    })
    mock_read_excel.return_value = mock_df
    
    config = Config()
    data_loader = DataLoader(config)
    
    # Mock exists check to avoid file not found error
    with mock.patch.object(Path, 'exists', return_value=True):
        result = data_loader._load_summary_data()
    
    assert result.equals(mock_df)
    mock_read_excel.assert_called_once_with(config.summary_file)