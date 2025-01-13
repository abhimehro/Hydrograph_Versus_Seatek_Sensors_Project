#!/usr/bin/env python3

"""
Seatek Sensor and Hydrograph Data Visualization
---------------------------------------------
Description: Processes and visualizes Seatek sensor data with hydrograph measurements.
Converts Seatek readings to NAVD88 elevations and creates professional visualizations.

Key Features:
- NAVD88 conversion with river mile-specific offsets
- Proper time axis in minutes
- Dual-axis visualization for Seatek and Hydrograph data
- Professional styling and formatting
- Comprehensive error handling and logging

Author: Abhi Mehrotra
Date: January 2025
Version: 2.0.0
"""

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union, Dict, List, Tuple

import logging

import matplotlib.pyplot as plt
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

REQUIRED_DIRECTORIES = [
    'data/raw',
    'data/processed',
    'output/combined'
]

class PathSetupError(Exception):
    """Custom exception for path setup errors."""
    pass

def validate_file_type(file_path: Path) -> bool:
    """Validate the file type."""
    return file_path.suffix in ['.xlsx', '.xls']

def check_file_size(file_path: Path) -> bool:
    """Check if the file size is within acceptable limits."""
    return file_path.stat().st_size < 100 * 1024 * 1024  # 100 MB

def validate_excel_structure(file_path: Path) -> bool:
    """Validate the structure of the Excel file."""
    try:
        df = pd.read_excel(file_path)
        required_cols = {'Time (Seconds)', 'Year'}
        return all(col in df.columns for col in required_cols)
    except Exception as e:
        logger.error(f"Excel validation error for {file_path}: {str(e)}")
        return False

def find_project_root() -> Path:
    """Find the project root directory by looking for key markers."""
    try:
        current_dir = Path(__file__).resolve().parent.parent.parent
        while current_dir.name:
            if any((current_dir / marker).exists() for marker in ['.git', 'pyproject.toml', 'setup.py']):
                return current_dir
            if current_dir.parent == current_dir:
                break
            current_dir = current_dir.parent
        raise PathSetupError("Could not find project root directory")
    except Exception as e:
        raise PathSetupError(f"Error finding project root: {str(e)}")

def setup_project_structure() -> Dict[str, Path]:
    """Set up and validate project directory structure."""
    try:
        project_root = find_project_root()
        directories = {}
        for dir_name in REQUIRED_DIRECTORIES:
            dir_path = project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            directories[dir_name] = dir_path
        return directories
    except Exception as e:
        raise PathSetupError(f"Failed to setup project structure: {str(e)}")

def verify_files_exist(required_files: Dict[Path, str]) -> Tuple[bool, List[str]]:
    """Verify existence and validity of required files."""
    errors = []
    for file_path, description in required_files.items():
        try:
            if not file_path.is_file():
                errors.append(f"Missing {description}")
                continue
            if not validate_file_type(file_path):
                errors.append(f"Invalid file type for {description}")
                continue
            if not check_file_size(file_path):
                errors.append(f"File too large: {description}")
                continue
            if not validate_excel_structure(file_path):
                errors.append(f"Invalid Excel structure: {description}")
                continue
        except Exception as e:
            errors.append(f"Error checking {description}: {str(e)}")
    return len(errors) == 0, errors

def check_file_accessibility(file_path: Path) -> Tuple[bool, Optional[str]]:
    """Check if file is accessible and readable."""
    try:
        if not file_path.exists():
            return False, "File does not exist"
        if not os.access(file_path, os.R_OK):
            return False, "File is not readable"
        with open(file_path, 'rb') as f:
            f.read(1)
        return True, None
    except Exception as e:
        return False, str(e)

