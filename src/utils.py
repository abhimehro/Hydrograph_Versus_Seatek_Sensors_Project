import logging
from datetime import datetime
from pathlib import Path
from typing import List

from pandas import DataFrame , ExcelFile , read_excel , Series


class DataVisualizationError ( Exception ) :
	"""Custom exception for errors during data visualization."""
	pass


def get_project_root ( ) -> Path :
	"""Return the root directory of the project."""
	return Path ( __file__ ).parent.parent


def validate_numeric_data ( data: Series ) -> Series :
	"""Validate and clean numeric data in a pandas Series."""
	return data [
		(data.notna ( ))
		& (data != 0)
		& (data > 0)
		& (data != float ( "inf" ))
		& (data != float ( "-inf" ))
		]


def clean_data ( data: DataFrame , required_columns: List [ str ] ) -> DataFrame :
	"""Clean the data by validating and removing invalid entries."""
	try :
		cleaned_data = data.copy ( )
		for col in required_columns :
			if col not in cleaned_data.columns :
				raise DataVisualizationError ( f"Required column '{col}' not found in data" )
			cleaned_data [ col ] = validate_numeric_data ( cleaned_data [ col ] )
		cleaned_data = cleaned_data.dropna ( subset = required_columns )
		if len ( cleaned_data ) < 2 :
			raise DataVisualizationError ( "Insufficient valid data points after cleaning" )
		return cleaned_data
	except KeyError as e :
		raise DataVisualizationError ( f"Column not found: {str ( e )}" )
	except Exception as e :
		raise DataVisualizationError ( f"Error during data cleaning: {str ( e )}" )


def format_sensor_name ( sensor: str ) -> str :
	"""Format the sensor name for display in the plot."""
	return sensor.replace ( "_" , " " ).title ( )


def load_excel_file ( file_path: Path ) -> DataFrame :
	"""Load an Excel file into a DataFrame."""
	try :
		with ExcelFile ( file_path ) as xls :
			return read_excel ( xls )
	except Exception as e :
		logging.error ( f"Error reading file {file_path}: {str ( e )}" )
		raise


def create_output_dir ( rm: float ) -> Path :
	"""Create the output directory for a specific river mile."""
	project_root = get_project_root ( )
	output_dir = project_root / "output" / f"RM_{rm}"
	output_dir.mkdir ( parents = True , exist_ok = True )
	return output_dir


def log_start_of_process ( ) -> None :
	"""Log the start of the visualization process."""
	logging.info ( f"Starting visualization process at {datetime.now ( ).strftime ( '%Y-%m-%d %H:%M:%S' )}" )


def log_end_of_process ( total_charts: int ) -> None :
	"""Log the end of the visualization process."""
	logging.info ( f"Processing complete at {datetime.now ( ).strftime ( '%Y-%m-%d %H:%M:%S' )}" )
	logging.info ( f"Total charts generated: {total_charts}" )
