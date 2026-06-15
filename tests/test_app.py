"""Tests for the Application class."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.hydrograph_seatek_analysis.app import Application, main
from src.hydrograph_seatek_analysis.core.config import Config


class TestApplication(unittest.TestCase):
    """Tests for Application."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.temp_config = Config(base_dir=self.temp_path)

    def tearDown(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_setup_success(self) -> None:
        """Test that setup returns True when all directories are created."""
        app = Application(config=self.temp_config)

        self.assertTrue(app.setup())

        # Verify directories were actually created
        self.assertTrue(self.temp_config.data_dir.exists())
        self.assertTrue(self.temp_config.raw_data_dir.exists())
        self.assertTrue(self.temp_config.processed_dir.exists())
        self.assertTrue(self.temp_config.output_dir.exists())

    def test_setup_exception(self) -> None:
        """Test that setup returns False if directory creation fails."""
        app = Application(config=self.temp_config)

        with mock.patch.object(
            Path, "mkdir", side_effect=PermissionError("Permission denied")
        ):
            self.assertFalse(app.setup())

    @mock.patch("src.hydrograph_seatek_analysis.app.DataLoader")
    def test_load_data_exception(self, mock_dl_class: mock.MagicMock) -> None:
        """Test that load_data returns False on data loading exception."""
        app = Application(config=self.temp_config)

        # We need to mock load_all_data to raise an exception
        app.data_loader.load_all_data.side_effect = Exception(  # type: ignore
            "Mock loading error"
        )

        # Test loading data failure
        self.assertFalse(app.load_data())




    def _setup_mock_processor(self, app: Application) -> mock.MagicMock:
        """Helper to set up a mock processor with basic river mile data."""
        app.processor = mock.MagicMock()
        rm_data = mock.MagicMock()
        rm_data.river_mile = 12.3
        rm_data.year_data_cache = {2020: {}}
        rm_data.sensors = ["sensor_1"]
        app.processor.river_mile_data = {"12.3": rm_data}
        return app.processor

    def test_process_data_no_processor(self) -> None:
        """Test process_data when processor is not initialized."""
        app = Application(config=self.temp_config)
        with mock.patch.object(app.logger, "error") as mock_logger:
            self.assertFalse(app.process_data())
            mock_logger.assert_called_once()

    @mock.patch("src.hydrograph_seatek_analysis.app.ChartGenerator")
    def test_process_data_success(self, mock_chart_gen_class: mock.MagicMock) -> None:
        """Test successful data processing."""
        app = Application(config=self.temp_config)
        self._setup_mock_processor(app)

        # Setup processor to return data
        app.processor.process_data.return_value = ([1], {})

        # Setup chart generator
        app.chart_generator = mock_chart_gen_class.return_value
        app.chart_generator.create_chart.return_value = (mock.MagicMock(), {})

        with mock.patch.object(app, "_save_generated_chart", return_value=True) as mock_save:
            self.assertTrue(app.process_data())
            mock_save.assert_called_once()

    def test_process_data_empty_data(self) -> None:
        """Test process_data when processor returns empty data."""
        app = Application(config=self.temp_config)
        self._setup_mock_processor(app)

        # Return empty list
        app.processor.process_data.return_value = ([], {})

        with mock.patch.object(app.logger, "warning") as mock_warning:
            self.assertTrue(app.process_data())
            mock_warning.assert_called_once()

    @mock.patch("src.hydrograph_seatek_analysis.app.ChartGenerator")
    def test_process_data_chart_generation_failure(self, mock_chart_gen_class: mock.MagicMock) -> None:
        """Test process_data when chart generation fails."""
        app = Application(config=self.temp_config)
        self._setup_mock_processor(app)

        # Mock process data to return something
        app.processor.process_data.return_value = ([1], {})

        # Fail chart generation
        app.chart_generator = mock_chart_gen_class.return_value
        app.chart_generator.create_chart.return_value = (None, None)

        with mock.patch.object(app.logger, "error") as mock_error:
            self.assertFalse(app.process_data())
            mock_error.assert_called_once()

    @mock.patch("src.hydrograph_seatek_analysis.app.ChartGenerator")
    def test_process_data_save_chart_failure(self, mock_chart_gen_class: mock.MagicMock) -> None:
        """Test process_data when saving chart fails."""
        app = Application(config=self.temp_config)
        self._setup_mock_processor(app)

        app.processor.process_data.return_value = ([1], {})

        app.chart_generator = mock_chart_gen_class.return_value
        app.chart_generator.create_chart.return_value = (mock.MagicMock(), {})

        with mock.patch.object(app, "_save_generated_chart", return_value=False):
            self.assertFalse(app.process_data())

    def test_process_data_exception_during_processing(self) -> None:
        """Test process_data when processor raises exception."""
        app = Application(config=self.temp_config)
        self._setup_mock_processor(app)

        app.processor.process_data.side_effect = Exception("Test Exception")

        with mock.patch.object(app.logger, "error") as mock_error:
            self.assertFalse(app.process_data())
            mock_error.assert_called()

    def test_process_data_exception_overall(self) -> None:
        """Test process_data when an unexpected overall exception occurs."""
        app = Application(config=self.temp_config)

        # Safe way to trigger the outer except block:
        # We mock processor with a regular Mock (not MagicMock) and delete the
        # river_mile_data attribute to trigger an AttributeError when accessed.
        app.processor = mock.Mock()
        del app.processor.river_mile_data

        with mock.patch.object(app.logger, "error") as mock_error:
            self.assertFalse(app.process_data())
            mock_error.assert_called_once()


class TestMain(unittest.TestCase):
    """Tests for the main function."""

    @mock.patch("src.hydrograph_seatek_analysis.app.configure_root_logger")
    @mock.patch("src.hydrograph_seatek_analysis.app.Application")
    @mock.patch("src.hydrograph_seatek_analysis.app.Path")
    def test_main_success(self, mock_path, mock_app_class, mock_configure_logger) -> None:
        """Test main execution returning 0 on success."""
        mock_app_instance = mock.MagicMock()
        mock_app_instance.run.return_value = True
        mock_app_class.return_value = mock_app_instance

        exit_code = main()

        self.assertEqual(exit_code, 0)
        mock_app_instance.run.assert_called_once()
        mock_configure_logger.assert_called_once()
        mock_path.return_value.mkdir.assert_called_once_with(exist_ok=True)

    @mock.patch("src.hydrograph_seatek_analysis.app.configure_root_logger")
    @mock.patch("src.hydrograph_seatek_analysis.app.Application")
    @mock.patch("src.hydrograph_seatek_analysis.app.Path")
    def test_main_failure(self, mock_path, mock_app_class, mock_configure_logger) -> None:
        """Test main execution returning 1 on app failure."""
        mock_app_instance = mock.MagicMock()
        mock_app_instance.run.return_value = False
        mock_app_class.return_value = mock_app_instance

        exit_code = main()

        self.assertEqual(exit_code, 1)
        mock_app_instance.run.assert_called_once()

    @mock.patch("src.hydrograph_seatek_analysis.app.configure_root_logger")
    @mock.patch("src.hydrograph_seatek_analysis.app.Path")
    def test_main_exception(self, mock_path, mock_configure_logger) -> None:
        """Test main execution returning 1 on exception."""
        mock_configure_logger.side_effect = Exception("Test Exception")

        with mock.patch("src.hydrograph_seatek_analysis.app.logging.error") as mock_logging_error:
            exit_code = main()

        self.assertEqual(exit_code, 1)
        mock_logging_error.assert_called_once_with("Fatal error in main execution: Test Exception")


if __name__ == "__main__":
    unittest.main()
