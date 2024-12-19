import os
import logging

# Constants
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOGGING_LEVEL = logging.DEBUG
DATA_DIRECTORY_NAME = "data"

# Configure logging
logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)


# Utility Functions
def get_project_root_dir():
    """Determine the project root directory safely."""
    try:
        root_dir = os.path.dirname(os.path.abspath(__file__))
        log_debug(f"Using script directory as the project root: {root_dir}")
    except NameError:
        root_dir = os.getcwd()
        log_warning("'__file__' is not defined. Falling back to current working directory as the project root.")
    return root_dir


def ensure_directory_exists(directory_path):
    """Check if a directory exists and create it if not."""
    if not os.path.exists(directory_path):
        log_info(f"Directory '{directory_path}' does not exist. Creating it.")
        try:
            os.makedirs(directory_path)
        except Exception as error:
            log_error(f"Failed to create directory '{directory_path}': {error}")
            raise
    else:
        log_info(f"Directory '{directory_path}' already exists.")


# Logging wrappers to improve readability and prevent repetition
def log_debug(message):
    logging.debug(message)


def log_warning(message):
    logging.warning(message)


def log_info(message):
    logging.info(message)


def log_error(message):
    logging.error(message)


# Main Function
def main():
    try:
        # Determine project root
        project_root = get_project_root_dir()

        # Define and ensure data directory existence
        data_directory = os.path.join(project_root, DATA_DIRECTORY_NAME)
        ensure_directory_exists(data_directory)

        # Further actions
        log_info(f"Data directory is ready: {data_directory}")
    except Exception as e:
        log_error(f"An unexpected error occurred during execution: {e}")


if __name__ == "__main__":
    main()