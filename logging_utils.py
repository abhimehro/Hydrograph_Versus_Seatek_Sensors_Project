import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_project_root():
    # Use the current working directory if __file__ is not defined
    try:
        root_dir = os.path.dirname(os.path.abspath(__file__))
        logging.debug(f"Using script directory as the project root: {root_dir}")
    except NameError:
        root_dir = os.getcwd()
        logging.warning("'__file__' is not defined. Falling back to current working directory as the project root.")
    return root_dir

def check_and_create_directory(path):
    if not os.path.exists(path):
        logging.info(f"Directory '{path}' does not exist. Creating it.")
        try:
            os.makedirs(path)
        except Exception as e:
            logging.error(f"Failed to create directory '{path}': {e}")
            raise
    else:
        logging.info(f"Directory '{path}' already exists.")

def main():
    # Determine the project root safely
    project_root = get_project_root()

    # Define the target directory
    data_directory = os.path.join(project_root, "data")

    # Ensure the data directory exists
    try:
        check_and_create_directory(data_directory)
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        return

    # Continue with further processing
    logging.info(f"Data directory is ready: {data_directory}")

if __name__ == "__main__":
    main()