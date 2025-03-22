"""
Data validation utilities for Seatek sensor data.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd

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
    
    def validate_summary_file(self) -> Optional[Dict[str, Any]]:
        """
        Validate summary data file.
        
        Returns:
            Dictionary with validation results or None if validation fails
        """
        summary_file = self.config.summary_file
        
        try:
            if not summary_file.exists():
                logger.error(f"Summary file not found: {summary_file}")
                return None
                
            df = pd.read_excel(summary_file)
            
            # Check required columns
            required_cols = ['River_Mile', 'Y_Offset', 'Num_Sensors']
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                logger.error(f"Missing required columns in summary data: {missing}")
                return None
                
            # Check data types
            if not pd.api.types.is_numeric_dtype(df['River_Mile']):
                logger.warning("River_Mile column is not numeric")
                
            if not pd.api.types.is_numeric_dtype(df['Y_Offset']):
                logger.warning("Y_Offset column is not numeric")
                
            if not pd.api.types.is_numeric_dtype(df['Num_Sensors']):
                logger.warning("Num_Sensors column is not numeric")
                
            # Check for missing values
            missing_values = df[required_cols].isna().sum()
            if missing_values.sum() > 0:
                logger.warning(f"Missing values detected in summary data: {missing_values}")
                
            return {
                "file": summary_file.name,
                "columns": list(df.columns),
                "rows": len(df),
                "required_columns_present": len(missing) == 0,
                "river_miles": df['River_Mile'].tolist(),
                "missing_values": missing_values.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error validating summary file: {str(e)}")
            return None
    
    def validate_hydro_file(self) -> Optional[Dict[str, Any]]:
        """
        Validate hydrograph data file.
        
        Returns:
            Dictionary with validation results or None if validation fails
        """
        hydro_file = self.config.hydro_file
        
        try:
            if not hydro_file.exists():
                logger.error(f"Hydrograph file not found: {hydro_file}")
                return None
                
            with pd.ExcelFile(hydro_file) as excel:
                sheets = excel.sheet_names
                rm_sheets = [s for s in sheets if s.startswith('RM_')]
                
                if not rm_sheets:
                    logger.error("No river mile sheets found in hydrograph file")
                    return None
                    
                sheet_info = []
                
                for sheet in rm_sheets:
                    df = pd.read_excel(excel, sheet_name=sheet)
                    
                    # Check required columns
                    required_cols = ['Time (Seconds)', 'Year']
                    missing = [col for col in required_cols if col not in df.columns]
                    
                    sheet_info.append({
                        "name": sheet,
                        "columns": list(df.columns),
                        "rows": len(df),
                        "required_columns_present": len(missing) == 0,
                        "years": sorted(df['Year'].unique().tolist()) if 'Year' in df.columns else None,
                        "time_range": [df['Time (Seconds)'].min(), df['Time (Seconds)'].max()] 
                            if 'Time (Seconds)' in df.columns and not df['Time (Seconds)'].empty else None
                    })
                    
                return {
                    "file": hydro_file.name,
                    "sheets": sheet_info,
                    "river_mile_sheets": rm_sheets
                }
                
        except Exception as e:
            logger.error(f"Error validating hydrograph file: {str(e)}")
            return None
    
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
        
        for file_path in rm_files:
            try:
                df = pd.read_excel(file_path)
                
                # Extract river mile
                try:
                    rm_str = file_path.stem.split('_')[1]
                    river_mile = float(rm_str)
                except (IndexError, ValueError):
                    logger.warning(f"Invalid river mile file name: {file_path.name}")
                    river_mile = None
                
                # Check required columns
                required_cols = ['Time (Seconds)', 'Year']
                missing = [col for col in required_cols if col not in df.columns]
                
                # Check for sensor columns
                sensor_cols = [col for col in df.columns if col.startswith('Sensor_')]
                
                # Check data range
                year_range = None
                time_range = None
                
                if 'Year' in df.columns and not df['Year'].empty:
                    year_range = [int(df['Year'].min()), int(df['Year'].max())]
                    
                if 'Time (Seconds)' in df.columns and not df['Time (Seconds)'].empty:
                    time_range = [float(df['Time (Seconds)'].min()), float(df['Time (Seconds)'].max())]
                
                results.append({
                    "file": file_path.name,
                    "river_mile": river_mile,
                    "columns": list(df.columns),
                    "rows": len(df),
                    "required_columns_present": len(missing) == 0,
                    "sensor_columns": sensor_cols,
                    "year_range": year_range,
                    "time_range": time_range
                })
                
            except Exception as e:
                logger.error(f"Error validating processed file {file_path.name}: {str(e)}")
                results.append({
                    "file": file_path.name,
                    "error": str(e)
                })
        
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
                r.get("river_mile") for r in processed_validation 
                if r.get("river_mile") is not None
            }
            
            # Check for consistency
            missing_rms = summary_rms - processed_rms
            extra_rms = processed_rms - summary_rms
            
            river_mile_consistency = {
                "all_summary_rms_processed": len(missing_rms) == 0,
                "missing_processed_rms": list(missing_rms),
                "extra_processed_rms": list(extra_rms)
            }
        
        return {
            "summary": summary_validation,
            "hydrograph": hydro_validation,
            "processed": processed_validation,
            "river_mile_consistency": river_mile_consistency,
            "overall_valid": (
                summary_validation is not None and
                hydro_validation is not None and
                len(processed_validation) > 0
            )
        }