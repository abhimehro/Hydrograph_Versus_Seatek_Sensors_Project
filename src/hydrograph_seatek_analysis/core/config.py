"""Configuration management for Seatek data processing."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple, Any, Optional


@dataclass
class NavdConstants:
    """Constants for NAVD88 conversion."""
    offset_a: float = 1.9
    offset_b: float = 0.32
    scale_factor: float = 400 / 30.48


@dataclass
class ChartSettings:
    """Chart configuration settings."""
    dpi: int = 300
    figure_size: Tuple[int, int] = (12, 8)
    font_family: str = 'Arial'
    font_size: int = 11


@dataclass
class Config:
    """Configuration settings for the Seatek data processing pipeline."""
    
    # Override with environment variable if provided
    base_dir: Path = field(default_factory=lambda: Path(
        os.environ.get(
            "HYDROGRAPH_BASE_DIR", 
            Path.cwd()
        )
    ))
    data_dir: Path = field(init=False)
    raw_data_dir: Path = field(init=False)
    processed_dir: Path = field(init=False)
    output_dir: Path = field(init=False)
    
    summary_file: Path = field(init=False)
    hydro_file: Path = field(init=False)
    
    navd88_constants: NavdConstants = field(default_factory=NavdConstants)
    chart_settings: ChartSettings = field(default_factory=ChartSettings)
    
    def __post_init__(self) -> None:
        """Initialize derived paths and ensure directories exist."""
        self.data_dir = self.base_dir / "data"
        self.raw_data_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.output_dir = self.base_dir / "output/charts"
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Data file paths
        self.summary_file = self.raw_data_dir / "Data_Summary.xlsx"
        self.hydro_file = self.raw_data_dir / "Hydrograph_Seatek_Data.xlsx"
    
    def _ensure_directories(self) -> None:
        """Create directories if they don't exist."""
        for directory in [
            self.data_dir, 
            self.raw_data_dir, 
            self.processed_dir, 
            self.output_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create a Config instance from a dictionary."""
        # Extract NavdConstants if present
        navd_dict = config_dict.pop('navd88_constants', {})
        navd_constants = NavdConstants(**navd_dict) if navd_dict else NavdConstants()
        
        # Extract ChartSettings if present
        chart_dict = config_dict.pop('chart_settings', {})
        chart_settings = ChartSettings(**chart_dict) if chart_dict else ChartSettings()
        
        # Create base_dir if present
        base_dir = config_dict.pop('base_dir', None)
        if base_dir:
            base_dir = Path(base_dir)
        
        # Create Config instance
        return cls(
            base_dir=base_dir or Path.cwd(),
            navd88_constants=navd_constants,
            chart_settings=chart_settings
        )