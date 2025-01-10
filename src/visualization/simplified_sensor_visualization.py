# simplified_sensor_visualization.py

#!/usr/bin/env python3

"""
Seatek Sensor Visualization Script
---------------------------
Description: This script processes and visualizes Seatek sensor data from river mile Excel files.
Purpose: It handles files named in the format 'RM_XX.X.xlsx' where XX.X is the river mile marker.

Author: Abhi Mehrotra
Date: January 2025
---------------------------
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union, Dict, List, Tuple

# Import path utilities
try:
    from .path_setup import verify_files_exist, get_data_paths
except ImportError:
    # Fallback for direct script execution
    from path_setup import verify_files_exist, get_data_paths

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sensor_visualization.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)


class RiverMileData:
    """Data structure to hold river mile information."""

    def __init__(self, file_path: Path):
        """
        Initialize river mile data container.

        Args:
            file_path (Path): Path to the river mile Excel file
        """
        self.file_path = file_path
        self.river_mile = self._extract_river_mile()
        self.data: Optional[pd.DataFrame] = None

    def _extract_river_mile(self) -> float:
        """
        Extract river mile number from filename.

        Returns:
            float: River mile number

        Raises:
            ValueError: If river mile cannot be extracted from filename
        """
        try:
            rm_str = self.file_path.stem.split('_')[1]
            return float(rm_str)
        except (IndexError, ValueError) as e:
            raise ValueError(f"Invalid river mile file name: {self.file_path.name}") from e


class SeatekDataProcessor:
    """Handles Seatek sensor data processing operations."""

    def __init__(self, data_dir: Union[str, Path]):
        """
        Initialize the data processor.

        Args:
            data_dir: Directory containing river mile files
        """
        self.data_dir = Path(data_dir)
        self.river_mile_data: Dict[float, RiverMileData] = {}

    def find_river_mile_files(self) -> List[Path]:
        """
        Find all valid river mile Excel files in the data directory.

        Returns:
            List[Path]: List of paths to valid river mile files

        Raises:
            FileNotFoundError: If data directory doesn't exist
        """
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

        # Find all Excel files matching pattern
        rm_files = list(self.data_dir.glob("RM_*.xlsx"))

        if not rm_files:
            logger.warning(f"No river mile files found in {self.data_dir}")
            return []

        # Validate filenames
        valid_files = []
        for file in rm_files:
            try:
                RiverMileData(file)
                valid_files.append(file)
            except ValueError as e:
                logger.warning(str(e))

        return sorted(valid_files)

    def load_data(self) -> None:
        """
        Load data from all valid river mile files.

        Raises:
            FileNotFoundError: If no valid files are found
        """
        try:
            rm_files = self.find_river_mile_files()

            if not rm_files:
                raise FileNotFoundError(
                    f"No valid river mile files found in {self.data_dir}"
                )

            for file_path in rm_files:
                try:
                    rm_data = RiverMileData(file_path)
                    rm_data.data = pd.read_excel(file_path)
                    self._validate_data_structure(rm_data)
                    self.river_mile_data[rm_data.river_mile] = rm_data
                    logger.info(f"Loaded data for River Mile {rm_data.river_mile}")

                except Exception as e:
                    logger.error(f"Error processing {file_path.name}: {str(e)}")

        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def _validate_data_structure(self, rm_data: RiverMileData) -> None:
        """
        Validate data structure of a river mile file.

        Args:
            rm_data: RiverMileData object to validate

        Raises:
            ValueError: If required columns are missing
        """
        required_columns = {'Time (Seconds)', 'Year'}
        sensor_columns = [
            col for col in rm_data.data.columns
            if col.startswith('Sensor_')
        ]

        if not sensor_columns:
            raise ValueError(
                f"No sensor columns found in {rm_data.file_path.name}"
            )

        missing_columns = required_columns - set(rm_data.data.columns)
        if missing_columns:
            raise ValueError(
                f"Missing required columns in {rm_data.file_path.name}: "
                f"{missing_columns}"
            )

    def _log_processing_metrics(self, metrics: Dict[str, int]) -> None:
        """Log data processing metrics."""
        logger.info(
            f"Data processing metrics:\n"
            f"  Original rows: {metrics['original_rows']}\n"
            f"  Invalid rows: {metrics['invalid_rows']}\n"
            f"  Zero values: {metrics['zero_values']}\n"
            f"  Null values: {metrics['null_values']}\n"
            f"  Valid rows: {metrics['original_rows'] - metrics['invalid_rows']}"
        )

    def process_sensor_data(
            self,
            data: pd.DataFrame,
            sensor: str
    ) -> Tuple[pd.DataFrame, Dict[str, int]]:
        metrics = {
            'original_rows': len(data),
            'invalid_rows': 0,
            'zero_values': 0,
            'null_values': 0
        }

        processed = data.copy()
        processed[sensor] = pd.to_numeric(processed[sensor], errors='coerce')

        metrics['null_values'] = processed[sensor].isna().sum()
        metrics['zero_values'] = (processed[sensor] == 0).sum()

        valid_mask = (processed[sensor].notna()) & (processed[sensor] != 0)
        processed = processed[valid_mask].copy()

        # Invert the values here and make them positive
        processed[sensor] = processed[sensor].abs()

        metrics['invalid_rows'] = metrics['original_rows'] - len(processed)
        processed.sort_values('Time (Seconds)', inplace=True)

        self._log_processing_metrics(metrics)
        return processed, metrics


    def _log_processing_metrics(self, metrics: Dict[str, int]) -> None:
        """Log data processing metrics."""
        logger.info(
            f"Data processing metrics:\n"
            f"  Original rows: {metrics['original_rows']}\n"
            f"  Invalid rows: {metrics['invalid_rows']}\n"
            f"  Zero values: {metrics['zero_values']}\n"
            f"  Null values: {metrics['null_values']}\n"
            f"  Valid rows: {metrics['original_rows'] - metrics['invalid_rows']}"
        )


class SeatekVisualizer:
    """Manages Seatek sensor data visualization."""

    def __init__(self):
        """Initialize visualizer with custom style settings."""
        self._setup_style()

    def _setup_style(self) -> None:
        """Configure plot styling."""
        sns.set_style("whitegrid", {
            "grid.linestyle": ":",
            "grid.alpha": 0.2,
            "axes.edgecolor": "#333333",
            "axes.linewidth": 1.2,
            "grid.color": "#CCCCCC",
        })

        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial"],
            "font.size": 11,
            "figure.figsize": (12, 8),
            "figure.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.2
        })

    def _format_sensor_name(self, sensor: str) -> str:
        """Format sensor name by removing underscores."""
        return sensor.replace('_', ' ')

    def create_visualization(
            self,
            data: pd.DataFrame,
            river_mile: float,
            year: int,
            sensor: str
    ) -> Optional[Figure]:
        try:
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor("white")

            # Convert time to hours
            time_hours = data['Time (Seconds)'] / 3600

            # Plot sensor data
            ax.scatter(time_hours,
                       data[sensor],  # Use the processed positive values
                       color='#FF7F0E',  # Professional orange
                       alpha=0.7,
                       s=45,
                       label=f'{self._format_sensor_name(sensor)} Elevation')

            # Customize axes
            ax.set_xlabel('Time (Hours)', fontsize=12, labelpad=10)
            ax.set_ylabel('Elevation (cm)', fontsize=12, labelpad=10)

            # Get current y-axis limits
            y_min, y_max = ax.get_ylim()

            # Invert the y-axis
            ax.set_ylim(y_max, y_min)

            # Update y-tick labels to show positive values
            y_ticks = ax.get_yticks()
            ax.set_yticks(y_ticks)
            ax.set_yticklabels([f'{abs(y):.1f}' for y in y_ticks])

            # Set title with formatted sensor name
            ax.set_title(
                f'River Mile {river_mile:.1f} - Year {year}\n'
                f'{self._format_sensor_name(sensor)} Elevation Data',
                pad=20,
                fontsize=14
            )

            # Enhance grid and spines
            ax.grid(True, alpha=0.2, linestyle=':')
            for spine in ax.spines.values():
                spine.set_linewidth(1.2)

            # Customize ticks
            ax.tick_params(axis='both', labelsize=11)

            # Add legend with enhanced styling
            ax.legend(
                loc='upper right',
                framealpha=0.9,
                fontsize=11,
                edgecolor='#CCCCCC'
            )

            plt.tight_layout()
            return fig

        except Exception as e:
            logger.error(f"Visualization error: {str(e)}")
            return None


def process_river_mile_data(
        processor: SeatekDataProcessor,
        visualizer: SeatekVisualizer,
        output_base: Path
) -> None:
    """
    Process and visualize data for all river miles.

    Args:
        processor: Initialized SeatekDataProcessor
        visualizer: Initialized SeatekVisualizer
        output_base: Base directory for output files
    """
    for rm_data in processor.river_mile_data.values():
        sensors = [
            col for col in rm_data.data.columns
            if col.startswith('Sensor_')
        ]

        for sensor in sensors:
            for year in sorted(rm_data.data['Year'].unique()):
                year_data = rm_data.data[rm_data.data['Year'] == year]
                processed_data, metrics = processor.process_sensor_data(
                    year_data, sensor
                )

                if not processed_data.empty:
                    fig = visualizer.create_visualization(
                        processed_data, rm_data.river_mile, year, sensor
                    )

                    if fig:
                        output_dir = (
                            output_base /
                            f"RM_{rm_data.river_mile:.1f}"
                        )
                        output_dir.mkdir(parents=True, exist_ok=True)

                        output_path = (
                            output_dir /
                            f"RM_{rm_data.river_mile:.1f}_"
                            f"Year_{year}_{sensor}.png"
                        )
                        fig.savefig(output_path, dpi=300, bbox_inches='tight')
                        plt.close(fig)

                        logger.info(f"Generated visualization: {output_path}")


def verify_files_exist() -> bool:
    """Verify that all required files exist in the raw data directory."""
    project_root = Path("/Users/abhimehrotra/PycharmProjects/Hydrograph_Versus_Seatek_Sensors_Project")
    raw_dir = project_root / "data/raw"

    required_files = [
        raw_dir / "Data_Summary.xlsx",
        raw_dir / "Hydrograph_Seatek_Data.xlsx"
    ]

    logger.info(f"Current working directory: {Path.cwd()}")
    logger.info(f"Checking required files in directory: {raw_dir}")

    for file in required_files:
        logger.info(f"Checking file: {file} (absolute path: {file.resolve()})")

    missing_files = [str(file) for file in required_files if not file.exists()]

    if missing_files:
        logger.error(f"Missing required files:\n- " + "\n- ".join(missing_files))
        return False

    logger.info("All required files are present.")
    return True


def check_file_accessibility(file_path: Path) -> bool:
    """
    Check if the file is accessible and can be read.

    Args:
        file_path (Path): Path to the file to check

    Returns:
        bool: True if file is accessible, False otherwise
    """
    try:
        pd.read_excel(file_path)
        logger.info(f"File {file_path} is accessible and readable.")
        return True
    except Exception as e:
        logger.error(f"Error accessing file {file_path}: {str(e)}")
        return False


def main():
    """
    Main function to process and visualize Seatek sensor data.

    This function:
    1. Verifies required files exist and are accessible
    2. Initializes data processor and visualizer
    3. Creates output directories
    4. Processes and visualizes sensor data
    5. Handles any errors that occur during execution
    """
    try:
        # First verify all files exist
        if not verify_files_exist():
            logger.error("Required files are missing. Please check file locations.")
            sys.exit(1)

        # Check file accessibility
        project_root = Path("/Users/abhimehrotra/PycharmProjects/Hydrograph_Versus_Seatek_Sensors_Project")
        raw_dir = project_root / "data/raw"
        required_files = [
            raw_dir / "Data_Summary.xlsx",
            raw_dir / "Hydrograph_Seatek_Data.xlsx"
        ]

        for file in required_files:
            if not check_file_accessibility(file):
                logger.error(f"File {file} is not accessible. Please check file permissions and integrity.")
                sys.exit(1)

        # Get verified paths
        paths = get_data_paths()
        if not paths:
            logger.error("Could not get valid paths to required files.")
            sys.exit(1)

        rm_path, summary_path, hydro_path = paths

        # Set up output directory structure
        output_dir = Path("output/sensor_only")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize processor with verified processed directory
        logger.info("Initializing data processor...")
        processor = SeatekDataProcessor(rm_path.parent)

        # Load and validate data
        logger.info("Loading and validating data...")
        processor.load_data()

        # Initialize visualizer
        logger.info("Initializing visualizer...")
        visualizer = SeatekVisualizer()

        # Process data and create visualizations
        logger.info("Starting data processing and visualization...")
        process_river_mile_data(processor, visualizer, output_dir)

        logger.info("Seatek sensor visualization completed successfully")
        logger.info(f"Output files can be found in: {output_dir.absolute()}")

    except FileNotFoundError as e:
        logger.error(f"File not found error: {str(e)}")
        sys.exit(1)
    except PermissionError as e:
        logger.error(f"Permission error accessing files: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Set up logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('sensor_visualization.log', mode='a')
        ]
    )

    try:
        main()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)