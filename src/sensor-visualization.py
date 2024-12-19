import logging
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict

SENSORS = [ "Sensor_1" , "Sensor_2" ]  # List of sensors

logging.basicConfig (
        level = logging.WARNING ,
        format = "%(asctime)s - %(levelname)s - %(message)s"
        )


def filter_numeric_data ( series: pd.Series ) -> pd.Series :
    """Filter numeric data, ensuring values are positive and finite."""
    return series [ (series.notna ( )) & (series > 0) & (series != float ( "inf" )) & (series != float ( "-inf" )) ]


def clean_data ( data: pd.DataFrame , sensor: str ) -> pd.DataFrame :
    """Clean the data by validating and removing invalid sensor entries."""
    if sensor not in data.columns :
        raise ValueError ( f"Sensor column '{sensor}' not found in data" )
    data = data.copy ( )
    data [ sensor ] = filter_numeric_data ( data [ sensor ] )
    cleaned = data.dropna ( subset = [ sensor ] )
    if len ( cleaned ) < 2 :
        raise ValueError ( "Insufficient valid data points after cleaning" )
    return cleaned


def setup_output_dir_for_sensor ( rm: int ) -> str :
    """Set up the output directory for a given river mile."""
    output_path = os.path.join ( "output" , f"RM_{int ( rm )}" )
    os.makedirs ( output_path , exist_ok = True )
    return output_path


def _process_year_data ( data: pd.DataFrame , year: int , rm: int , sensor: str , output_dir: str ) -> int :
    """Process data for a specific year, including visualization and saving charts."""
    year_data = data [ data [ "Year" ] == year ]
    if year_data.empty :
        logging.warning ( f"No data for year {year}, sensor '{sensor}'" )
        return 0
    
    try :
        cleaned_year_data = clean_data ( year_data , sensor )
        fig , stats = create_sensor_visualization ( cleaned_year_data , rm , year , sensor )
        output_file = os.path.join ( output_dir , f"RM_{rm}_Year_{year}_{sensor}.png" )
        save_visualization ( fig , output_file )
        logging.info ( f"Generated chart for RM {rm}, Year {year}, Sensor {sensor}: {stats}" )
        return 1
    except ValueError as error :
        logging.warning ( f"Year {year} processing failed for RM {rm} | {sensor}: {error}" )
        return 0


def process_rm_data ( data: pd.DataFrame , rm: int , sensor: str ) -> int :
    """Process all available data for a given river mile (RM) and sensor."""
    if not all ( column in data.columns for column in [ "Time (Seconds)" , "Year" , sensor ] ) :
        logging.error ( f"Required columns missing for RM {rm} (Sensor: {sensor})" )
        return 0
    
    output_dir = setup_output_dir_for_sensor ( rm )
    total_charts = sum ( _process_year_data ( data , year , rm , sensor , output_dir ) for year in range ( 1 , 21 ) )
    return total_charts


def process_file ( file_path: str ) -> int :
    """Process a single data file and generate visualizations for each sensor."""
    try :
        rm = int ( float ( file_path.split ( "_" ) [ 1 ] ) )  # Extract RM from file name
        logging.info ( f"Processing River Mile: {rm}" )
        data = pd.read_excel ( file_path , engine = 'openpyxl' , na_values = [ '' ] )
        charts_generated = sum (
                process_rm_data ( data , rm , sensor ) for sensor in SENSORS if sensor in data.columns
                )
        return charts_generated
    except Exception as e :
        logging.error ( f"Failed to process file {file_path}: {e}" )
        return 0
