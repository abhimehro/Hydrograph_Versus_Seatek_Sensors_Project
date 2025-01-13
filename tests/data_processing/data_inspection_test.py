"""
Script to inspect Excel data structure and content.
"""

import logging
from pathlib import Path

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_inspection.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def inspect_excel_file(file_path: Path) -> None:
    """
    Inspect Excel file structure and content.

    Args:
        file_path: Path to Excel file
    """
    try:
        logger.info(f"\nInspecting file: {file_path}")

        # Load Excel file
        excel = pd.ExcelFile(str(file_path))
        logger.info(f"Found sheets: {excel.sheet_names}")

        # Inspect each sheet
        for sheet_name in excel.sheet_names:
            inspect_sheet(excel, sheet_name)

    except Exception as e:
        logger.error(f"Error inspecting file {file_path}: {str(e)}")


def inspect_sheet(excel: pd.ExcelFile, sheet_name: str) -> None:
    """
    Inspect individual Excel sheet.

    Args:
        excel: Excel file object
        sheet_name: Name of sheet to inspect
    """
    try:
        logger.info(f"\nSheet: {sheet_name}")

        # Read first few rows for column inspection
        df_head = pd.read_excel(excel, sheet_name=sheet_name, nrows=5)
        logger.info(f"Columns: {list(df_head.columns)}")

        # Read full sheet for data analysis
        df = pd.read_excel(excel, sheet_name=sheet_name)
        logger.info(f"Data shape: {df.shape}")

        # Analyze column types
        logger.info("\nColumn types:")
        for col in df.columns:
            logger.info(f"{col}: {df[col].dtype}")

        # Check for sensor columns
        sensor_cols = [col for col in df.columns if 'Sensor' in col]
        if sensor_cols:
            logger.info("\nSensor columns found:")
            for col in sensor_cols:
                non_null = df[col].notna().sum()
                unique_vals = df[col].nunique()
                logger.info(f"{col}: {non_null} non-null values, {unique_vals} unique values")

        # Check time data if present
        time_cols = [col for col in df.columns if 'Time' in col]
        if time_cols:
            logger.info("\nTime columns found:")
            for col in time_cols:
                time_range = f"[{df[col].min()}, {df[col].max()}]"
                logger.info(f"{col} range: {time_range}")

        # Sample data preview
        logger.info("\nData preview:")
        logger.info(df.head().to_string())

    except Exception as e:
        logger.error(f"Error inspecting sheet {sheet_name}: {str(e)}")


def main():
    """Main execution function."""
    try:
        # Define data files to inspect
        project_root = Path(__file__).resolve().parent.parent.parent
        data_files = [
            project_root / "data/processed/RM_54.0.xlsx",
            project_root / "data/raw/Data_Summary.xlsx",
            project_root / "data/raw/Hydrograph_Seatek_Data.xlsx"
        ]

        # Inspect each file
        for file_path in data_files:
            if file_path.exists():
                inspect_excel_file(file_path)
            else:
                logger.error(f"File not found: {file_path}")

    except Exception as e:
        logger.error(f"Error during inspection: {str(e)}")


if __name__ == "__main__":
    main()