from typing import Any

"""Tests for the data validator module."""

from pathlib import Path
from unittest import mock

import pandas as pd

from src.hydrograph_seatek_analysis.core.config import Config
from src.hydrograph_seatek_analysis.data.validator import DataValidator


def _create_mock_read_excel(df: Any) -> Any:
    """Helper to create a mock read_excel function that respects usecols callback."""

    def _mock_read_excel(*args: Any, **kwargs: Any) -> Any:
        usecols = kwargs.get("usecols")
        if callable(usecols):
            for col in df.columns:
                usecols(col)
        return df

    return _mock_read_excel


def _mock_path_context(validator_func: Any, **kwargs: Any) -> Any:
    """Helper to mock Path.is_file and Path.stat to avoid file not found errors."""
    with (
        mock.patch.object(Path, "is_file", return_value=True),
        mock.patch.object(Path, "stat", return_value=mock.Mock(st_size=1000)),
    ):
        if "glob_mock" in kwargs:
            with mock.patch.object(Path, "glob", return_value=kwargs["glob_mock"]):
                return validator_func()
        return validator_func()


def _setup_validator_test() -> DataValidator:
    """Helper to setup config and validator."""
    return DataValidator(Config())


def test_validator_initialization() -> None:
    """Test DataValidator initialization."""
    validator = _setup_validator_test()
    assert validator.config is not None


@mock.patch.object(Path, "is_symlink", return_value=False)
@mock.patch("pandas.read_excel")
def test_validate_summary_file(mock_read_excel: Any, mock_is_symlink: Any) -> None:
    """Test validate_summary_file with mocked Excel file."""
    mock_read_excel.side_effect = _create_mock_read_excel(
        pd.DataFrame(
            {
                "River_Mile": [54.0, 53.0],
                "Y_Offset": [10.5, 11.2],
                "Num_Sensors": [2, 2],
            }
        )
    )
    validator = _setup_validator_test()
    result = _mock_path_context(validator.validate_summary_file)
    assert result is not None
    assert result["file"] == validator.config.summary_file.name
    assert result["rows"] == 2
    assert "River_Mile" in result["columns"]
    assert result["required_columns_present"] is True
    assert result["river_miles"] == [54.0, 53.0]


@mock.patch.object(Path, "is_symlink", return_value=False)
@mock.patch("pandas.read_excel")
def test_validate_summary_file_missing_columns(
    mock_read_excel: Any, mock_is_symlink: Any
) -> None:
    """Test validate_summary_file with missing columns."""
    mock_read_excel.side_effect = _create_mock_read_excel(
        pd.DataFrame({"River_Mile": [54.0, 53.0]})
    )
    validator = _setup_validator_test()
    assert _mock_path_context(validator.validate_summary_file) is None


@mock.patch("pandas.ExcelFile")
@mock.patch.object(Path, "is_symlink", return_value=False)
@mock.patch("pandas.read_excel")
def test_validate_hydro_file(
    mock_read_excel: Any, mock_is_symlink: Any, mock_excel_file_cls: Any
) -> None:
    """Test validate_hydro_file with mocked Excel file."""
    mock_excel_file = mock.MagicMock()
    mock_excel_file.sheet_names = ["RM_54.0", "RM_53.0", "OtherSheet"]
    mock_excel_file_cls.return_value.__enter__.return_value = mock_excel_file

    df_base = pd.DataFrame({"Time (Seconds)": [0, 60, 120], "Year": [1, 1, 1]})

    def mock_read_excel_hydro(*args: Any, **kwargs: Any) -> Any:
        sheet = kwargs.get("sheet_name")
        df = df_base if sheet in ("RM_54.0", "RM_53.0") else pd.DataFrame()
        return _create_mock_read_excel(df)(*args, **kwargs)

    mock_read_excel.side_effect = mock_read_excel_hydro
    validator = _setup_validator_test()
    result = _mock_path_context(validator.validate_hydro_file)

    assert result is not None
    assert result["file"] == validator.config.hydro_file.name
    assert len(result["sheets"]) == 2
    assert result["river_mile_sheets"] == ["RM_54.0", "RM_53.0"]
    sheet1 = next(s for s in result["sheets"] if s["name"] == "RM_54.0")
    assert sheet1["rows"] == 3
    assert sheet1["required_columns_present"] is True


