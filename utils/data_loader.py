"""Data loading utilities for Seatek processing."""

import logging
from typing import Dict, Tuple

import pandas as pd

from utils.security import validate_file_size

from .config import Config

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading and initial validation of data files."""

    def __init__(self, config: Config):
        self.config = config

    def load_all_data(self) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Load all required data files."""
        try:
            logger.debug("Loading summary and hydrograph data...")
            summary_data = self._load_summary_data()
            hydro_data = self._load_hydro_data()
            logger.debug("Data loading completed successfully")
            return (summary_data, hydro_data)
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def _load_summary_data(self) -> pd.DataFrame:
        """Load and validate summary data."""
        try:
            logger.debug(f"Loading summary data from: {self.config.summary_file}")
            validate_file_size(
                self.config.summary_file, self.config.max_file_size_bytes
            )
            required_cols = {"River_Mile", "Y_Offset", "Num_Sensors"}

            # ⚡ Bolt Optimization: load columns dynamically to avoid checking headers and reloading
            # This is an optimization for reading excel files in a single pass to reduce memory overhead
            df = pd.read_excel(
                self.config.summary_file, usecols=lambda c: c in required_cols
            )
            missing_cols = required_cols - set(df.columns)
            if missing_cols:
                raise ValueError(
                    f"Missing required columns in summary data: {missing_cols}"
                )
            logger.debug(f"Summary data loaded successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading summary data: {str(e)}")
            raise

    def _load_hydro_data(self) -> Dict[str, pd.DataFrame]:
        """Load and validate hydrograph data."""
        try:
            logger.debug(f"Loading hydrograph data from: {self.config.hydro_file}")
            hydro_data = {}
            validate_file_size(self.config.hydro_file, self.config.max_file_size_bytes)
            excel_file = pd.ExcelFile(self.config.hydro_file)
            required_cols = {"Time (Seconds)", "Year"}
            for sheet_name in excel_file.sheet_names:
                if not sheet_name.startswith("RM_"):
                    continue
                validate_file_size(
                    self.config.hydro_file, self.config.max_file_size_bytes
                )

                # ⚡ Bolt Optimization: Load only required columns and sensor/hydrograph columns
                # to reduce memory usage and speed up loading for large Excel sheets
                df = pd.read_excel(
                    excel_file,
                    sheet_name=sheet_name,
                    usecols=lambda c: c in required_cols
                    or str(c).startswith("Sensor_")
                    or c == "Hydrograph (Lagged)",
                )

                missing_cols = required_cols - set(df.columns)
                if missing_cols:
                    logger.warning(
                        f"Skipping sheet {sheet_name}: Missing required columns: {missing_cols}"
                    )
                    continue
                hydro_data[sheet_name] = df
                logger.debug(f"Loaded sheet {sheet_name}. Shape: {df.shape}")
            if not hydro_data:
                raise ValueError("No valid hydrograph data sheets found")
            return hydro_data
        except Exception as e:
            logger.error(f"Error loading hydrograph data: {str(e)}")
            raise
