"""
Data processing utilities for Seatek sensor data.
This module implements decoupled filtering for sensor and hydrograph values,
and merges the two streams using a full outer join so that all valid sensor readings
(as well as all valid lagged hydrograph measurements) are preserved.
"""

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
    """Container for river mile–specific data and metadata."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.river_mile = self._extract_river_mile()
        self.data: Optional[pd.DataFrame] = None
        self.y_offset: float = 0
        self.sensors: List[str] = []

    def _extract_river_mile(self) -> float:
        """Extract river mile from the filename."""
        try:
            rm_str = self.file_path.stem.split('_')[1]
            return float(rm_str)
        except (IndexError, ValueError) as e:
            raise ValueError(f"Invalid river mile file name: {self.file_path.name}") from e

    def load_data(self) -> None:
        """Load and validate data from the Excel file."""
        try:
            self.data = pd.read_excel(self.file_path)
            self._validate_data()
            self._setup_sensors()
        except Exception as e:
            logger.error(f"Error loading {self.file_path.name}: {str(e)}")
            raise

    def _validate_data(self) -> None:
        """Ensure that required columns exist."""
        required_cols = {'Time (Seconds)', 'Year'}
        missing = required_cols - set(self.data.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def _setup_sensors(self) -> None:
        """Identify available sensor columns (those whose names begin with 'Sensor_')."""
        self.sensors = [col for col in self.data.columns if col.startswith('Sensor_')]
        if not self.sensors:
            raise ValueError("No sensor columns found")


class SeatekDataProcessor:
    """Handles Seatek sensor data processing and conversion to NAVD88,
    while independently filtering sensor and hydrograph streams and merging them.

    The key modifications are as follows:
      • Data (including sensor values) are first converted (e.g. to NAVD88) and time is converted to minutes.
      • The hydrograph stream (column "Hydrograph (Lagged)") is filtered to retain only its nonzero, non-null values.
      • The sensor stream is filtered separately to retain only nonzero, non-null sensor values.
      • If the sensor data are completely missing (but hydrograph data exist), the hydrograph values can be forced to 0.
      • Finally, the two streams are merged with an outer join on "Time (Seconds)" so that all valid sensor points are preserved,
        in addition to all valid hydrograph points.
    """

    def __init__(self, data_dir: Union[str, Path], summary_data: pd.DataFrame):
        self.data_dir = Path(data_dir)
        self.summary_data = summary_data
        self.river_mile_data: Dict[float, RiverMileData] = {}
        self._setup_offsets()

    def _setup_offsets(self) -> None:
        """Setup Y_Offset values for each river mile from the summary data."""
        self.offsets = self.summary_data.set_index('River_Mile')['Y_Offset'].to_dict()

    def convert_to_navd88(
        self,
        data: pd.DataFrame,
        sensor: str,
        river_mile: float
    ) -> pd.DataFrame:
        """Convert Seatek sensor readings to NAVD88 elevation using the
        river mile–specific offset, and convert time from seconds to minutes.
        """
        processed = data.copy()
        y_offset = self.offsets.get(river_mile, 0)
        # Convert time from seconds to minutes.
        processed['Time (Minutes)'] = processed['Time (Seconds)'] / 60.0

        # Convert the sensor column to numeric and apply the NAVD88 conversion.
        raw_data = pd.to_numeric(processed[sensor], errors='coerce')
        # Conversion formula (adjust as necessary):
        # NAVD88_value = -(raw_data + 1.9 - 0.32) * (400 / 30.48) + y_offset
        processed[sensor] = -(raw_data + 1.9 - 0.32) * (400 / 30.48) + y_offset

        return processed

    def process_data(
            self,
            river_mile: float,
            year: int,
            sensor: str
    ) -> Tuple[pd.DataFrame, ProcessingMetrics]:
        """
        Process data for a given river mile, year, and sensor with fully decoupled filtering.

        Steps:
          • Extract data for the specified year.
          • Convert time and sensor readings (to NAVD88); this also creates a "Time (Minutes)" column.
          • Independently filter the hydrograph stream: keep only rows where "Hydrograph (Lagged)" is nonzero and non-null.
          • Independently filter the sensor stream: keep only rows where the sensor value is nonzero and non-null.
          • Update processing metrics (based on the sensor column).
          • (Optionally) – if sensor data are entirely missing but hydrograph data exist, force hydrograph values to 0.
          • Merge the two streams using an outer join on "Time (Seconds)" so that all valid sensor points and all
            valid hydrograph points are retained.
          • Finally, recalculate the time in minutes (if needed), sort by time, and update metrics.
        """
        if river_mile not in self.river_mile_data:
            raise ValueError(f"No data loaded for River Mile {river_mile}")

        rm_data = self.river_mile_data[river_mile]
        year_data = rm_data.data[rm_data.data['Year'] == year].copy()
        metrics = ProcessingMetrics(original_rows=len(year_data))

        if year_data.empty:
            return pd.DataFrame(), metrics

        # Convert the data and sensor values.
        processed = self.convert_to_navd88(year_data, sensor, river_mile)

        # Independently filter the hydrograph stream (if present).
        if 'Hydrograph (Lagged)' in processed.columns:
            hydro_df = processed[
                processed['Hydrograph (Lagged)'].notna() &
                (processed['Hydrograph (Lagged)'] != 0)
                ].copy()
        else:
            hydro_df = pd.DataFrame()

        # Independently filter the sensor stream.
        sensor_df = processed[
            processed[sensor].notna() & (processed[sensor] != 0)
            ].copy()

        # Update processing metrics from the sensor column.
        metrics.null_values = processed[sensor].isna().sum()
        metrics.zero_values = (processed[sensor] == 0).sum()

        # If there are no valid sensor readings but hydrograph data exist, force hydrograph to 0.
        if sensor_df.empty and not hydro_df.empty:
            hydro_df.loc[:, 'Hydrograph (Lagged)'] = 0

        # Merge the two streams using an outer join on "Time (Seconds)" so that
        # every valid sensor data point and every valid hydrograph value is preserved.
        merged = pd.merge(
            sensor_df[['Time (Seconds)', sensor]],
            hydro_df[['Time (Seconds)', 'Hydrograph (Lagged)']],
            on='Time (Seconds)',
            how='outer'
        )

        # Recalculate "Time (Minutes)" for the merged dataset.
        merged['Time (Minutes)'] = merged['Time (Seconds)'] / 60.0

        # Sort by time.
        merged.sort_values('Time (Minutes)', inplace=True)

        metrics.valid_rows = len(merged)
        metrics.invalid_rows = metrics.original_rows - len(processed)
        metrics.log_metrics()

        return merged, metrics

    def load_data(self) -> None:
        """Load data from all river mile Excel files present in the data directory."""
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
        """Find all Excel files in the data directory with names starting with 'RM_'."""
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        rm_files = list(self.data_dir.glob("RM_*.xlsx"))
        return sorted(rm_files)