def get_data_paths() -> Optional[Tuple[Path, Path, Path]]:
    """Get paths to required data files."""
    try:
        directories = setup_project_structure()
        rm_file = directories['data/processed'] / "RM_54.0.xlsx"
        summary_file = directories['data/raw'] / "Data_Summary.xlsx"
        hydro_file = directories['data/raw'] / "Hydrograph_Seatek_Data.xlsx"
        required_files = {
            rm_file: "River Mile data file",
            summary_file: "Summary data file",
            hydro_file: "Hydrograph data file"
        }
        success, errors = verify_files_exist(required_files)
        if not success:
            for error in errors:
                logger.error(error)
            return None
        for file_path in [rm_file, summary_file, hydro_file]:
            success, error = check_file_accessibility(file_path)
            if not success:
                logger.error(f"Access error for {file_path}: {error}")
                return None
        return rm_file, summary_file, hydro_file
    except Exception as e:
        logger.error(f"Error getting data paths: {str(e)}")
        return None

def cleanup_output_directory(output_dir: Path) -> None:
    """Clean up output directory before processing."""
    try:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True)
    except Exception as e:
        logger.warning(f"Error cleaning output directory: {str(e)}")

def create_backup(file_path: Path) -> Optional[Path]:
    """Create backup of important files."""
    try:
        backup_path = file_path.parent / f"{file_path.stem}_backup{file_path.suffix}"
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        logger.error(f"Backup failed for {file_path}: {str(e)}")
        return None

@dataclass
class DataMetrics:
    """Data structure to hold processing metrics."""
    original_rows: int = 0
    invalid_rows: int = 0
    zero_values: int = 0
    null_values: int = 0
    valid_rows: int = 0

    def to_dict(self) -> Dict[str, int]:
        """Convert metrics to dictionary."""
        return {
            'original_rows': self.original_rows,
            'invalid_rows': self.invalid_rows,
            'zero_values': self.zero_values,
            'null_values': self.null_values,
            'valid_rows': self.valid_rows
        }

