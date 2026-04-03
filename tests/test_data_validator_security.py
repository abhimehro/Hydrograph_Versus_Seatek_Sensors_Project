import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Create a mock for pandas so we can import data_validator even if pandas is missing
sys.modules["pandas"] = MagicMock()

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_validator import validate_data_files


class TestDataValidatorSecurity(unittest.TestCase):
    @patch("data_validator.Config")
    @patch("data_validator.pd.read_excel")
    @patch("data_validator.Path.is_symlink")
    @patch("data_validator.Path.exists")
    @patch("data_validator.Path.stat")
    @patch("data_validator.os.walk")
    def test_summary_path_size_exceeds(
        self, mock_walk, mock_stat, mock_exists, mock_is_symlink, mock_read_excel, mock_config_cls
    ):
        mock_walk.return_value = []
        mock_exists.return_value = True
        mock_is_symlink.return_value = False

        mock_config = MagicMock()
        mock_config.max_file_size_bytes = 100 * 1024 * 1024
        mock_config_cls.return_value = mock_config

        # Make the stat return size > 100MB
        mock_stat.return_value = MagicMock(st_size=100 * 1024 * 1024 + 1)

        with self.assertRaises(ValueError) as context:
            validate_data_files()

        self.assertIn("exceeds maximum size", str(context.exception))
        mock_read_excel.assert_not_called()

    @patch("data_validator.Config")
    @patch("data_validator.pd.read_excel")
    @patch("data_validator.pd.ExcelFile")
    @patch("data_validator.Path.is_symlink")
    @patch("data_validator.Path.exists")
    @patch("data_validator.Path.stat")
    @patch("data_validator.os.walk")
    def test_hydro_path_size_exceeds(
        self,
        mock_walk,
        mock_stat,
        mock_exists,
        mock_is_symlink,
        mock_excel_file,
        mock_read_excel,
        mock_config_cls,
    ):
        mock_walk.return_value = []
        mock_exists.return_value = True
        mock_is_symlink.return_value = False

        mock_config = MagicMock()
        mock_config.max_file_size_bytes = 100 * 1024 * 1024
        mock_config_cls.return_value = mock_config

        def stat_side_effect():
            # The order of checks: summary_path, hydro_path, rm_path
            # First stat call is for summary_path
            yield MagicMock(st_size=100)  # Passes
            # Second stat call is for hydro_path
            yield MagicMock(st_size=100)  # Passes general check
            yield MagicMock(st_size=100 * 1024 * 1024 + 1)  # Fails specific check

        mock_stat.side_effect = stat_side_effect()

        # Mock ExcelFile context manager
        mock_xlsx = MagicMock()
        mock_xlsx.sheet_names = ["Sheet1"]
        mock_excel_file.return_value.__enter__.return_value = mock_xlsx

        with self.assertRaises(ValueError) as context:
            validate_data_files()

        self.assertIn("exceeds maximum size", str(context.exception))
        self.assertEqual(mock_read_excel.call_count, 1)  # Called for summary_path
        mock_excel_file.assert_not_called()  # ExcelFile must not be used for oversized hydro file
        mock_excel_file.assert_not_called()

    @patch("data_validator.Config")
    @patch("data_validator.pd.read_excel")
    @patch("data_validator.pd.ExcelFile")
    @patch("data_validator.Path.is_symlink")
    @patch("data_validator.Path.exists")
    @patch("data_validator.Path.stat")
    @patch("data_validator.os.walk")
    def test_rm_path_size_exceeds(
        self,
        mock_walk,
        mock_stat,
        mock_exists,
        mock_is_symlink,
        mock_excel_file,
        mock_read_excel,
        mock_config_cls,
    ):
        mock_walk.return_value = []
        mock_exists.return_value = True
        mock_is_symlink.return_value = False

        mock_config = MagicMock()
        mock_config.max_file_size_bytes = 100 * 1024 * 1024
        mock_config_cls.return_value = mock_config

        def stat_side_effect():
            # summary_path general check
            yield MagicMock(st_size=100)
            # summary_path specific check
            yield MagicMock(st_size=100)
            # hydro_path checks path.stat() before general check
            yield MagicMock(st_size=100)
            # hydro_path checks path.stat() before specific check
            yield MagicMock(st_size=100)
            # hydro_path checks path.stat() inside loop
            yield MagicMock(st_size=100)
            # rm_path general check
            yield MagicMock(st_size=100)
            # rm_path specific check
            yield MagicMock(st_size=100 * 1024 * 1024 + 1)

        mock_stat.side_effect = stat_side_effect()

        # Mock ExcelFile context manager
        mock_xlsx = MagicMock()
        mock_xlsx.sheet_names = ["Sheet1"]
        mock_excel_file.return_value.__enter__.return_value = mock_xlsx

        with self.assertRaises(ValueError) as context:
            validate_data_files()

        self.assertIn("exceeds maximum", str(context.exception))
        self.assertEqual(
            mock_read_excel.call_count, 2
        )  # Called for summary_path and hydro_path
        mock_excel_file.assert_called_once()


if __name__ == "__main__":
    unittest.main()
