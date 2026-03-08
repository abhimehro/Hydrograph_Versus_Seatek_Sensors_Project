"""Tests for the Application class."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sys

# Mock pandas, matplotlib and other missing libraries in the sandbox
sys.modules['pandas'] = mock.MagicMock()
sys.modules['matplotlib'] = mock.MagicMock()
sys.modules['matplotlib.pyplot'] = mock.MagicMock()
sys.modules['matplotlib.figure'] = mock.MagicMock()
sys.modules['matplotlib.axes'] = mock.MagicMock()
sys.modules['matplotlib.lines'] = mock.MagicMock()
sys.modules['seaborn'] = mock.MagicMock()
sys.modules['matplotlib.dates'] = mock.MagicMock()
sys.modules['matplotlib.ticker'] = mock.MagicMock()

from src.hydrograph_seatek_analysis.app import Application
from src.hydrograph_seatek_analysis.core.config import Config


class TestApplicationSetup(unittest.TestCase):
    """Tests for Application.setup()."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.temp_config = Config(base_dir=self.temp_path)

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_setup_success(self):
        """Test that setup returns True when all directories are created successfully."""
        app = Application(config=self.temp_config)

        self.assertTrue(app.setup())

        # Verify directories were actually created
        self.assertTrue(self.temp_config.data_dir.exists())
        self.assertTrue(self.temp_config.raw_data_dir.exists())
        self.assertTrue(self.temp_config.processed_dir.exists())
        self.assertTrue(self.temp_config.output_dir.exists())

    def test_setup_output_not_exists(self):
        """Test that setup returns False if the output directory does not exist after creation."""
        app = Application(config=self.temp_config)

        original_exists = Path.exists

        def mock_exists(path_self):
            if path_self == self.temp_config.output_dir:
                return False
            return original_exists(path_self)

        with mock.patch.object(Path, 'exists', autospec=True, side_effect=mock_exists):
            self.assertFalse(app.setup())

    def test_setup_output_not_dir(self):
        """Test that setup returns False if the output path exists but is not a directory."""
        app = Application(config=self.temp_config)

        original_is_dir = Path.is_dir

        def mock_is_dir(path_self):
            if path_self == self.temp_config.output_dir:
                return False
            return original_is_dir(path_self)

        with mock.patch.object(Path, 'is_dir', autospec=True, side_effect=mock_is_dir):
            self.assertFalse(app.setup())

    def test_setup_exception(self):
        """Test that setup returns False if an exception occurs during directory creation."""
        app = Application(config=self.temp_config)

        with mock.patch.object(Path, 'mkdir', side_effect=PermissionError("Permission denied")):
            self.assertFalse(app.setup())


if __name__ == '__main__':
    unittest.main()