class RiverMileData:
    """Container for river mile specific data and metadata."""

    def __init__(self, file_path: Path):
        """
        Initialize river mile data container.

        Args:
            file_path: Path to the river mile Excel file
        """
        self.file_path = file_path
        self.river_mile = self._extract_river_mile()
        self.data: Optional[pd.DataFrame] = None
        self.y_offset: float = 0
        self.sensors: List[str] = []

    def _extract_river_mile(self) -> float:
        """Extract river mile from filename."""
        try:
            rm_str = self.file_path.stem.split('_')[1]
            return float(rm_str)
        except (IndexError, ValueError) as e:
            raise ValueError(f"Invalid river mile file name: {self.file_path.name}") from e

    def load_data(self) -> None:
        """Load and validate data from Excel file."""
        try:
            self.data = pd.read_excel(self.file_path)
            self._validate_data()
            self._setup_sensors()
        except Exception as e:
            logger.error(f"Error loading {self.file_path.name}: {str(e)}")
            raise

    def _validate_data(self) -> None:
        """Validate data structure."""
        required_cols = {'Time (Seconds)', 'Year'}
        missing = required_cols - set(self.data.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def _setup_sensors(self) -> None:
        """Identify available sensor columns."""
        self.sensors = [col for col in self.data.columns if col.startswith('Sensor_')]
        if not self.sensors:
            raise ValueError("No sensor columns found")

class SeatekDataProcessor:
    """Handles Seatek sensor data processing and NAVD88 conversion."""

    def __init__(self, data_dir: Union[str, Path], summary_data: pd.DataFrame):
        """
        Initialize data processor.py.

        Args:
            data_dir: Directory containing river mile files
            summary_data: DataFrame with river mile metadata
        """
        self.data_dir = Path(data_dir)
        self.summary_data = summary_data
        self.river_mile_data: Dict[float, RiverMileData] = {}
        self._setup_offsets()

    def _setup_offsets(self) -> None:
        """Setup Y_Offset values for each river mile."""
        self.offsets = self.summary_data.set_index('River_Mile')['Y_Offset'].to_dict()

    def convert_to_navd88(
            self,
            data: pd.DataFrame,
            sensor: str,
            river_mile: float
    ) -> pd.DataFrame:
        """
        Convert Seatek sensor readings to NAVD88 elevation.

        Formula: =-[Raw + 1.9 - 0.32] × (400/30.48) + Y_Offset

        Args:
            data: Raw sensor data
            sensor: Sensor column name
            river_mile: River mile for offset lookup

        Returns:
            DataFrame with converted values
        """
        processed = data.copy()
        y_offset = self.offsets.get(river_mile, 0)

        # Convert time to minutes
        processed['Time (Minutes)'] = processed['Time (Seconds)'] / 60

        # Apply NAVD88 conversion
        raw_data = pd.to_numeric(processed[sensor], errors='coerce')
        processed[sensor] = -(raw_data + 1.9 - 0.32) * (400 / 30.48) + y_offset

        return processed

    def process_data(
            self,
            river_mile: float,
            year: int,
            sensor: str
    ) -> Tuple[pd.DataFrame, DataMetrics]:
        """
        Process data for a specific river mile, year, and sensor.

        Args:
            river_mile: River mile to process
            year: Year to process
            sensor: Sensor to process

        Returns:
            Tuple of (processed DataFrame, metrics)
        """
        if river_mile not in self.river_mile_data:
            raise ValueError(f"No data loaded for River Mile {river_mile}")

        rm_data = self.river_mile_data[river_mile]
        year_data = rm_data.data[rm_data.data['Year'] == year].copy()

        if year_data.empty:
            return pd.DataFrame(), DataMetrics()

        metrics = DataMetrics(original_rows=len(year_data))

        # Convert to NAVD88
        processed = self.convert_to_navd88(year_data, sensor, river_mile)

        # Handle missing values
        metrics.null_values = processed[sensor].isna().sum()
        metrics.zero_values = (processed[sensor] == 0).sum()

        # Remove invalid values
        valid_mask = processed[sensor].notna()
        processed = processed[valid_mask].copy()

        metrics.invalid_rows = metrics.original_rows - len(processed)
        metrics.valid_rows = len(processed)

        processed.sort_values('Time (Minutes)', inplace=True)
        self._log_metrics(metrics)

        return processed, metrics

    def load_data(self) -> None:
        """Load data from all river mile files."""
        try:
            rm_files = self._find_river_mile_files()

            if not rm_files:
                raise FileNotFoundError("No valid river mile files found")

            for file_path in rm_files:
                try:
                    rm_data = RiverMileData(file_path)
                    rm_data.load_data()
                    self.river_mile_data[rm_data.river_mile] = rm_data
                    logger.info(f"Loaded data for River Mile {rm_data.river_mile}")
                except Exception as e:
                    logger.error(f"Error loading {file_path.name}: {str(e)}")

        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def _find_river_mile_files(self) -> List[Path]:
        """Find all valid river mile Excel files."""
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

        rm_files = list(self.data_dir.glob("RM_*.xlsx"))
        return sorted(rm_files)

    @staticmethod
    def _log_metrics(metrics: DataMetrics) -> None:
        """Log data processing metrics."""
        logger.info(
            "Data processing metrics:\n"
            f"  Original rows: {metrics.original_rows}\n"
            f"  Invalid rows: {metrics.invalid_rows}\n"
            f"  Zero values: {metrics.zero_values}\n"
            f"  Null values: {metrics.null_values}\n"
            f"  Valid rows: {metrics.valid_rows}"
        )

class SeatekVisualizer:
    """Handles visualization of Seatek sensor data with hydrograph measurements."""

    def __init__(self):
        """Initialize visualizer with professional styling."""
        self._setup_style()

    def _setup_style(self) -> None:
        """Configure professional plot styling."""
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

    def create_visualization(
            self,
            data: pd.DataFrame,
            river_mile: float,
            year: int,
            sensor: str
    ) -> Optional[Figure]:
        """
        Create professional visualization with Seatek and Hydrograph data.

        Args:
            data: Processed data
            river_mile: River mile number
            year: Year of data
            sensor: Sensor column name

        Returns:
            Optional[Figure]: Matplotlib figure if successful
        """
        try:
            fig, ax1 = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor("white")

            # Plot Seatek data
            ax1.scatter(
                data['Time (Minutes)'],
                data[sensor],
                color='#FF7F0E',
                alpha=0.7,
                s=45,
                label=f'Sensor {sensor.split("_")[1]} (NAVD88)'
            )

            # Configure primary axis
            ax1.set_xlabel('Time (Minutes)', fontsize=12, labelpad=10)
            ax1.set_ylabel('Seatek Sensor Reading (NAVD88)', color='#FF7F0E', fontsize=12)
            ax1.tick_params(axis='y', labelcolor='#FF7F0E')
            ax1.grid(True, alpha=0.2, linestyle=':')

            # Add hydrograph if available
            if 'Hydrograph (Lagged)' in data.columns:
                ax2 = ax1.twinx()
                hydro_data = data[data['Hydrograph (Lagged)'].notna()]

                if not hydro_data.empty:
                    ax2.scatter(
                        hydro_data['Time (Minutes)'],
                        hydro_data['Hydrograph (Lagged)'],
                        color='#1F77B4',
                        alpha=0.7,
                        s=70,
                        marker='s',
                        label='Hydrograph (GPM)'
                    )
                    ax2.set_ylabel('Hydrograph (GPM)', color='#1F77B4', fontsize=12)
                    ax2.tick_params(axis='y', labelcolor='#1F77B4')

            # Set title and format plot
            plt.title(
                f'River Mile {river_mile:.1f} - Year {year}\n'
                f'Seatek Sensor {sensor.split("_")[1]} Data with Hydrograph',
                pad=20,
                fontsize=14
            )

            # Enhance spines
            for spine in ax1.spines.values():
                spine.set_linewidth(1.2)

            # Add legend
            lines1, labels1 = ax1.get_legend_handles_labels()
            if 'Hydrograph (Lagged)' in data.columns:
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax1.legend(
                    lines1 + lines2,
                    labels1 + labels2,
                    loc='upper right',
                    bbox_to_anchor=(0.99, 0.99),
                    framealpha=0.9,
                    fontsize=11
                )
            else:
                ax1.legend(
                    loc='upper right',
                    framealpha=0.9,
                    fontsize=11
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
        processor: Initialized data processor.py
        visualizer: Initialized visualizer
        output_base: Base output directory
    """
    import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for rm_data in processor.river_mile_data.values():
                for sensor in rm_data.sensors:
                    for year in sorted(rm_data.data['Year'].unique()):
                        futures.append(
                            executor.submit(
                                process_and_visualize,
                                processor,
                                visualizer,
                                output_base,
                                rm_data.river_mile,
                                year,
                                sensor
                            )
                        )
import concurrent.futures
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error in processing: {str(e)}")

    except Exception as e:
        logger.error(f"Error in process_river_mile_data: {str(e)}")


def process_and_visualize(
        processor: SeatekDataProcessor,
        visualizer: SeatekVisualizer,
        output_base: Path,
        river_mile: float,
        year: int,
        sensor: str
) -> None:
    """
    Process and visualize data for a specific river mile, year, and sensor.

    Args:
        processor: Initialized data processor.py
        visualizer: Initialized visualizer
        output_base: Base output directory
        river_mile: River mile number
        year: Year of data
        sensor: Sensor column name
    """
    try:
        processed_data, metrics = processor.process_data(river_mile, year, sensor)

        if not processed_data.empty:
            fig = visualizer.create_visualization(processed_data, river_mile, year, sensor)

            if fig:
                output_dir = output_base / f"RM_{river_mile:.1f}"
                output_dir.mkdir(parents=True, exist_ok=True)

                output_path = output_dir / f"RM_{river_mile:.1f}_Year_{year}_{sensor}_NAVD88.png"
                fig.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close(fig)
                logger.info(f"Generated visualization: {output_path}")

    except Exception as e:
        logger.error(f"Error processing and visualizing RM {river_mile}, Year {year}, Sensor {sensor}: {str(e)}")


def verify_files_exist() -> bool:
    """Verify required files exist."""
    project_root = Path(__file__).resolve().parent.parent.parent
    raw_dir = project_root / 'data/raw'
    processed_dir = project_root / 'data/processed'

    required_files = [
        raw_dir / 'Data_Summary.xlsx',
        raw_dir / 'Hydrograph_Seatek_Data.xlsx',
        processed_dir / 'RM_54.0.xlsx'
    ]

    logger.info(f"Current working directory: {Path.cwd()}")
    logger.info(f"Checking required files in directories: {raw_dir}, {processed_dir}")

    for file in required_files:
        logger.info(f"Checking file: {file} (absolute path: {file.resolve()})")

    missing_files = [str(file) for file in required_files if not file.exists()]

    if missing_files:
        logger.error(f"Missing required files:\n- " + "\n- ".join(missing_files))
        return False

    logger.info("All required files are present.")
    return True


def main():
    """Main execution function."""
    try:
        # Initialize
        from chart_generator import ChartGenerator
        chart_generator = ChartGenerator()

        # Verify required files
        if not verify_files_exist():
            logger.error("Required files are missing. Exiting.")
            sys.exit(1)

            # Load data
            summary_data, hydro_data = data_loader.load_all_data()

            # Load summary data for offsets
            summary_data = pd.read_excel(summary_path)

            # Initialize processor.py with summary data
            logger.info("Initializing data processor.py...")
            processor = SeatekDataProcessor(rm_path.parent, summary_data)

            # Create base output directory
            output_base = project_root / "output/charts"
            output_base.mkdir(parents=True, exist_ok=True)

            # Process each river mile
            for _, row in summary_data.iterrows():
                river_mile = row['River_Mile']
                num_sensors = row['Num_Sensors']
                sheet_name = f"RM_{river_mile:.1f}"

                if sheet_name not in hydro_data:
                    logging.warning(f"No data found for {sheet_name}")
                    continue

                logging.info(f"\nProcessing {sheet_name} with {num_sensors} sensors")

                # Get data for this river mile
                rm_data = hydro_data[sheet_name]

                # Create river mile directory
                rm_dir = output_base / sheet_name
                rm_dir.mkdir(parents=True, exist_ok=True)

                # Process each sensor
                for sensor_num in range(1, num_sensors + 1):
                    sensor = f"Sensor_{sensor_num}"
                    if sensor not in rm_data.columns:
                        logging.warning(f"Sensor column {sensor} not found in {sheet_name}")
                        continue

                    # Create sensor directory
                    sensor_dir = rm_dir / sensor
                    sensor_dir.mkdir(parents=True, exist_ok=True)

                    # Process each year
                    for year in range(1, 21):  # Years 1-20
                        # Process data
                        year_data = data_processor.process_river_mile_data(
                            rm_data,
                            river_mile,
                            year,
                            sensor
                        )

                        if year_data.empty:
                            logging.info(f"No data for {sheet_name} {sensor} Year {year}")
                            continue

                        # Create and save chart
                        fig = chart_generator.create_chart(
                            year_data,
                            river_mile,
                            year,
                            sensor
                        )

                        if fig:
                            output_path = sensor_dir / f"Year_{year}.png"
                            fig.savefig(
                                output_path,
                                dpi=300,
                                bbox_inches='tight',
                                facecolor='white'
                            )
                            plt.close(fig)
                            logging.info(f"Generated chart: {output_path}")
            except Exception as e:
            except Exception as e:
        raise
        raise


if __name__ == "__main__":
    main()