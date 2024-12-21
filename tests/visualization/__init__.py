import os
import unittest
import pandas as pd
import matplotlib.pyplot as plt
from src.data_processing import Visualizer

class TestVisualizer(unittest.TestCase):
    def setUp(self):
        self.visualizer = Visualizer()
        self.test_data = pd.DataFrame({
            "Time (Seconds)": [0, 3600, 7200, 10800],
            "Sensor_1": [1.0, 2.5, 3.0, 4.5],
            "Year": [2020, 2020, 2020, 2020]
        })
        self.output_dir = "tests/visualization/output"
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            os.rmdir(self.output_dir)

    def test_create_visualization(self):
        fig, stats = self.visualizer.create_visualization(
            self.test_data, river_mile=1.0, year=2020, sensor="Sensor_1"
        )
        output_path = os.path.join(self.output_dir, "test_visualization.png")
        fig.savefig(output_path)
        plt.close(fig)
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(stats["mean"], 0)

if __name__ == "__main__":
    unittest.main()