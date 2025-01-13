import glob
import logging.config
import os
from concurrent.futures import ProcessPoolExecutor

import yaml

# Load YAML content
yaml_content = """
version: 1
disable_existing_loggers: False
formatters:
  simple:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: simple
    level: DEBUG
root:
  level: DEBUG
  handlers: [console]
"""

logging_config = yaml.safe_load ( yaml_content )
logging.config.dictConfig ( logging_config )
logger = logging.getLogger ( __name__ )


def load_config ( config_file = "config.yaml" ) :
	try :
		with open ( config_file , "r" ) as file :
			return yaml.safe_load ( file )
	except FileNotFoundError :
		logger.error ( f"Configuration file {config_file} not found." )
		return { }
	except yaml.YAMLError as e :
		logger.error ( f"Error parsing configuration file: {str ( e )}" )
		return { }


def process_rm_file ( file_path ) :
	try :
		# Your processing code here
		logger.info ( f"Processing file: {file_path}" )
		# Example processing logic
	except Exception as e :
		logger.error ( f"Error processing file {file_path}: {str ( e )}" )


def process_all_files ( configuration ) :
	data_dir = configuration.get ( "data_dir" )
	if not data_dir :
		logger.error ( "Data directory not specified in the configuration." )
		return
	
	with ProcessPoolExecutor ( ) as executor :
		futures = [
				executor.submit ( process_rm_file , file )
				for file in glob.glob ( os.path.join ( data_dir , "raw" , "RM-*.xlsx" ) )
				]
		for future in futures :
			future.result ( )


if __name__ == "__main__" :
	config = load_config ( )
	process_all_files ( config )