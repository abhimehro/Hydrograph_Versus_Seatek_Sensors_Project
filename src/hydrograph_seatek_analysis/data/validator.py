"""
Data validation utilities for Seatek sensor data.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

from utils.security import validate_file_size

from ..core.config import Config

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates data files and structure."""

    def __init__(self, config: Config):
        """
        Initialize validator with configuration.

        Args:
            config: Application configuration
        """
        self.config = config

    def _create_stateful_col_filter(
        self, keep_condition: Callable[[Any], bool]
    ) -> Tuple[Callable[[Any], bool], List[str]]:
        """Creates a stateful column filter that always includes the first column."""
        seen_cols: List[str] = []

        def filter_func(col: Any) -> bool:
            is_first = not seen_cols
            seen_cols.append(col)
            return keep_condition(col) or is_first

        return filter_func, seen_cols


    def _calculate_missing_values(self, df: pd.DataFrame, columns: set) -> pd.Series:
        """Helper to calculate missing values efficiently."""
        # ⚡ Bolt Optimization: Replace df[cols].isna().sum() with dictionary comprehension and np.count_nonzero
        # to avoid the overhead of creating an intermediate boolean DataFrame in memory and implicit type casting.
        return pd.Series({col: np.count_nonzero(pd.isna(df[col].values)) for col in columns})

    def validate_summary_file(self) -> Optional[Dict[str, Any]]:
        """
        Validate summary data file.

        Returns:
            Dictionary with validation results or None if validation fails
        """
        summary_file = self.config.summary_file

        try:
            # SECURITY: Limit file size to prevent memory exhaustion (DoS)
            try:
                validate_file_size(summary_file, self.config.max_file_size_bytes)
            except (ValueError, FileNotFoundError) as e:
                logger.error(str(e))
                return None

            required_cols = {"River_Mile", "Y_Offset", "Num_Sensors"}

            # Optimization: load columns dynamically and validate headers in a single pass
            seen_cols = []

            def filter_cols(col):
                seen_cols.append(col)
                return col in required_cols

            df = pd.read_excel(summary_file, usecols=filter_cols)
            columns = list(seen_cols)

            missing = [col for col in required_cols if col not in columns]
            if missing:
                logger.error(f"Missing required columns in summary data: {missing}")
                return None

            # Check data types
            if not pd.api.types.is_numeric_dtype(df["River_Mile"]):
                logger.warning("River_Mile column is not numeric")

            if not pd.api.types.is_numeric_dtype(df["Y_Offset"]):
                logger.warning("Y_Offset column is not numeric")

            if not pd.api.types.is_numeric_dtype(df["Num_Sensors"]):
                logger.warning("Num_Sensors column is not numeric")

            # Check for missing values
            missing_values = self._calculate_missing_values(df, required_cols)
            if missing_values.any():
                logger.warning(
                    f"Missing values detected in summary data: {missing_values}"
                )

            return {
                "file": summary_file.name,
                "columns": list(df.columns),
                "rows": len(df),
                "required_columns_present": len(missing) == 0,
                "river_miles": df["River_Mile"].tolist(),
                "missing_values": missing_values.to_dict(),
            }

        except Exception as e:
            logger.error(f"Error validating summary file: {str(e)}")
            return None



    def _extract_hydro_years(self, df: pd.DataFrame) -> Optional[List[int]]:
        """Helper to extract years safely."""
        if "Year" not in df.columns or len(df) == 0:
            return None
        if not df["Year"].notna().any():
            return None
        return sorted([int(y) for y in df["Year"].unique() if not pd.isna(y)])

    def _extract_hydro_time_range(self, df: pd.DataFrame) -> Optional[List[float]]:
        """Helper to extract time range safely."""
        if "Time (Seconds)" not in df.columns or len(df) == 0:
            return None
        if not df["Time (Seconds)"].notna().any():
            return None
        return [
            df["Time (Seconds)"].min(),
            df["Time (Seconds)"].max(),
        ]

    def _process_hydro_sheet(self, excel, hydro_file, sheet: str) -> Dict[str, Any]:
        """Process a single hydrograph sheet."""
        required_cols = {"Time (Seconds)", "Year"}

        # Optimization: check headers and conditionally load only required in single pass.
        # First column is unconditionally included as an anchor to guarantee a non-empty dataframe for row-count retrieval.
        filter_cols, seen_cols = self._create_stateful_col_filter(
            lambda c: c in required_cols
        )

        # SECURITY: Limit file size to prevent memory exhaustion (DoS)
        validate_file_size(hydro_file, self.config.max_file_size_bytes)

        df = pd.read_excel(excel, sheet_name=sheet, usecols=filter_cols)
        columns = list(seen_cols)
        missing = [col for col in required_cols if col not in columns]

        years = self._extract_hydro_years(df)
        time_range = self._extract_hydro_time_range(df)

        return {
            "name": sheet,
            "columns": columns,
            "rows": len(df),
            "required_columns_present": len(missing) == 0,
            "years": years,
            "time_range": time_range,
        }

    def validate_hydro_file(self) -> Optional[Dict[str, Any]]:
        """
        Validate hydrograph data file.

        Returns:
            Dictionary with validation results or None if validation fails
        """
        hydro_file = self.config.hydro_file

        try:
            # SECURITY: Limit file size to prevent memory exhaustion (DoS)
            try:
                validate_file_size(hydro_file, self.config.max_file_size_bytes)
            except (ValueError, FileNotFoundError) as e:
                logger.error(str(e))
                return None

            with pd.ExcelFile(hydro_file) as excel:
                sheets = excel.sheet_names
                rm_sheets = [s for s in sheets if s.startswith("RM_")]

                if not rm_sheets:
                    logger.error("No river mile sheets found in hydrograph file")
                    return None

                sheet_info = [
                    self._process_hydro_sheet(excel, hydro_file, sheet)
                    for sheet in rm_sheets
                ]

                return {
                    "file": hydro_file.name,
                    "sheets": sheet_info,
                    "river_mile_sheets": rm_sheets,
                }

        except Exception as e:
            logger.error(f"Error validating hydrograph file: {str(e)}")
            return None



    def _extract_processed_year_range(self, df: pd.DataFrame) -> Optional[List[int]]:
        if "Year" not in df.columns or len(df) == 0:
            return None
        return [int(df["Year"].min()), int(df["Year"].max())]

    def _extract_processed_time_range(self, df: pd.DataFrame) -> Optional[List[float]]:
        if "Time (Seconds)" not in df.columns or len(df) == 0:
            return None
        return [
            float(df["Time (Seconds)"].min()),
            float(df["Time (Seconds)"].max()),
        ]

    def _process_processed_file(self, file_path, required_cols) -> Dict[str, Any]:
        """Process a single processed river mile file."""
        # Extract river mile
        try:
            rm_str = file_path.stem.split("_")[1]
            river_mile = float(rm_str)
        except (IndexError, ValueError):
            logger.warning(f"Invalid river mile file name: {file_path.name}")
            river_mile = None

        # Optimization: load columns dynamically and load in a single pass.
        # First column is unconditionally included as an anchor so df may include a column that is neither required nor a Sensor_ column.
        filter_cols, seen_cols = self._create_stateful_col_filter(
            lambda c: c in required_cols or str(c).startswith("Sensor_")
        )

        df = pd.read_excel(file_path, usecols=filter_cols)
        columns = list(seen_cols)

        missing = [col for col in required_cols if col not in columns]
        sensor_cols = [col for col in columns if str(col).startswith("Sensor_")]

        # Check data range
        year_range = self._extract_processed_year_range(df)
        time_range = self._extract_processed_time_range(df)

        return {
            "file": file_path.name,
            "river_mile": river_mile,
            "columns": columns,
            "rows": len(df),
            "required_columns_present": len(missing) == 0,
            "sensor_columns": sensor_cols,
            "year_range": year_range,
            "time_range": time_range,
        }

    def validate_processed_files(self) -> List[Dict[str, Any]]:
        """
        Validate processed river mile files.

        Returns:
            List of dictionaries with validation results for each file
        """
        results = []
        processed_dir = self.config.processed_dir

        if not processed_dir.exists():
            logger.error(f"Processed directory not found: {processed_dir}")
            return results

        rm_files = list(processed_dir.glob("RM_*.xlsx"))
        required_cols = {"Time (Seconds)", "Year"}

        for file_path in rm_files:
            try:
                # SECURITY: Limit file size to prevent memory exhaustion (DoS)
                try:
                    validate_file_size(file_path, self.config.max_file_size_bytes)
                except (ValueError, FileNotFoundError) as e:
                    logger.error(str(e))
                    results.append({"file": file_path.name, "error": str(e)})
                    continue

                res = self._process_processed_file(file_path, required_cols)
                results.append(res)

            except Exception as e:
                logger.error(
                    f"Error validating processed file {file_path.name}: {str(e)}"
                )
                results.append({"file": file_path.name, "error": str(e)})

        return results

    def run_validation(self) -> Dict[str, Any]:
        """
        Run full validation on all data files.

        Returns:
            Dictionary with validation results
        """
        logger.info("Running data validation")

        summary_validation = self.validate_summary_file()
        hydro_validation = self.validate_hydro_file()
        processed_validation = self.validate_processed_files()

        # Check for consistency between summary and processed files
        river_mile_consistency = None

        if summary_validation and processed_validation:
            # Extract river miles from summary and processed files
            summary_rms = set(summary_validation.get("river_miles", []))
            processed_rms = {
                r.get("river_mile")
                for r in processed_validation
                if r.get("river_mile") is not None
            }

            # Check for consistency
            missing_rms = summary_rms - processed_rms
            extra_rms = processed_rms - summary_rms

            river_mile_consistency = {
                "all_summary_rms_processed": len(missing_rms) == 0,
                "missing_processed_rms": list(missing_rms),
                "extra_processed_rms": list(extra_rms),
            }

        return {
            "summary": summary_validation,
            "hydrograph": hydro_validation,
            "processed": processed_validation,
            "river_mile_consistency": river_mile_consistency,
            "overall_valid": (
                summary_validation is not None
                and hydro_validation is not None
                and len(processed_validation) > 0
            ),
        }
