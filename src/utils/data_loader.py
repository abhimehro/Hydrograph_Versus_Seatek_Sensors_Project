"""Data loading utilities for Seatek processing."""

import pandas as pd
import logging
from pathlib import Path
from typing import Tuple, Dict, Optional

from .config import Config

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading and initial validation of data files."""

    def __init__(self, config: Config):
        self.config = config

    def load_all_data(self) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Load all required data files."""
        try:
            summary_data = self._load_summary_data()
            hydro_data = self._load_hydro_data()
            return summary_data, hydro_data
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def _load_summary_data(self) -> pd.DataFrame:
        """Load and validate summary data."""
        try:
            df = pd.read_excel(self.config.summary_file)
            required_cols = {'River_Mile', 'Y_Offset', 'Num_Sensors'}

            if not all(col in df.columns for col in required_cols):
                raise ValueError("Missing required columns in summary data")

            return df

        except Exception as e:
            logger.error(f"Error loading summary data: {str(e)}")
            raise

    def _load_hydro_data(self) -> Dict[str, pd.DataFrame]:
        """Load and validate hydrograph data."""
        try:
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

            return hydro_data

        except Exception as e:
            logger.error(f"Error loading hydrograph data: {str(e)}")
            raise