@mock.patch("pandas.ExcelFile")
@mock.patch.object(Path, "is_symlink", return_value=False)
@mock.patch("pandas.read_excel")
def test_validate_hydro_file_missing_columns(
    mock_read_excel: Any, mock_is_symlink: Any, mock_excel_file_cls: Any
) -> None:
    """Test validate_hydro_file behavior when required columns are absent."""
    mock_excel_file = mock.MagicMock()
    mock_excel_file.sheet_names = ["RM_54.0"]
    mock_excel_file_cls.return_value.__enter__.return_value = mock_excel_file

    df_missing = pd.DataFrame(
        {"SomeOtherCol": [0, 60, 120], "YetAnotherCol": [1, 1, 1]}
    )
    mock_read_excel.side_effect = _create_mock_read_excel(df_missing[["SomeOtherCol"]])

    validator = _setup_validator_test()
    result = _mock_path_context(validator.validate_hydro_file)

    assert result is not None
    assert result["sheets"][0]["rows"] == 3
    assert result["sheets"][0]["required_columns_present"] is False


@mock.patch.object(Path, "is_symlink", return_value=False)
@mock.patch("pandas.read_excel")
def test_validate_processed_files_missing_columns(
    mock_read_excel: Any, mock_is_symlink: Any
) -> None:
    """Test validate_processed_files behavior when required and sensor columns are absent."""
    mock_read_excel.side_effect = _create_mock_read_excel(
        pd.DataFrame({"RandomData": [1.0, 2.0], "MoreRandomData": [3.0, 4.0]})[
            ["RandomData"]
        ]
    )

    validator = _setup_validator_test()
    mock_file = mock.MagicMock()
    mock_file.name = "RM_54.0.xlsx"
    mock_file.stem = "RM_54.0"
    mock_file.stat.return_value.st_size = 1000
    mock_file.exists.return_value = True
    mock_file.is_symlink.return_value = False

    results = _mock_path_context(
        validator.validate_processed_files, glob_mock=[mock_file]
    )

    assert len(results) == 1
    assert results[0]["river_mile"] == 54.0
    assert results[0]["required_columns_present"] is False


@mock.patch.object(DataValidator, "validate_summary_file")
@mock.patch.object(DataValidator, "validate_hydro_file")
@mock.patch.object(DataValidator, "validate_processed_files")
def test_run_validation_success(
    mock_processed: Any, mock_hydro: Any, mock_summary: Any
) -> None:
    """Test run_validation when all files are valid and consistent."""
    mock_summary.return_value = {"river_miles": [54.0, 53.0]}
    mock_hydro.return_value = {"mock_key": "mock_value"}
    mock_processed.return_value = [{"river_mile": 54.0}, {"river_mile": 53.0}]

    result = _setup_validator_test().run_validation()

    assert result["overall_valid"] is True
    assert result["river_mile_consistency"]["all_summary_rms_processed"] is True


@mock.patch.object(DataValidator, "validate_summary_file")
@mock.patch.object(DataValidator, "validate_hydro_file")
@mock.patch.object(DataValidator, "validate_processed_files")
def test_run_validation_inconsistent(
    mock_processed: Any, mock_hydro: Any, mock_summary: Any
) -> None:
    """Test run_validation when files are valid but river miles are inconsistent."""
    mock_summary.return_value = {"river_miles": [54.0, 53.0]}
    mock_hydro.return_value = {"mock_key": "mock_value"}
    mock_processed.return_value = [{"river_mile": 54.0}, {"river_mile": 55.0}]

    result = _setup_validator_test().run_validation()

    assert result["overall_valid"] is True
    assert result["river_mile_consistency"]["all_summary_rms_processed"] is False
    assert set(result["river_mile_consistency"]["missing_processed_rms"]) == {53.0}


@mock.patch.object(DataValidator, "validate_summary_file")
@mock.patch.object(DataValidator, "validate_hydro_file")
@mock.patch.object(DataValidator, "validate_processed_files")
def test_run_validation_failure(
    mock_processed: Any, mock_hydro: Any, mock_summary: Any
) -> None:
    """Test run_validation when files are invalid."""
    mock_summary.return_value = None
    mock_hydro.return_value = None
    mock_processed.return_value = []

    result = _setup_validator_test().run_validation()
    assert result["overall_valid"] is False
