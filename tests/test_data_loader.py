"""Tests for the data loader module."""

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
    df = pd.DataFrame(columns=["Time (Seconds)", "Year", "Value"])

    # Should not raise an exception
    data_loader._validate_columns(df, ["Time (Seconds)", "Year"], "test")


def test_validate_columns_failure():
    """Test _validate_columns with missing columns."""
    data_loader = DataLoader(Config())
    df = pd.DataFrame(columns=["Time (Seconds)", "Value"])

    with pytest.raises(ValueError) as exc_info:
        data_loader._validate_columns(df, ["Time (Seconds)", "Year"], "test")

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


@mock.patch.object(Path, "is_symlink", return_value=False)
@mock.patch("pandas.read_excel")
def test_load_summary_data(mock_read_excel, mock_is_symlink):
    """Test _load_summary_data with mocked Excel file."""
    mock_df = pd.DataFrame(
        {"River_Mile": [54.0, 53.0], "Y_Offset": [10.5, 11.2], "Num_Sensors": [2, 2]}
    )

    def mock_read_excel_func(*args, **kwargs):
        usecols = kwargs.get("usecols")
        if callable(usecols):
            selected_cols = [col for col in mock_df.columns if usecols(col)]
            return mock_df[selected_cols]
        return mock_df

    mock_read_excel.side_effect = mock_read_excel_func

    config = Config()
    data_loader = DataLoader(config)

    # Mock exists check to avoid file not found error
    with mock.patch.object(Path, "exists", return_value=True):
        with mock.patch.object(Path, "stat") as mock_stat:
            mock_stat.return_value.st_size = 1000
            result = data_loader._load_summary_data()

    assert result.equals(mock_df)
    mock_read_excel.assert_called_once()
    args, kwargs = mock_read_excel.call_args
    assert args[0] == config.summary_file
    assert callable(kwargs.get("usecols"))


@mock.patch("pandas.ExcelFile")
@mock.patch.object(Path, "is_symlink", return_value=False)
@mock.patch("pandas.read_excel")
def test_load_hydro_data_skips_invalid_sheet_value_error(
    mock_read_excel, mock_is_symlink, mock_excel_file_cls, caplog
):
    """Test _load_hydro_data skips sheets that raise a parsing ValueError."""
    mock_excel_file = mock.MagicMock()
    mock_excel_file.sheet_names = ["RM_invalid", "RM_54.0"]
    mock_excel_file_cls.return_value = mock_excel_file

    valid_df = pd.DataFrame(
        {
            "Time (Seconds)": [0, 60, 120],
            "Year": [1, 1, 1],
            "Sensor_1": [1.0, 2.0, 3.0],
            "Hydrograph (Lagged)": [0.1, 0.2, 0.3],
        }
    )

    def mock_read_excel_func(*args, **kwargs):
        sheet_name = kwargs.get("sheet_name")
        if sheet_name == "RM_invalid":
            raise ValueError("No columns to parse from file")

        usecols = kwargs.get("usecols")
        if callable(usecols):
            selected_cols = [col for col in valid_df.columns if usecols(col)]
            return valid_df[selected_cols]
        return valid_df

    mock_read_excel.side_effect = mock_read_excel_func

    config = Config()
    data_loader = DataLoader(config)

    with mock.patch.object(Path, "exists", return_value=True):
        with mock.patch.object(Path, "stat") as mock_stat:
            mock_stat.return_value.st_size = 1000
            result = data_loader._load_hydro_data()

    expected_df = valid_df[
        ["Time (Seconds)", "Year", "Sensor_1", "Hydrograph (Lagged)"]
    ]
    assert list(result) == ["RM_54.0"]
    assert result["RM_54.0"].equals(expected_df)
    assert list(result["RM_54.0"].columns) == list(expected_df.columns)
    assert "Skipping sheet RM_invalid: No columns to parse from file" in caplog.text


@mock.patch.object(DataLoader, "_load_hydro_data")
@mock.patch.object(DataLoader, "_load_summary_data")
def test_load_all_data_success(mock_load_summary, mock_load_hydro):
    """Test successful loading of all data."""
    config = Config()
    data_loader = DataLoader(config)

    mock_summary_df = pd.DataFrame({"River_Mile": [54.0]})
    mock_hydro_dict = {"RM_54.0": pd.DataFrame({"Time (Seconds)": [0]})}

    mock_load_summary.return_value = mock_summary_df
    mock_load_hydro.return_value = mock_hydro_dict

    summary_data, hydro_data = data_loader.load_all_data()

    assert summary_data.equals(mock_summary_df)
    assert set(hydro_data.keys()) == set(mock_hydro_dict.keys())
    for key in hydro_data:
        assert hydro_data[key].equals(mock_hydro_dict[key])
    mock_load_summary.assert_called_once()
    mock_load_hydro.assert_called_once()


@mock.patch.object(DataLoader, "_load_hydro_data")
@mock.patch.object(DataLoader, "_load_summary_data")
def test_load_all_data_exception(mock_load_summary, mock_load_hydro):
    """Test exception handling during load_all_data."""
    config = Config()
    data_loader = DataLoader(config)

    mock_load_summary.side_effect = RuntimeError("Test summary error")

    with pytest.raises(RuntimeError, match="Test summary error"):
        data_loader.load_all_data()

    mock_load_summary.assert_called_once()
    mock_load_hydro.assert_not_called()
