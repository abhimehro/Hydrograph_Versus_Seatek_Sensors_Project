"""Tests for the Application class."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from matplotlib.figure import Figure

from src.hydrograph_seatek_analysis.app import Application, main
from src.hydrograph_seatek_analysis.core.config import Config
from src.hydrograph_seatek_analysis.utils.security import sanitize_filename


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

    @mock.patch("src.hydrograph_seatek_analysis.app.SeatekDataProcessor")
    @mock.patch("src.hydrograph_seatek_analysis.app.DataLoader")
    def test_load_data_exception(
        self,
        mock_dl_class: mock.MagicMock,
        mock_processor_class: mock.MagicMock,
    ) -> None:
        """Test that load_data returns False on data loading exception."""
        app = Application(config=self.temp_config)

        app.data_loader.load_summary_data.side_effect = Exception("Mock loading error")

        self.assertFalse(app.load_data())
        app.data_loader.load_summary_data.assert_called_once()
        app.data_loader.load_all_data.assert_not_called()
        mock_processor_class.assert_not_called()

    @mock.patch("src.hydrograph_seatek_analysis.app.SeatekDataProcessor")
    @mock.patch("src.hydrograph_seatek_analysis.app.DataLoader")
    def test_load_data_uses_summary_only(
        self,
        mock_dl_class: mock.MagicMock,
        mock_processor_class: mock.MagicMock,
    ) -> None:
        """Test load_data does not require the aggregate hydrograph workbook."""
        summary_data = mock.MagicMock()
        processor = mock_processor_class.return_value
        processor.river_mile_data = {54.0: mock.MagicMock()}
        app = Application(config=self.temp_config)
        app.data_loader.load_summary_data.return_value = summary_data

        self.assertTrue(app.load_data())

        app.data_loader.load_summary_data.assert_called_once()
        app.data_loader.load_all_data.assert_not_called()
        app.data_loader._load_hydro_data.assert_not_called()
        mock_processor_class.assert_called_once_with(
            data_dir=self.temp_config.processed_dir,
            summary_data=summary_data,
            config=self.temp_config,
        )
        processor.load_data.assert_called_once()

    def _setup_mock_processor(self, app: Application) -> mock.MagicMock:
        """Helper to set up a mock processor with basic river mile data."""
        app.processor = mock.MagicMock()
        rm_data = mock.MagicMock()
        rm_data.river_mile = 12.3
        rm_data.year_data_cache = {2020: {}}
        rm_data.sensors = ["sensor_1"]
        app.processor.river_mile_data = {"12.3": rm_data}
        return app.processor

    def _setup_processing_test(
        self, mock_chart_gen_class: mock.MagicMock
    ) -> tuple[Application, mock.MagicMock]:
        """Helper to set up Application, processor and chart generator mocks for processing tests."""
        app = Application(config=self.temp_config)
        self._setup_mock_processor(app)
        app.processor.process_data.return_value = ([1], {})
        app.chart_generator = mock_chart_gen_class.return_value
        return app, app.chart_generator

    def test_process_data_no_processor(self) -> None:
        """Test process_data when processor is not initialized."""
        app = Application(config=self.temp_config)
        with mock.patch.object(app.logger, "error") as mock_logger:
            self.assertFalse(app.process_data())
            mock_logger.assert_called_once()

    def test_save_generated_charts_preserves_colliding_sensors(self) -> None:
        """Distinct sensor names produce separate PNGs without replacing earlier ones."""
        app = Application(config=self.temp_config)
        self.temp_config.chart_settings.dpi = 30
        rm_data = mock.Mock(river_mile=12.3)
        fig = Figure(figsize=(1, 1))
        fig.subplots().plot([0, 1])
        originals = {}
        for sensor in (
            "Sensor/1",
            "Sensor?1",
            "Sensor_1",
            "Sensor_é",
            "Sensor_ø",
            "Sensor_" + "A" * 300 + "x",
            "Sensor_" + "A" * 300 + "y",
        ):
            self.assertTrue(app._save_generated_chart(fig, rm_data, 2020, sensor))
            path = (
                self.temp_config.output_dir
                / "RM_12.3"
                / f"Year_2020_{sanitize_filename(sensor)}.png"
            )
            originals[path] = path.read_bytes()
            for previous_path, content in originals.items():
                self.assertEqual(previous_path.read_bytes(), content)
        self.assertEqual(len(list(self.temp_config.output_dir.rglob("*.png"))), 7)

    def test_save_generated_chart_rejects_residual_collision(self) -> None:
        """A literal name matching a hashed name cannot reach savefig twice."""
        app = Application(config=self.temp_config)
        rm_data = mock.Mock(river_mile=12.3)
        first = mock.Mock()
        second = mock.Mock()
        with mock.patch("matplotlib.pyplot.close"):
            self.assertTrue(app._save_generated_chart(first, rm_data, 2020, "Sensor/1"))
            self.assertFalse(
                app._save_generated_chart(
                    second, rm_data, 2020, sanitize_filename("Sensor/1")
                )
            )
        first.savefig.assert_called_once()
        second.savefig.assert_not_called()

    def test_save_generated_chart_rejects_resolved_collision(self) -> None:
        """An in-directory symlink cannot alias an earlier chart and overwrite it."""
        app = Application(config=self.temp_config)
        rm_data = mock.Mock(river_mile=12.3)
        fig = Figure(figsize=(1, 1))
        self.assertTrue(app._save_generated_chart(fig, rm_data, 2020, "Sensor_1"))
        directory = self.temp_config.output_dir / "RM_12.3"
        original = directory / "Year_2020_Sensor_1.png"
        content = original.read_bytes()
        (directory / "Year_2020_Sensor_2.png").symlink_to(original)
        second = mock.Mock()
        self.assertFalse(app._save_generated_chart(second, rm_data, 2020, "Sensor_2"))
        second.savefig.assert_not_called()
        self.assertEqual(original.read_bytes(), content)

    def test_save_generated_chart_preserves_safe_path_check(self) -> None:
        """An output directory symlink escaping the chart root is still rejected."""
        app = Application(config=self.temp_config)
        outside = self.temp_path / "outside"
        outside.mkdir()
        (self.temp_config.output_dir / "RM_12.3").symlink_to(outside)
        fig = mock.Mock()
        self.assertFalse(
            app._save_generated_chart(fig, mock.Mock(river_mile=12.3), 2020, "Sensor/1")
        )
        fig.savefig.assert_not_called()
        self.assertEqual(list(outside.iterdir()), [])

    @mock.patch("src.hydrograph_seatek_analysis.app.ChartGenerator")
    def test_process_data_collision_guard_resets_each_run(self, mock_chart_gen_class):
        """Duplicates fail within a run, and a new run can refresh its charts."""
        app, chart_gen = self._setup_processing_test(mock_chart_gen_class)
        rm_data = next(iter(app.processor.river_mile_data.values()))
        rm_data.sensors = ["Sensor_1", "Sensor_1"]
        chart_gen.create_chart.return_value = (mock.Mock(), {})
        chart_gen.save_chart.return_value = True
        self.assertFalse(app.process_data())
        chart_gen.save_chart.assert_called_once()
        rm_data.sensors = ["Sensor_1"]
        self.assertTrue(app.process_data())
        self.assertEqual(chart_gen.save_chart.call_count, 2)

    @mock.patch("src.hydrograph_seatek_analysis.app.ChartGenerator")
    def test_process_data_success(self, mock_chart_gen_class: mock.MagicMock) -> None:
        """Test successful data processing."""
        app, chart_gen = self._setup_processing_test(mock_chart_gen_class)
        chart_gen.create_chart.return_value = (mock.MagicMock(), {})

        with mock.patch.object(
            app, "_save_generated_chart", return_value=True
        ) as mock_save:
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
    def test_process_data_chart_generation_failure(
        self, mock_chart_gen_class: mock.MagicMock
    ) -> None:
        """Test process_data when chart generation fails."""
        app, chart_gen = self._setup_processing_test(mock_chart_gen_class)
        chart_gen.create_chart.return_value = (None, None)

        with mock.patch.object(app.logger, "error") as mock_error:
            self.assertFalse(app.process_data())
            mock_error.assert_called_once()

    @mock.patch("src.hydrograph_seatek_analysis.app.ChartGenerator")
    def test_process_data_save_chart_failure(
        self, mock_chart_gen_class: mock.MagicMock
    ) -> None:
        """Test process_data when saving chart fails."""
        app, chart_gen = self._setup_processing_test(mock_chart_gen_class)
        chart_gen.create_chart.return_value = (mock.MagicMock(), {})

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
    @mock.patch("src.hydrograph_seatek_analysis.app.Config")
    @mock.patch("src.hydrograph_seatek_analysis.app.Path")
    def test_main_success(
        self, mock_path, mock_config_class, mock_app_class, mock_configure_logger
    ) -> None:
        """Test main execution returning 0 on success."""
        mock_app_instance = mock.MagicMock()
        mock_app_instance.run.return_value = True
        mock_app_class.return_value = mock_app_instance

        exit_code = main(argv=[])

        self.assertEqual(exit_code, 0)
        mock_app_class.assert_called_once_with(config=mock_config_class.return_value)
        mock_app_instance.run.assert_called_once()
        mock_configure_logger.assert_called_once()
        mock_path.return_value.mkdir.assert_called_once_with(exist_ok=True)

    @mock.patch("src.hydrograph_seatek_analysis.app.configure_root_logger")
    @mock.patch("src.hydrograph_seatek_analysis.app.Application")
    @mock.patch("src.hydrograph_seatek_analysis.app.Config")
    @mock.patch("src.hydrograph_seatek_analysis.app.Path")
    def test_main_failure(
        self, mock_path, mock_config_class, mock_app_class, mock_configure_logger
    ) -> None:
        """Test main execution returning 1 on app failure."""
        mock_app_instance = mock.MagicMock()
        mock_app_instance.run.return_value = False
        mock_app_class.return_value = mock_app_instance

        exit_code = main(argv=[])

        self.assertEqual(exit_code, 1)
        mock_app_instance.run.assert_called_once()

    @mock.patch("src.hydrograph_seatek_analysis.app.configure_root_logger")
    @mock.patch("src.hydrograph_seatek_analysis.app.Config")
    @mock.patch("src.hydrograph_seatek_analysis.app.Path")
    def test_main_exception(
        self, mock_path, mock_config_class, mock_configure_logger
    ) -> None:
        """Test main execution returning 1 on exception."""
        mock_configure_logger.side_effect = Exception("Test Exception")

        with mock.patch(
            "src.hydrograph_seatek_analysis.app.logging.error"
        ) as mock_logging_error:
            exit_code = main(argv=[])

        self.assertEqual(exit_code, 1)
        mock_logging_error.assert_called_once_with(
            "Fatal error in main execution: Test Exception"
        )

    @mock.patch("src.hydrograph_seatek_analysis.app.configure_root_logger")
    @mock.patch("src.hydrograph_seatek_analysis.app.Application")
    @mock.patch("src.hydrograph_seatek_analysis.app.Config")
    def test_main_help_exits_zero(self, mock_config, mock_app, mock_logger) -> None:
        """Test --help prints usage and exits 0 without running the app."""
        with self.assertRaises(SystemExit) as cm:
            main(argv=["--help"])
        self.assertEqual(cm.exception.code, 0)
        mock_app.assert_not_called()
        mock_config.assert_not_called()

    @mock.patch("src.hydrograph_seatek_analysis.app.configure_root_logger")
    @mock.patch("src.hydrograph_seatek_analysis.app.Application")
    @mock.patch("src.hydrograph_seatek_analysis.app.Config")
    def test_main_version_exits_zero(self, mock_config, mock_app, mock_logger) -> None:
        """Test --version prints version and exits 0 without running the app."""
        with self.assertRaises(SystemExit) as cm:
            main(argv=["--version"])
        self.assertEqual(cm.exception.code, 0)
        mock_app.assert_not_called()
        mock_config.assert_not_called()

    @mock.patch("src.hydrograph_seatek_analysis.app.configure_root_logger")
    @mock.patch("src.hydrograph_seatek_analysis.app.Application")
    @mock.patch("src.hydrograph_seatek_analysis.app.Config")
    @mock.patch("src.hydrograph_seatek_analysis.app.Path")
    def test_main_data_dir(
        self, mock_path, mock_config_class, mock_app_class, mock_configure_logger
    ) -> None:
        """Test --data-dir is forwarded to Config."""
        mock_config_instance = mock.MagicMock()
        mock_config_class.return_value = mock_config_instance

        # Keep the real Path for data directories; mock only the logs directory
        # used inside main() so tests do not write to the repo filesystem.
        mock_path.side_effect = lambda arg: (
            mock.MagicMock() if arg == "logs" else Path(arg)
        )

        main(argv=["--data-dir", "/tmp/test-data"])

        mock_config_class.assert_called_once_with(base_dir=Path("/tmp/test-data"))
        mock_app_class.assert_called_once_with(config=mock_config_instance)


if __name__ == "__main__":
    unittest.main()
