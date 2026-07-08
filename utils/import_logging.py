import glob
import logging.config
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import yaml

from .security import is_safe_path

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

logging_config = yaml.safe_load(yaml_content)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


def load_config(config_file="config.yaml"):
    try:
        with open(config_file, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"Configuration file {config_file} not found.")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {str(e)}")
        return {}


def process_rm_file(file_path):
    try:
        # Your processing code here
        logger.info(f"Processing file: {file_path}")
        # Example processing logic
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")


def process_all_files(configuration):
    data_dir = configuration.get("data_dir")
    if not data_dir:
        logger.error("Data directory not specified in the configuration.")
        return

    # SECURITY: Use a trusted base directory (current working directory) rather than
    # allowing the untrusted configuration to specify its own base_dir.
    base_dir = Path.cwd()

    # Construct the target directory path safely
    target_dir = Path(data_dir) / "raw"

    # Check if the target directory is safely within the base directory
    if not is_safe_path(base_dir, target_dir):
        logger.error(
            f"SECURITY: Attempted path traversal detected. Path outside base directory: {target_dir}"
        )
        return

    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(process_rm_file, str(file))
            for file in target_dir.glob("RM-*.xlsx")
        ]
        for future in futures:
            future.result()


if __name__ == "__main__":
    config = load_config()
    process_all_files(config)
