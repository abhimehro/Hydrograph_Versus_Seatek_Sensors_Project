import unittest
from pathlib import Path

from matplotlib.figure import Figure
from pandas import DataFrame
from src import (
    create_visualization ,
    DataVisualizationError ,
    save_visualization ,
    setup_plot_style ,
    )


class TestVisualization(unittest.TestCase):

    def test_setup_plot_style(self):
        try:
            setup_plot_style()
        except Exception as e:
            self.fail(f"setup_plot_style() raised an exception: {e}")

    def test_create_visualization(self):
        plot_data = DataFrame(
            {
                "Time_(Hours)": [0, 1, 2, 3],
                "Hydrograph (Lagged)": [10, 20, 30, 40],
                "Sensor_1": [15, 25, 35, 45],
            }
        )
        column_mappings = {
            "time": "Time_(Hours)",
            "hydrograph": "Hydrograph (Lagged)",
            "year": "Year",
        }
        try:
            fig, correlation = create_visualization(
                plot_data, 1.0, 2023, "Sensor_1", column_mappings
            )
            self.assertIsInstance(fig, Figure)
            self.assertIsInstance(correlation, float)
        except DataVisualizationError as e:
            self.fail(f"create_visualization() raised DataVisualizationError: {e}")

    def test_save_visualization(self):
        plot_data = DataFrame(
            {
                "Time_(Hours)": [0, 1, 2, 3],
                "Hydrograph (Lagged)": [10, 20, 30, 40],
                "Sensor_1": [15, 25, 35, 45],
            }
        )
        column_mappings = {
            "time": "Time_(Seconds)",
            "hydrograph": "Hydrograph (Lagged)",
            "year": "Year",
        }
        fig, _ = create_visualization(plot_data, 1.0, 2023, "Sensor_1", column_mappings)
        output_path = Path("test_output.png")
        try:
            save_visualization(fig, output_path)
            self.assertTrue(output_path.exists())
        except DataVisualizationError as e:
            self.fail(f"save_visualization() raised DataVisualizationError: {e}")
        finally:
            if output_path.exists():
                output_path.unlink()  # Clean up the test file


if __name__ == "__main__":
    unittest.main()
