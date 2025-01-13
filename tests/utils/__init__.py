"""
Seatek Sensor Data Processing Utilities
-------------------------------------
A package for processing and visualizing Seatek sensor data with hydrograph measurements.

Modules:
    - config: Configuration management
    - data_loader: Data loading and validation
    - processor: Data processing and NAVD88 conversion
    - visualizer: Data visualization
    - chart_generator: Chart generation utilities
"""

from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple, Union

# Version information
__version__ = "2.0.0"
__author__ = "Abhi Mehrotra"
__email__ = "your.email@example.com"  # Replace with your email

# Setup package-level logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Import main classes and functions for easier access
from utils.config import Config
from utils.data_loader import DataLoader
from utils.processor import (
    ProcessingMetrics,
    RiverMileData,
    SeatekDataProcessor
)
from utils.visualizer import SeatekVisualizer
from utils.chart_generator import ChartGenerator

# Define what should be imported with "from utils import *"
__all__ = [
    # Classes
    'Config',
    'DataLoader',
    'ProcessingMetrics',
    'RiverMileData',
    'SeatekDataProcessor',
    'SeatekVisualizer',
    'ChartGenerator',

    # Version info
    '__version__',
    '__author__',
    '__email__'
]

# Package metadata
PACKAGE_ROOT = Path(__file__).parent.parent
DATA_DIR = PACKAGE_ROOT / "data"
OUTPUT_DIR = PACKAGE_ROOT / "output"
LOGS_DIR = PACKAGE_ROOT / "logs"

# Ensure required directories exist
for directory in [DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def get_version() -> str:
    """Return the package version."""
    return __version__


def setup_logging(
        level: int = logging.INFO,
        log_file: Optional[Union[str, Path]] = None
) -> None:
    """
    Setup logging configuration for the package.

    Args:
        level: Logging level (default: logging.INFO)
        log_file: Optional path to log file
    """
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_package_info() -> Dict[str, str]:
    """
    Return package information.

    Returns:
        Dict containing package metadata
    """
    return {
        'version': __version__,
        'author': __author__,
        'email': __email__,
        'package_root': str(PACKAGE_ROOT),
        'data_dir': str(DATA_DIR),
        'output_dir': str(OUTPUT_DIR),
        'logs_dir': str(LOGS_DIR)
    }


def validate_environment() -> Tuple[bool, List[str]]:
    """
    Validate the package environment.

    Returns:
        Tuple of (success: bool, errors: List[str])
    """
    errors = []

    # Check required directories
    required_dirs = {
        'data': DATA_DIR,
        'output': OUTPUT_DIR,
        'logs': LOGS_DIR
    }

    for name, path in required_dirs.items():
        if not path.exists():
            errors.append(f"Missing required directory: {name} ({path})")

    # Check data subdirectories
    required_data_dirs = ['raw', 'processed']
    for subdir in required_data_dirs:
        path = DATA_DIR / subdir
        if not path.exists():
            errors.append(f"Missing required data subdirectory: {subdir}")

    return len(errors) == 0, errors


# Initialize package
try:
    success, errors = validate_environment()
    if not success:
        logger.warning("Package environment validation failed:")
        for error in errors:
            logger.warning(f"  - {error}")
except Exception as e:
    logger.error(f"Error initializing package: {str(e)}")


def get_processor(
        data_dir: Optional[Union[str, Path]] = None,
        summary_data: Optional['pd.DataFrame'] = None
) -> SeatekDataProcessor:
    """
    Convenience function to create a configured SeatekDataProcessor instance.

    Args:
        data_dir: Optional custom data directory
        summary_data: Optional pre-loaded summary data

    Returns:
        Configured SeatekDataProcessor instance
    """
    if data_dir is None:
        data_dir = DATA_DIR / 'processed'

    if summary_data is None:
        config = Config()
        loader = DataLoader(config)
        summary_data, _ = loader.load_all_data()

    return SeatekDataProcessor(data_dir, summary_data)


def get_visualizer() -> SeatekVisualizer:
    """
    Convenience function to create a configured SeatekVisualizer instance.

    Returns:
        Configured SeatekVisualizer instance
    """
    return SeatekVisualizer()


def get_chart_generator() -> ChartGenerator:
    """
    Convenience function to create a configured ChartGenerator instance.

    Returns:
        Configured ChartGenerator instance
    """
    return ChartGenerator()
