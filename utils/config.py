"""Configuration management for Seatek data processing."""

from pathlib import Path

class Config:
    """Configuration settings for the Seatek data processing pipeline."""

    def __init__(self):
        # Base directories
        self.base_dir = Path("/Users/abhimehrotra/PycharmProjects/Hydrograph_Versus_Seatek_Sensors_Project")
        self.data_dir = self.base_dir / "data"
        self.raw_data_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.output_dir = self.base_dir / "output/charts"

        # Ensure directories exist
        for directory in [self.data_dir, self.raw_data_dir, self.processed_dir, self.output_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Data file paths
        self.summary_file = self.raw_data_dir / "Data_Summary.xlsx"
        self.hydro_file = self.raw_data_dir / "Hydrograph_Seatek_Data.xlsx"

        # Processing constants
        self.navd88_constants = {
            'offset_a': 1.9,
            'offset_b': 0.32,
            'scale_factor': 400 / 30.48
        }

        # Visualization settings
        self.chart_settings = {
            'dpi': 300,
            'figure_size': (12, 8),
            'font_family': 'Arial',
            'font_size': 11
        }
