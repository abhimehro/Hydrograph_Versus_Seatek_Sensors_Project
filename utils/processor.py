"""Data processing utilities for Seatek sensor data."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class ProcessingMetrics:
    """Metrics for data processing operations."""
    original_rows: int = 0
    invalid_rows: int = 0
    zero_values: int = 0
    null_values: int = 0
    valid_rows: int = 0

    def log_metrics(self) -> None:
        """Log processing metrics."""
        logger.info(
            "Data processing metrics:\n"
            f"  Original rows: {self.original_rows}\n"
            f"  Invalid rows: {self.invalid_rows}\n"
            f"  Zero values: {self.zero_values}\n"
            f"  Null values: {self.null_values}\n"
            f"  Valid rows: {self.valid_rows}"
        )

class RiverMileData:
    """Container for river mile specific data and metadata."""

    def __init__(self, file_path: Path):
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
        """Convert Seatek sensor readings to NAVD88 elevation."""
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
    ) -> Tuple[pd.DataFrame, ProcessingMetrics]:
        """Process data for a specific river mile, year, and sensor."""
        if river_mile not in self.river_mile_data:
            raise ValueError(f"No data loaded for River Mile {river_mile}")

        rm_data = self.river_mile_data[river_mile]
        year_data = rm_data.data[rm_data.data['Year'] == year].copy()

        metrics = ProcessingMetrics(original_rows=len(year_data))

        if year_data.empty:
            return pd.DataFrame(), metrics

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
        metrics.log_metrics()

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
