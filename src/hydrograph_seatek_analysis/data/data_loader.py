"""Data loading utilities for Seatek processing."""

import logging
from pathlib import Path
from typing import Tuple, Dict, Optional, List

import pandas as pd

from ..core.config import Config

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading and initial validation of data files."""

    def __init__(self, config: Config):
        """
        Initialize the data loader with configuration.
        
        Args:
            config: Application configuration
        """
        self.config = config

    def load_all_data(self) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Load all required data files.
        
        Returns:
            Tuple containing summary data and hydrograph data
            
        Raises:
            Exception: If an error occurs while loading data
        """
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
        """
        Load and validate summary data.
        
        Returns:
            DataFrame containing summary data
            
        Raises:
            FileNotFoundError: If the summary file doesn't exist
            ValueError: If required columns are missing
            Exception: If an error occurs while loading the file
        """
        try:
            summary_file = self.config.summary_file
            logger.debug(f"Loading summary data from: {summary_file}")
            
            if not summary_file.exists():
                raise FileNotFoundError(f"Summary file not found: {summary_file}")
                
            df = pd.read_excel(summary_file)
            self._validate_columns(df, ['River_Mile', 'Y_Offset', 'Num_Sensors'], "summary data")

            logger.debug(f"Summary data loaded successfully. Shape: {df.shape}")
            return df

        except Exception as e:
            logger.error(f"Error loading summary data: {str(e)}")
            raise

    def _load_hydro_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load and validate hydrograph data.
        
        Returns:
            Dictionary mapping sheet names to DataFrames containing hydrograph data
            
        Raises:
            FileNotFoundError: If the hydrograph file doesn't exist
            ValueError: If no valid hydrograph data sheets are found
            Exception: If an error occurs while loading the file
        """
        try:
            hydro_file = self.config.hydro_file
            logger.debug(f"Loading hydrograph data from: {hydro_file}")
            
            if not hydro_file.exists():
                raise FileNotFoundError(f"Hydrograph file not found: {hydro_file}")
                
            hydro_data = {}
            excel_file = pd.ExcelFile(hydro_file)

            for sheet_name in excel_file.sheet_names:
                if not sheet_name.startswith('RM_'):
                    continue

                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                try:
                    self._validate_columns(df, ['Time (Seconds)', 'Year'], f"sheet {sheet_name}")
                    hydro_data[sheet_name] = df
                    logger.debug(f"Loaded sheet {sheet_name}. Shape: {df.shape}")
                except ValueError as e:
                    logger.warning(f"Skipping sheet {sheet_name}: {str(e)}")
                    continue

            if not hydro_data:
                raise ValueError("No valid hydrograph data sheets found")

            return hydro_data

        except Exception as e:
            logger.error(f"Error loading hydrograph data: {str(e)}")
            raise
            
    @staticmethod
    def _validate_columns(df: pd.DataFrame, required_cols: List[str], context: str) -> None:
        """
        Validate that a DataFrame has all required columns.
        
        Args:
            df: DataFrame to validate
            required_cols: List of required column names
            context: Context for error message
            
        Raises:
            ValueError: If required columns are missing
        """
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in {context}: {missing_cols}")
            
    @staticmethod
    def get_available_river_miles(processed_dir: Path) -> List[float]:
        """
        Get list of available river miles from processed data directory.
        
        Args:
            processed_dir: Path to processed data directory
            
        Returns:
            List of river mile values
            
        Raises:
            FileNotFoundError: If the processed directory doesn't exist
        """
        if not processed_dir.exists():
            raise FileNotFoundError(f"Processed data directory not found: {processed_dir}")
            
        rm_files = list(processed_dir.glob("RM_*.xlsx"))
        river_miles = []
        
        for file_path in rm_files:
            try:
                rm_str = file_path.stem.split('_')[1]
                river_miles.append(float(rm_str))
            except (IndexError, ValueError):
                logger.warning(f"Skipping invalid river mile file: {file_path.name}")
                
        return sorted(river_miles)