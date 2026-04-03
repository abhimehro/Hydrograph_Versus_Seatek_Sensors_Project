"""Tests for the data validator module."""

from pathlib import Path
from unittest import mock

import pandas as pd

from src.hydrograph_seatek_analysis.core.config import Config
from src.hydrograph_seatek_analysis.data.validator import DataValidator


def test_validator_initialization():
    """Test DataValidator initialization."""
    config = Config()
    validator = DataValidator(config)
    assert validator.config == config


@mock.patch("pandas.read_excel")
def test_validate_summary_file(mock_read_excel):
    """Test validate_summary_file with mocked Excel file."""
    mock_df = pd.DataFrame(
        {"River_Mile": [54.0, 53.0], "Y_Offset": [10.5, 11.2], "Num_Sensors": [2, 2]}
    )

    def mock_read_excel_func(*args, **kwargs):
        usecols = kwargs.get("usecols")
        if callable(usecols):
            for col in mock_df.columns:
                usecols(col)
        return mock_df

    mock_read_excel.side_effect = mock_read_excel_func

    config = Config()
    validator = DataValidator(config)

    # Mock exists check to avoid file not found error
    with (
        mock.patch.object(Path, "exists", return_value=True),
        mock.patch.object(Path, "stat", return_value=mock.Mock(st_size=1000)),
    ):
        result = validator.validate_summary_file()

    assert result is not None
    assert result["file"] == config.summary_file.name
    assert result["rows"] == 2
    assert "River_Mile" in result["columns"]
    assert result["required_columns_present"] is True
    assert result["river_miles"] == [54.0, 53.0]


@mock.patch("pandas.read_excel")
def test_validate_summary_file_missing_columns(mock_read_excel):
    """Test validate_summary_file with missing columns."""
    mock_df = pd.DataFrame(
        {
            "River_Mile": [54.0, 53.0],
            # Missing Y_Offset and Num_Sensors
        }
    )

    def mock_read_excel_func(*args, **kwargs):
        usecols = kwargs.get("usecols")
        if callable(usecols):
            for col in mock_df.columns:
                usecols(col)
        return mock_df

    mock_read_excel.side_effect = mock_read_excel_func

    config = Config()
    validator = DataValidator(config)

    # For missing columns, the validator returns None
    # Mock exists check to avoid file not found error
    with (
        mock.patch.object(Path, "exists", return_value=True),
        mock.patch.object(Path, "stat", return_value=mock.Mock(st_size=1000)),
    ):
        result = validator.validate_summary_file()

    assert result is None


@mock.patch("pandas.ExcelFile")
@mock.patch("pandas.read_excel")
def test_validate_hydro_file(mock_read_excel, mock_excel_file_cls):
    """Test validate_hydro_file with mocked Excel file."""
    # Create mock ExcelFile instance
    mock_excel_file = mock.MagicMock()
    mock_excel_file.sheet_names = ["RM_54.0", "RM_53.0", "OtherSheet"]
    mock_excel_file_cls.return_value.__enter__.return_value = mock_excel_file

    # Mock read_excel return values
    df_54 = pd.DataFrame({"Time (Seconds)": [0, 60, 120], "Year": [1, 1, 1]})
    df_53 = pd.DataFrame({"Time (Seconds)": [0, 60, 120], "Year": [1, 1, 1]})

    # Configure mock to return different values based on sheet name
    def mock_read_excel_hydro(*args, **kwargs):
        sheet = kwargs.get("sheet_name")
        df = (
            df_54
            if sheet == "RM_54.0"
            else df_53 if sheet == "RM_53.0" else pd.DataFrame()
        )
        usecols = kwargs.get("usecols")
        if callable(usecols):
            for col in df.columns:
                usecols(col)
        return df

    mock_read_excel.side_effect = mock_read_excel_hydro

    config = Config()
    validator = DataValidator(config)

    # Mock exists check to avoid file not found error
    with (
        mock.patch.object(Path, "exists", return_value=True),
        mock.patch.object(Path, "stat", return_value=mock.Mock(st_size=1000)),
    ):
        result = validator.validate_hydro_file()

    assert result is not None
    assert result["file"] == config.hydro_file.name
    assert len(result["sheets"]) == 2  # Only RM_ sheets are processed
    assert result["river_mile_sheets"] == ["RM_54.0", "RM_53.0"]

    # Check sheet details
    sheet1 = next(s for s in result["sheets"] if s["name"] == "RM_54.0")
    assert sheet1["rows"] == 3
    assert sheet1["required_columns_present"] is True
    assert sheet1["years"] == [1]
    assert sheet1["time_range"] == [0, 120]


