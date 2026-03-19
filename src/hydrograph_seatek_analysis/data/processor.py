"""
Data processing utilities for Seatek sensor data.
This module implements decoupled filtering for sensor and hydrograph values,
and merges the two streams using a full outer join so that all valid sensor readings
(as well as all valid lagged hydrograph measurements) are preserved.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

import pandas as pd
import numpy as np

from ..core.config import Config

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
        """
        Initialize river mile data from file.

        Args:
            file_path: Path to the Excel file containing river mile data
        """
        self.file_path = file_path
        self.river_mile = self._extract_river_mile()
        self.data: Optional[pd.DataFrame] = None
        self.year_data_cache: Dict[int, pd.DataFrame] = {}
        self.y_offset: float = 0
        self.sensors: List[str] = []

    def _extract_river_mile(self) -> float:
        """
        Extract river mile from the filename.

        Returns:
            The river mile as a float

        Raises:
            ValueError: If the river mile cannot be extracted from the filename
        """
        try:
            rm_str = self.file_path.stem.split('_')[1]
            return float(rm_str)
        except (IndexError, ValueError) as e:
            raise ValueError(f"Invalid river mile file name: {self.file_path.name}") from e

    def load_data(self, max_file_size_bytes: int = 100 * 1024 * 1024) -> None:
        """
        Load and validate data from the Excel file.

        Args:
            max_file_size_bytes: Maximum allowed file size to prevent memory exhaustion

        Raises:
            Exception: If the data cannot be loaded or validated
        """
        try:
            # SECURITY: Limit file size to prevent memory exhaustion (DoS)
            if self.file_path.exists() and self.file_path.stat().st_size > max_file_size_bytes:
                raise ValueError(f"File size exceeds maximum allowed size ({max_file_size_bytes} bytes): {self.file_path}")

            required_cols = {'Time (Seconds)', 'Year'}

            # Optimization: load columns dynamically and load in a single pass
            seen_cols = []
            def filter_cols(col):
                seen_cols.append(col)
                return col in required_cols or str(col).startswith('Sensor_') or col == 'Hydrograph (Lagged)'

            self.data = pd.read_excel(self.file_path, usecols=filter_cols)
            cols = list(seen_cols)

            # Check required columns
            missing = [c for c in required_cols if c not in cols]
            if missing:
                raise ValueError(f"Missing required columns: {set(missing)}")

            # Find sensor columns
            self.sensors = [col for col in cols if str(col).startswith('Sensor_')]
            if not self.sensors:
                raise ValueError("No sensor columns found")

            # Keep original validation steps to ensure no methods are bypassed
            self._validate_data()
            self._setup_sensors()

            # Optimization: Pre-group data by year to avoid O(N) boolean masking
            # for each sensor during data processing.
            self.year_data_cache = {int(year): df for year, df in self.data.groupby('Year', sort=False)}
        except Exception as e:
            logger.error(f"Error loading {self.file_path.name}: {str(e)}")
            raise

    def _validate_data(self) -> None:
        """
        Ensure that required columns exist.

        Raises:
            ValueError: If required columns are missing
        """
        required_cols = {'Time (Seconds)', 'Year'}
        missing = required_cols - set(self.data.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def _setup_sensors(self) -> None:
        """
        Identify available sensor columns (those whose names begin with 'Sensor_').

        Raises:
            ValueError: If no sensor columns are found
        """
        self.sensors = [col for col in self.data.columns if col.startswith('Sensor_')]
        if not self.sensors:
            raise ValueError("No sensor columns found")


@dataclass
class SeatekDataProcessor:
    """
    Handles Seatek sensor data processing and conversion to NAVD88,
    while independently filtering sensor and hydrograph streams and merging them.

    The key modifications are as follows:
    • Data (including sensor values) are first converted (e.g. to NAVD88) and time is converted to minutes.
    • The hydrograph stream (column "Hydrograph (Lagged)") is filtered to retain only its nonzero, non-null values.
    • The sensor stream is filtered separately to retain only nonzero, non-null sensor values.
    • If the sensor data are completely missing (but hydrograph data exist), the hydrograph values can be forced to 0.
    • Finally, the two streams are merged with an outer join on "Time (Seconds)" so that all valid sensor points are preserved,
      in addition to all valid hydrograph points.
    """

    data_dir: Path
    summary_data: pd.DataFrame
    config: Config
    river_mile_data: Dict[float, RiverMileData] = field(default_factory=dict)
    offsets: Dict[float, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize processor after creation."""
        self._setup_offsets()

    def _setup_offsets(self) -> None:
        """Setup Y_Offset values for each river mile from the summary data."""
        self.offsets = self.summary_data.set_index('River_Mile')['Y_Offset'].to_dict()

    def convert_to_navd88(
        self,
        data: pd.DataFrame,
        sensor: str,
        river_mile: float,
        copy: bool = True
    ) -> pd.DataFrame:
        """
        Convert Seatek sensor readings to NAVD88 elevation using the
        river mile–specific offset, and convert time from seconds to minutes.

        Args:
            data: DataFrame containing sensor data.
            sensor: Name of the sensor column.
            river_mile: River mile for the data.
            copy: Whether to operate on a copy of ``data``. Defaults to ``True``.
                If ``True``, this method works on a copy and leaves the input
                ``data`` unchanged. If ``False``, this method mutates the
                passed-in DataFrame in place (it adds a ``"Time (Minutes)"``
                column and overwrites the specified ``sensor`` column) and
                returns the same object.

        Returns:
            DataFrame with converted sensor readings. When ``copy=False``,
            the returned DataFrame is the same object as the input ``data``.
        """
        processed = data.copy() if copy else data
        y_offset = self.offsets.get(river_mile, 0)
        # Convert time from seconds to minutes.
        processed['Time (Minutes)'] = processed['Time (Seconds)'] / 60.0

        # Convert the sensor column to numeric and apply the NAVD88 conversion.
        # Optimization: Avoid pd.to_numeric if the column is already numeric.
        if pd.api.types.is_numeric_dtype(processed[sensor]):
            raw_data = processed[sensor]
        else:
            raw_data = pd.to_numeric(processed[sensor], errors='coerce')
        # Get conversion constants from config
        constants = self.config.navd88_constants

        # Optimization: Pre-calculate scalar coefficients to minimize memory allocations
        # and array operations. Math simplification:
        # -(raw_data + A - B) * C + D  ==>  raw_data * (-C) + (D - (A - B) * C)
        m = -constants.scale_factor
        b = y_offset + (constants.offset_a - constants.offset_b) * m

        processed[sensor] = raw_data * m + b

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

        Args:
            river_mile: River mile to process
            year: Year to process
            sensor: Sensor column to process

        Returns:
            Tuple containing processed DataFrame and processing metrics

        Raises:
            ValueError: If no data is loaded for the specified river mile
        """
        if river_mile not in self.river_mile_data:
            raise ValueError(f"No data loaded for River Mile {river_mile}")

        rm_data = self.river_mile_data[river_mile]

        # Optimization: Use pre-grouped year data cache instead of O(N) boolean masking
        cached_year_data = rm_data.year_data_cache.get(year)
        if cached_year_data is None:
            year_data = pd.DataFrame()
        else:
            # Optimization: Only extract the required columns (Time, current sensor, and Hydrograph)
            # to avoid redundantly copying all other sensor columns on every iteration.
            cols = ['Time (Seconds)', sensor]
            if 'Hydrograph (Lagged)' in cached_year_data.columns:
                cols.append('Hydrograph (Lagged)')
            year_data = cached_year_data[cols].copy()
        metrics = ProcessingMetrics(original_rows=len(year_data))

        if year_data.empty:
            return pd.DataFrame(), metrics

        # Convert the data and sensor values.
        processed = self.convert_to_navd88(year_data, sensor, river_mile, copy=False)

        # Update processing metrics from the sensor column before filtering
        metrics.null_values = processed[sensor].isna().sum()
        metrics.zero_values = (processed[sensor] == 0).sum()

        has_hydro = 'Hydrograph (Lagged)' in processed.columns

        # Optimization: Use boolean masking instead of expensive outer pd.merge.
        # Create masks for valid data (nonzero and non-null) for each stream.
        # ⚡ Bolt Optimization: Cache underlying numpy arrays to avoid repeated
        # pandas Series indexing and intermediate object allocations.
        sensor_vals = processed[sensor].values
        # Need to handle potential object dtype or strings carefully if data wasn't fully numeric,
        # but in convert_to_navd88 we've already done arithmetic, so it should be numeric/nan.
        sensor_mask_arr = ~pd.isna(sensor_vals) & (sensor_vals != 0)
        sensor_mask = pd.Series(sensor_mask_arr, index=processed.index)

        if has_hydro:
            hydro_vals = processed['Hydrograph (Lagged)'].values
            hydro_mask_arr = ~pd.isna(hydro_vals) & (hydro_vals != 0)
            hydro_mask = pd.Series(hydro_mask_arr, index=processed.index)
            keep_mask = sensor_mask | hydro_mask
        else:
            hydro_mask = pd.Series(False, index=processed.index)
            keep_mask = sensor_mask

        # If no valid readings exist for both streams, return appropriate early empty df.
        if not keep_mask.any():
            if has_hydro:
                # Select and order columns identical to original pd.merge output
                if not sensor_mask.any():
                    cols = ['Time (Seconds)', 'Time (Minutes)', 'Hydrograph (Lagged)']
                elif not hydro_mask.any():
                    cols = ['Time (Seconds)', 'Time (Minutes)', sensor]
                else:
                    cols = ['Time (Seconds)', sensor, 'Time (Minutes)', 'Hydrograph (Lagged)']
            else:
                cols = ['Time (Seconds)', 'Time (Minutes)', sensor]

            merged = pd.DataFrame(columns=cols)
        else:
            # Filter processed data using the union mask
            merged = processed[keep_mask].copy()

            # Sub-masks on the filtered data
            sensor_keep = sensor_mask[keep_mask]
            hydro_keep = hydro_mask[keep_mask]

            # Nullify values that are not valid in their respective streams
            if has_hydro:
                if not sensor_keep.all():
                    merged.loc[~sensor_keep, sensor] = pd.NA if pd.api.types.is_object_dtype(merged[sensor]) else np.nan
                if not hydro_keep.all():
                    merged.loc[~hydro_keep, 'Hydrograph (Lagged)'] = pd.NA if pd.api.types.is_object_dtype(merged['Hydrograph (Lagged)']) else np.nan

                # If no valid sensor readings exist but hydrograph data exist, force hydrograph to 0
                if not sensor_mask.any() and hydro_mask.any():
                    merged['Hydrograph (Lagged)'] = 0

                # Select and order columns identical to original pd.merge output
                if not sensor_mask.any():
                    cols = ['Time (Seconds)', 'Time (Minutes)', 'Hydrograph (Lagged)']
                elif not hydro_mask.any():
                    cols = ['Time (Seconds)', 'Time (Minutes)', sensor]
                else:
                    cols = ['Time (Seconds)', sensor, 'Time (Minutes)', 'Hydrograph (Lagged)']
            else:
                if not sensor_keep.all():
                    merged.loc[~sensor_keep, sensor] = np.nan
                cols = ['Time (Seconds)', 'Time (Minutes)', sensor]

            merged = merged[cols]
            merged.sort_values('Time (Minutes)', inplace=True)

        metrics.valid_rows = len(merged)
        metrics.invalid_rows = metrics.original_rows - len(processed)
        metrics.log_metrics()

        return merged, metrics

    def load_data(self) -> None:
        """
        Load data from all river mile Excel files present in the data directory.

        Raises:
            FileNotFoundError: If no valid river mile files are found
            Exception: If an error occurs while loading data
        """
        try:
            rm_files = self._find_river_mile_files()

            if not rm_files:
                raise FileNotFoundError("No valid river mile files found")

            for file_path in rm_files:
                try:
                    rm_data = RiverMileData(file_path)
                    rm_data.load_data(max_file_size_bytes=self.config.max_file_size_bytes)
                    self.river_mile_data[rm_data.river_mile] = rm_data
                    logger.info(f"Loaded data for River Mile {rm_data.river_mile}")
                except Exception as e:
                    logger.error(f"Error loading {file_path.name}: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def _find_river_mile_files(self) -> List[Path]:
        """
        Find all Excel files in the data directory with names starting with 'RM_'.

        Returns:
            List of Paths to river mile Excel files

        Raises:
            FileNotFoundError: If the data directory doesn't exist
        """
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        rm_files = list(self.data_dir.glob("RM_*.xlsx"))
        return sorted(rm_files)
