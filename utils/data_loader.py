"""Data loading utilities for Seatek processing."""

import logging
from typing import Tuple, Dict

import pandas as pd

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
            return summary_data, hydro_data
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def _load_summary_data(self) -> pd.DataFrame:
        """Load and validate summary data."""
        try:
            logger.debug(f"Loading summary data from: {self.config.summary_file}")
            df = pd.read_excel(self.config.summary_file)
            required_cols = {'River_Mile', 'Y_Offset', 'Num_Sensors'}

            if not all(col in df.columns for col in required_cols):
                missing_cols = required_cols - set(df.columns)
                raise ValueError(f"Missing required columns in summary data: {missing_cols}")

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
            excel_file = pd.ExcelFile(self.config.hydro_file)

            for sheet_name in excel_file.sheet_names:
                if not sheet_name.startswith('RM_'):
                    continue

                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                required_cols = {'Time (Seconds)', 'Year'}

                if not all(col in df.columns for col in required_cols):
                    logger.warning(f"Skipping sheet {sheet_name}: Missing required columns")
                    continue

                hydro_data[sheet_name] = df
                logger.debug(f"Loaded sheet {sheet_name}. Shape: {df.shape}")

            if not hydro_data:
                raise ValueError("No valid hydrograph data sheets found")

            return hydro_data

        except Exception as e:
            logger.error(f"Error loading hydrograph data: {str(e)}")
            raise
