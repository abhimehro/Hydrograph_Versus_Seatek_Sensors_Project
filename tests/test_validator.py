"""Tests for the data validator module."""

import tempfile
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest

from src.hydrograph_seatek_analysis.core.config import Config
from src.hydrograph_seatek_analysis.data.validator import DataValidator


def test_validator_initialization():
    """Test DataValidator initialization."""
    config = Config()
    validator = DataValidator(config)
    assert validator.config == config


@mock.patch('pandas.read_excel')
def test_validate_summary_file(mock_read_excel):
    """Test validate_summary_file with mocked Excel file."""
    mock_df = pd.DataFrame({
        'River_Mile': [54.0, 53.0],
        'Y_Offset': [10.5, 11.2],
        'Num_Sensors': [2, 2]
    })
    mock_read_excel.return_value = mock_df
    
    config = Config()
    validator = DataValidator(config)
    
    # Mock exists check to avoid file not found error
    with mock.patch.object(Path, 'exists', return_value=True):
        result = validator.validate_summary_file()
    
    assert result is not None
    assert result['file'] == config.summary_file.name
    assert result['rows'] == 2
    assert 'River_Mile' in result['columns']
    assert result['required_columns_present'] is True
    assert result['river_miles'] == [54.0, 53.0]


@mock.patch('pandas.read_excel')
def test_validate_summary_file_missing_columns(mock_read_excel):
    """Test validate_summary_file with missing columns."""
    mock_df = pd.DataFrame({
        'River_Mile': [54.0, 53.0],
        # Missing Y_Offset and Num_Sensors
    })
    mock_read_excel.return_value = mock_df
    
    config = Config()
    validator = DataValidator(config)
    
    # For missing columns, the validator returns None
    # Mock exists check to avoid file not found error
    with mock.patch.object(Path, 'exists', return_value=True):
        result = validator.validate_summary_file()
    
    assert result is None


@mock.patch('pandas.ExcelFile')
@mock.patch('pandas.read_excel')
def test_validate_hydro_file(mock_read_excel, mock_excel_file_cls):
    """Test validate_hydro_file with mocked Excel file."""
    # Create mock ExcelFile instance
    mock_excel_file = mock.MagicMock()
    mock_excel_file.sheet_names = ['RM_54.0', 'RM_53.0', 'OtherSheet']
    mock_excel_file_cls.return_value.__enter__.return_value = mock_excel_file
    
    # Mock read_excel return values
    df_54 = pd.DataFrame({
        'Time (Seconds)': [0, 60, 120],
        'Year': [1, 1, 1]
    })
    df_53 = pd.DataFrame({
        'Time (Seconds)': [0, 60, 120],
        'Year': [1, 1, 1]
    })
    
    # Configure mock to return different values based on sheet name
    mock_read_excel.side_effect = lambda *args, **kwargs: (
        df_54 if kwargs.get('sheet_name') == 'RM_54.0' else 
        df_53 if kwargs.get('sheet_name') == 'RM_53.0' else 
        pd.DataFrame()
    )
    
    config = Config()
    validator = DataValidator(config)
    
    # Mock exists check to avoid file not found error
    with mock.patch.object(Path, 'exists', return_value=True):
        result = validator.validate_hydro_file()
    
    assert result is not None
    assert result['file'] == config.hydro_file.name
    assert len(result['sheets']) == 2  # Only RM_ sheets are processed
    assert result['river_mile_sheets'] == ['RM_54.0', 'RM_53.0']
    
    # Check sheet details
    sheet1 = next(s for s in result['sheets'] if s['name'] == 'RM_54.0')
    assert sheet1['rows'] == 3
    assert sheet1['required_columns_present'] is True
    assert sheet1['years'] == [1]
    assert sheet1['time_range'] == [0, 120]