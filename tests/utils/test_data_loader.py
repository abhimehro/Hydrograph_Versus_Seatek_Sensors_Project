import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from utils.config import Config
from utils.data_loader import DataLoader


class TestDataLoaderSizeLimits(unittest.TestCase):
    @patch.object(Path, 'mkdir')
    def setUp(self, mock_mkdir):
        # Prevent the Config from trying to make hardcoded /Users/... dirs
        self.config = Config()
        self.loader = DataLoader(self.config)

    @patch('utils.data_loader.pd.read_excel')
    @patch.object(Path, 'stat')
    @patch.object(Path, 'exists')
    def test_load_summary_data_size_limit(self, mock_exists, mock_stat, mock_read_excel):
        mock_exists.return_value = True

        # Mock st_size to be larger than max_file_size_bytes
        mock_stat.return_value = MagicMock(st_size=self.config.max_file_size_bytes + 1)

        with self.assertRaises(ValueError) as context:
            self.loader._load_summary_data()

        self.assertIn("Summary file exceeds maximum size", str(context.exception))
        mock_read_excel.assert_not_called()

    @patch('utils.data_loader.pd.ExcelFile')
    @patch.object(Path, 'stat')
    @patch.object(Path, 'exists')
    def test_load_hydro_data_size_limit(self, mock_exists, mock_stat, mock_excel_file):
        mock_exists.return_value = True

        # Mock st_size to be larger than max_file_size_bytes
        mock_stat.return_value = MagicMock(st_size=self.config.max_file_size_bytes + 1)

        with self.assertRaises(ValueError) as context:
            self.loader._load_hydro_data()

        self.assertIn("Hydrograph file exceeds maximum size", str(context.exception))
        mock_excel_file.assert_not_called()

if __name__ == '__main__':
    unittest.main()
