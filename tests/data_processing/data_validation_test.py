"""
Test script to verify data loading and structure.
"""

import logging
from pathlib import Path

import pandas as pd


def check_excel_structure(file_path: Path) -> None:
    """
    Verify Excel file structure and content.

    Args:
        file_path: Path to Excel file
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Checking file: {file_path}")

        with pd.ExcelFile(file_path) as excel:
            # Check sheets
            sheets = excel.sheet_names
            logger.info(f"Found sheets: {sheets}")

            # Check each sheet
            for sheet in sheets:
                df = pd.read_excel(excel, sheet_name=sheet)
                logger.info(f"\nSheet: {sheet}")
                logger.info(f"Columns: {list(df.columns)}")
                logger.info(f"Data shape: {df.shape}")

                # Check for sensor columns
                sensor_cols = [col for col in df.columns if col.startswith('Sensor_')]
                if sensor_cols:
                    for col in sensor_cols:
                        non_null = df[col].notna().sum()
                        zeros = df[col].eq(0).sum()
                        logger.info(
                            f"{col}: {non_null} non-null values, "
                            f"{zeros} zero values"
                        )

                # Check time column
                if 'Time (Seconds)' in df.columns:
                    time_data = df['Time (Seconds)']
                    logger.info(
                        f"Time range: [{time_data.min()}, {time_data.max()}]"
                    )

    except Exception as e:
        logger.error(f"Error checking file: {str(e)}")


def main():
    """Run data validation checks."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Define paths
    project_root = Path(__file__).resolve().parent.parent.parent
    data_files = [
        project_root / "data/raw/Data_Summary.xlsx",
        project_root / "data/raw/Hydrograph_Seatek_Data.xlsx"
    ]

    # Check each file
    for file_path in data_files:
        check_excel_structure(file_path)


if __name__ == "__main__":
    main()