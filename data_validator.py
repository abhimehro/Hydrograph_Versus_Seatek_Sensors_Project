import logging
from pathlib import Path
import os
import pandas as pd


def get_project_root() -> Path:
    """Get the project root directory."""
    current_path = Path.cwd()

    # Look for project markers
    while current_path.name:
        if (current_path / '.git').exists() or \
                (current_path / 'setup.py').exists() or \
                (current_path / 'pyproject.toml').exists() or \
                current_path.name == 'Hydrograph_Versus_Seatek_Sensors_Project':
            return current_path
        parent = current_path.parent
        if parent == current_path:
            break
        current_path = parent

    raise RuntimeError("Could not find project root directory")


def validate_data_files():
    """Validate the structure and content of input data files."""

    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # Get project root using absolute path
        project_root = get_project_root()
        logging.info(f"Project root: {project_root}")

        # Construct absolute paths
        summary_path = project_root / "data/raw/Data_Summary.xlsx"
        hydro_path = project_root / "data/raw/Hydrograph_Seatek_Data.xlsx"
        rm_path = project_root / "data/processed/RM_54.0.xlsx"

        # Log directory structure
        logging.info("\nDirectory structure:")
        for root, dirs, files in os.walk(project_root):
            level = root.replace(str(project_root), '').count(os.sep)
            indent = ' ' * 4 * level
            logging.info(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                logging.info(f"{subindent}{f}")

        # Validate existence
        for path in [summary_path, hydro_path, rm_path]:
            logging.info(f"\nChecking path: {path}")
            if not path.exists():
                logging.error(f"File not found: {path}")
                continue

            # Read and validate Data_Summary
            if path == summary_path:
                df = pd.read_excel(path)
                logging.info("Data_Summary.xlsx structure:")
                logging.info(f"Columns: {df.columns.tolist()}")
                logging.info(f"Shape: {df.shape}")

            # Read and validate Hydrograph_Seatek_Data
            elif path == hydro_path:
                with pd.ExcelFile(path) as xlsx:
                    sheets = xlsx.sheet_names
                    logging.info(f"Available sheets in Hydrograph data: {sheets}")

                    for sheet in sheets:
                        df = pd.read_excel(xlsx, sheet_name=sheet)
                        logging.info(f"\nSheet: {sheet}")
                        logging.info(f"Columns: {df.columns.tolist()}")
                        logging.info(f"Shape: {df.shape}")

            # Read and validate RM_54.0
            elif path == rm_path:
                df = pd.read_excel(path)
                logging.info("\nRM_54.0.xlsx structure:")
                logging.info(f"Columns: {df.columns.tolist()}")
                logging.info(f"Shape: {df.shape}")

        logging.info("\nValidation completed")

    except Exception as e:
        logging.error(f"Validation error: {str(e)}")
        raise


if __name__ == "__main__":
    validate_data_files()