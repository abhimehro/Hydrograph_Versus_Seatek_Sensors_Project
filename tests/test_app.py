"""Tests for the Application class."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Mock pandas, matplotlib and other missing libraries in the sandbox
sys.modules["pandas"] = mock.MagicMock()
sys.modules["matplotlib"] = mock.MagicMock()
sys.modules["matplotlib.pyplot"] = mock.MagicMock()
sys.modules["matplotlib.figure"] = mock.MagicMock()
sys.modules["matplotlib.axes"] = mock.MagicMock()
sys.modules["matplotlib.lines"] = mock.MagicMock()
sys.modules["seaborn"] = mock.MagicMock()
sys.modules["matplotlib.dates"] = mock.MagicMock()
sys.modules["matplotlib.ticker"] = mock.MagicMock()
sys.modules["numpy"] = mock.MagicMock()

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

    def test_setup_exception(self):
        """Test that setup returns False if an exception occurs during directory creation."""
        app = Application(config=self.temp_config)

        with mock.patch.object(
            Path, "mkdir", side_effect=PermissionError("Permission denied")
        ):
            self.assertFalse(app.setup())


if __name__ == "__main__":
    unittest.main()
