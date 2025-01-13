"""Configuration management for Seatek data processing."""

from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration settings."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data"
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.output_dir = self.project_root / "output" / "charts"

        # Data file paths
        self.summary_file = self.raw_dir / "Data_Summary.xlsx"
        self.hydro_file = self.raw_dir / "Hydrograph_Seatek_Data.xlsx"

        # Constants
        self.navd88_constants = {
            'offset_a': 1.9,
            'offset_b': 0.32,
            'scale_factor': 400 / 30.48
        }
