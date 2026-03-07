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
                
            # SECURITY: Limit file size to prevent memory exhaustion (DoS)
            if summary_file.stat().st_size > self.config.max_file_size_bytes:
                logger.error(f"Summary file size exceeds maximum allowed size ({self.config.max_file_size_bytes} bytes): {summary_file}")
                return None

            required_cols = ['River_Mile', 'Y_Offset', 'Num_Sensors']

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
                
            # SECURITY: Limit file size to prevent memory exhaustion (DoS)
            if hydro_file.stat().st_size > self.config.max_file_size_bytes:
                logger.error(f"Hydrograph file size exceeds maximum allowed size ({self.config.max_file_size_bytes} bytes): {hydro_file}")
                return None

            with pd.ExcelFile(hydro_file) as excel:
                sheets = excel.sheet_names
                rm_sheets = [s for s in sheets if s.startswith('RM_')]
                
                if not rm_sheets:
                    logger.error("No river mile sheets found in hydrograph file")
                    return None
                    
                sheet_info = []
                
                for sheet in rm_sheets:
                    required_cols = ['Time (Seconds)', 'Year']

                    # Optimization: load columns dynamically to check headers and load only required in single pass
                    seen_cols = []
                    def filter_cols(col):
                        seen_cols.append(col)
                        return col in required_cols

                    df = pd.read_excel(excel, sheet_name=sheet, usecols=filter_cols)
                    columns = list(seen_cols)

                    # If no required cols found but there are columns, load first column to get row count
                    if df.empty and columns:
                        df = pd.read_excel(excel, sheet_name=sheet, usecols=[0])

                    missing = [col for col in required_cols if col not in columns]
                    
                    sheet_info.append({
                        "name": sheet,
                        "columns": columns,
                        "rows": len(df),
                        "required_columns_present": len(missing) == 0,
                        "years": sorted(df['Year'].dropna().unique().astype(int).tolist()) if 'Year' in df.columns and df['Year'].notna().any() else None,
                        "time_range": [df['Time (Seconds)'].dropna().min(), df['Time (Seconds)'].dropna().max()] 
                            if 'Time (Seconds)' in df.columns and df['Time (Seconds)'].notna().any() else None
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
                # SECURITY: Limit file size to prevent memory exhaustion (DoS)
                if file_path.stat().st_size > self.config.max_file_size_bytes:
                    logger.error(f"Processed file size exceeds maximum allowed size ({self.config.max_file_size_bytes} bytes): {file_path}")
                    results.append({
                        "file": file_path.name,
                        "error": f"File size exceeds maximum allowed size ({self.config.max_file_size_bytes} bytes)"
                    })
                    continue

                # Extract river mile
                try:
                    rm_str = file_path.stem.split('_')[1]
                    river_mile = float(rm_str)
                except (IndexError, ValueError):
                    logger.warning(f"Invalid river mile file name: {file_path.name}")
                    river_mile = None
                
                required_cols = ['Time (Seconds)', 'Year']
                
                # Optimization: load columns dynamically and load in a single pass
                seen_cols = []
                def filter_cols(col):
                    seen_cols.append(col)
                    return col in required_cols or str(col).startswith('Sensor_')

                df = pd.read_excel(file_path, usecols=filter_cols)
                columns = list(seen_cols)

                # If no required or sensor cols found but there are columns, load first column to get row count
                if df.shape[1] == 0 and columns:
                    df = pd.read_excel(file_path, usecols=[0])

                missing = [col for col in required_cols if col not in columns]
                sensor_cols = [col for col in columns if str(col).startswith('Sensor_')]
                
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
                    "columns": columns,
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