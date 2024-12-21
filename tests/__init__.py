import os
import unittest

from matplotlib import pyplot as plt

from src.data_processing import DataProcessor, Visualizer, DataAnalyzer

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DataProcessor("path/to/test/file.xlsx")

    def test_load_data(self):
        self.processor.load_data()
        self.assertIsNotNone(self.processor.summary_data)
        self.assertGreater(len(self.processor.river_mile_data), 0)

class TestVisualizer(unittest.TestCase):
    def setUp(self):
        self.visualizer = Visualizer()

    def test_setup_plot_style(self):
        self.visualizer.setup_plot_style()
        self.assertEqual(plt.rcParams["font.family"], "sans-serif")

class TestDataAnalyzer(unittest.TestCase):
    def setUp(self):
        self.processor = DataProcessor("path/to/test/file.xlsx")
        self.visualizer = Visualizer()
        self.analyzer = DataAnalyzer(self.processor, self.visualizer)

    def test_process_all_data(self):
        self.processor.load_data()
        self.analyzer.process_all_data()
        self.assertTrue(os.path.exists(self.analyzer.output_base_dir))

if __name__ == "__main__":
    unittest.main()