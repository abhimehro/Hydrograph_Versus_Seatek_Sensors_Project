import glob
import logging
import os
from concurrent.futures import ProcessPoolExecutor

import yaml

# Sample YAML content
yaml_content = """
name: John Doe
age: 30
"""

# Load YAML content
data = yaml.safe_load(yaml_content)
print(data)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample YAML content
yaml_content = """
logging:
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

# Load YAML content
config = yaml.safe_load(yaml_content)

# Apply logging configuration
logging.config.dictConfig(config)

# Example log message
logger.info("Logging is configured using YAML")


# Load configuration
def load_config(config_file="config.yaml"):
    try:
        with open(config_file, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logging.error(f"Configuration file {config_file} not found.")
        return {}
    except yaml.YAMLError as e:
        logging.error(f"Error parsing configuration file: {str(e)}")
        return {}


# Main processing function with error handling
def process_rm_file(file_path):
    try:
        # Your processing code here
        data_dir = config.get("data_dir")
        if not data_dir:
            logging.error("Data directory not specified in the configuration.")
            return

        with ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(process_rm_file, file)
                for file in glob.glob(os.path.join(data_dir, "RM-*.xlsx"))
            ]
            for future in futures:
                future.result()
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {str(e)}")


# Process all files function
def process_all_files(config):
    data_dir = config.get("data_dir")
    if not data_dir:
        logging.error("Data directory not specified in the configuration.")
        return

    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(process_rm_file, file)
            for file in glob.glob(os.path.join(data_dir, "RM-*.xlsx"))
        ]
        for future in futures:
            future.result()


# Main execution
if __name__ == "__main__":
    config = load_config()
    process_all_files(config)