@mock.patch("pandas.ExcelFile")
@mock.patch("pandas.read_excel")
def test_validate_hydro_file_missing_columns(mock_read_excel, mock_excel_file_cls):
    """Test validate_hydro_file behavior when required columns are absent."""
    mock_excel_file = mock.MagicMock()
    mock_excel_file.sheet_names = ["RM_54.0"]
    mock_excel_file_cls.return_value.__enter__.return_value = mock_excel_file

    # Missing 'Time (Seconds)' and 'Year'
    df_missing = pd.DataFrame(
        {"SomeOtherCol": [0, 60, 120], "YetAnotherCol": [1, 1, 1]}
    )

    def mock_read_excel_hydro(*args, **kwargs):
        usecols = kwargs.get("usecols")
        if callable(usecols):
            # Our stateful filter logic expects columns to be passed iteratively
            for col in df_missing.columns:
                usecols(col)
        # Because we load at least the first column, we mock the dataframe subset
        return df_missing[["SomeOtherCol"]]

    mock_read_excel.side_effect = mock_read_excel_hydro

    config = Config()
    validator = DataValidator(config)

    with (
        mock.patch.object(Path, "exists", return_value=True),
        mock.patch.object(Path, "stat", return_value=mock.Mock(st_size=1000)),
    ):
        result = validator.validate_hydro_file()

    assert result is not None
    sheet1 = result["sheets"][0]
    # Rows should match the length of the loaded first column (3 rows)
    assert sheet1["rows"] == 3
    # Required columns were absent
    assert sheet1["required_columns_present"] is False
    assert sheet1["years"] is None
    assert sheet1["time_range"] is None


@mock.patch("pandas.read_excel")
def test_validate_processed_files_missing_columns(mock_read_excel):
    """Test validate_processed_files behavior when required and sensor columns are absent."""
    df_missing = pd.DataFrame({"RandomData": [1.0, 2.0], "MoreRandomData": [3.0, 4.0]})

    def mock_read_excel_proc(*args, **kwargs):
        usecols = kwargs.get("usecols")
        if callable(usecols):
            for col in df_missing.columns:
                usecols(col)
        return df_missing[["RandomData"]]

    mock_read_excel.side_effect = mock_read_excel_proc

    config = Config()
    validator = DataValidator(config)

    # Create a mock path object that matches glob "RM_*.xlsx"
    mock_file = mock.MagicMock()
    mock_file.name = "RM_54.0.xlsx"
    mock_file.stem = "RM_54.0"
    mock_file.stat.return_value.st_size = 1000

    with (
        mock.patch.object(Path, "exists", return_value=True),
        mock.patch.object(Path, "glob", return_value=[mock_file]),
    ):

        results = validator.validate_processed_files()

    assert len(results) == 1
    res = results[0]
    assert res["river_mile"] == 54.0
    assert res["rows"] == 2
    assert res["required_columns_present"] is False
    assert res["sensor_columns"] == []
    assert res["year_range"] is None
    assert res["time_range"] is None


@mock.patch.object(DataValidator, "validate_summary_file")
@mock.patch.object(DataValidator, "validate_hydro_file")
@mock.patch.object(DataValidator, "validate_processed_files")
def test_run_validation_success(mock_processed, mock_hydro, mock_summary):
    """Test run_validation when all files are valid and consistent."""
    mock_summary.return_value = {"river_miles": [54.0, 53.0]}
    mock_hydro.return_value = {"mock_key": "mock_value"}
    mock_processed.return_value = [{"river_mile": 54.0}, {"river_mile": 53.0}]

    config = Config()
    validator = DataValidator(config)

    result = validator.run_validation()

    assert result["summary"] == mock_summary.return_value
    assert result["hydrograph"] == mock_hydro.return_value
    assert result["processed"] == mock_processed.return_value
    assert result["overall_valid"] is True

    assert result["river_mile_consistency"]["all_summary_rms_processed"] is True
    assert set(result["river_mile_consistency"]["missing_processed_rms"]) == set()
    assert set(result["river_mile_consistency"]["extra_processed_rms"]) == set()


@mock.patch.object(DataValidator, "validate_summary_file")
@mock.patch.object(DataValidator, "validate_hydro_file")
@mock.patch.object(DataValidator, "validate_processed_files")
def test_run_validation_inconsistent(mock_processed, mock_hydro, mock_summary):
    """Test run_validation when files are valid but river miles are inconsistent."""
    mock_summary.return_value = {"river_miles": [54.0, 53.0]}
    mock_hydro.return_value = {"mock_key": "mock_value"}
    mock_processed.return_value = [{"river_mile": 54.0}, {"river_mile": 55.0}]

    config = Config()
    validator = DataValidator(config)

    result = validator.run_validation()

    assert result["overall_valid"] is True
    assert result["river_mile_consistency"]["all_summary_rms_processed"] is False
    assert set(result["river_mile_consistency"]["missing_processed_rms"]) == {53.0}
    assert set(result["river_mile_consistency"]["extra_processed_rms"]) == {55.0}


@mock.patch.object(DataValidator, "validate_summary_file")
@mock.patch.object(DataValidator, "validate_hydro_file")
@mock.patch.object(DataValidator, "validate_processed_files")
def test_run_validation_failure(mock_processed, mock_hydro, mock_summary):
    """Test run_validation when files are invalid."""
    mock_summary.return_value = None
    mock_hydro.return_value = None
    mock_processed.return_value = []

    config = Config()
    validator = DataValidator(config)

    result = validator.run_validation()

    assert result["overall_valid"] is False
    assert result["river_mile_consistency"] is None
