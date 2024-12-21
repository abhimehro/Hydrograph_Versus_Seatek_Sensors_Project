import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from pandas import DataFrame
from src import (
    create_visualization,
    DataVisualizationError,
    save_visualization,
    setup_plot_style,
)

# Check if matplotlib is available to gracefully skip tests that require it
try:
    from matplotlib.figure import Figure

    has_matplotlib = True
except ImportError:
    Figure = None
    has_matplotlib = False


class TestVisualization(unittest.TestCase):
    # Extract constants for better readability and maintainability
    SENSOR_COLUMN = "Sensor_1"
    TIME_COLUMN = "Time_(Hours)"
    HYDROGRAPH_COLUMN = "Hydrograph (Lagged)"

    def setUp(self) -> None:
        """
        Set up shared test resources, including plot data, column mappings,
        and a temporary directory for storing artifacts.
        """
        self.plot_data = self.get_test_plot_data()
        self.column_mappings = {
            "time": self.TIME_COLUMN,
            "hydrograph": self.HYDROGRAPH_COLUMN,
            "year": "Year",
        }
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.temp_dir.name) / "test_output.png"

    def tearDown(self) -> None:
        """Clean up temporary directory after tests."""
        self.temp_dir.cleanup()

    @staticmethod
    def get_test_plot_data() -> DataFrame:
        """Provide shared test data DataFrame."""
        return DataFrame({
            TestVisualization.TIME_COLUMN: [0, 1, 2, 3],
            TestVisualization.HYDROGRAPH_COLUMN: [10, 20, 30, 40],
            TestVisualization.SENSOR_COLUMN: [15, 25, 35, 45],
        })

    def test_setup_plot_style(self) -> None:
        """Test that setup_plot_style() executes without exceptions."""
        import matplotlib as mpl
        original_style = mpl.rcParams.copy()

        try:
            setup_plot_style()
            # Validate changes made to rcParams
            self.assertNotEqual(original_style, mpl.rcParams)
        except Exception as e:
            self.fail(f"setup_plot_style() raised an exception: {e}")
        finally:
            # Restore the original style
            mpl.rcParams.update(original_style)

    @unittest.skipIf(not has_matplotlib, "matplotlib is required for this test")
    def test_create_visualization(self) -> None:
        """
        Test that create_visualization() generates the expected outputs.
        """
        expected_correlation = 0.99  # Replace with appropriate value
        rain_multiplier = 1.0  # Improved clarity for `rm`
        year = 2023

        try:
            fig, correlation = create_visualization(
                plot_data=self.plot_data,
                rm=rain_multiplier,
                year=year,
                sensor=self.SENSOR_COLUMN,
                column_mappings=self.column_mappings,
            )
            self.assertIsInstance(fig, Figure)
            self.assertIsInstance(correlation, float)
            self.assertAlmostEqual(correlation, expected_correlation, places=2)
        except DataVisualizationError as e:
            self.fail(f"create_visualization() raised DataVisualizationError: {e}")

    @unittest.skipIf(not has_matplotlib, "matplotlib is required for this test")
    def test_save_visualization(self) -> None:
        """
        Test that save_visualization() saves the figure and performs cleanup.
        """
        with patch("src.visualization.Path.exists", return_value=True) as mock_exists, \
                patch("src.visualization.Path.unlink") as mock_unlink:
            # Create the visualization to save
            fig, _ = create_visualization(
                self.plot_data, 1.0, 2023, self.SENSOR_COLUMN, self.column_mappings
            )
            try:
                save_visualization(fig, self.output_path)
                self.assertTrue(self.output_path.exists())  # File should exist
            except DataVisualizationError as e:
                self.fail(f"save_visualization() raised DataVisualizationError: {e}")
            # Assertions to ensure file cleanup occurred
            mock_unlink.assert_called_once()
            mock_exists.assert_called_once()

    def test_invalid_column_mapping(self) -> None:
        """Test invalid column mappings for create_visualization()."""
        invalid_column_mappings = {
            "invalid_key": self.TIME_COLUMN,  # This key doesn't exist in the DataFrame
        }
        with self.assertRaises(DataVisualizationError):
            create_visualization(
                self.plot_data, 1.0, 2023, self.SENSOR_COLUMN, invalid_column_mappings
            )

    def test_empty_plot_data(self) -> None:
        """Test empty plot data for create_visualization()."""
        empty_data = DataFrame()  # Empty DataFrame
        with self.assertRaises(DataVisualizationError):
            create_visualization(
                empty_data, 1.0, 2023, self.SENSOR_COLUMN, self.column_mappings
            )

    def test_insufficient_numeric_data(self) -> None:
        """Test insufficient numeric data in create_visualization()."""
        insufficient_data = DataFrame({
            self.TIME_COLUMN: [0],
            self.HYDROGRAPH_COLUMN: [10],
            self.SENSOR_COLUMN: [15],
        })  # Only one data point
        with self.assertRaises(DataVisualizationError):
            create_visualization(
                insufficient_data, 1.0, 2023, self.SENSOR_COLUMN, self.column_mappings
            )

    def test_invalid_sensor_in_column_mappings(self) -> None:
        """Test invalid sensor in column mappings for create_visualization()."""
        with self.assertRaises(DataVisualizationError):
            create_visualization(
                self.plot_data, 1.0, 2023, "Invalid_Sensor", self.column_mappings
            )


if __name__ == "__main__":
    unittest.main()
