# scripts/main.py
"""
Main script for the Hydrograph-Versus-Seatek-Sensors-Project.

This script performs the following tasks:
1. Defines paths for raw data, processed data, and output charts.
2. Ensures the necessary directories exist.
3. Loads raw data using the `load_data` function from `scripts.data_loader`.
4. Processes the loaded data using the `process_data` function from `scripts.data_processor`.
5. Saves the processed data to a CSV file in the processed data directory.
6. Generates charts for each unique RM (River Mile) and for each year from 1 to 20 using the `create_chart` function from `scripts.visualizer`.

Functions:
    main(): The main function that orchestrates the data loading, processing, saving, and chart generation.

Execution:
    This script is intended to be executed as a standalone program.
    If executed directly, it will call the `main` function.
"""

import sys
from pathlib import Path

from scripts.data_loader import load_data
from scripts.data_processor import process_data
from scripts.visualizer import create_chart

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def main():
    # Define paths
    data_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"
    output_dir = project_root / "output" / "charts"

    # Ensure directories exist
    processed_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load and process data
    raw_data = load_data(data_dir)
    processed_data = process_data(raw_data)

    # Save processed data
    processed_data.to_csv(processed_dir / "all_rm_data.csv", index=False)

    # Generate charts
    for rm in processed_data["RM"].unique():
        rm_data = processed_data[processed_data["RM"] == rm]
        for year in range(1, 21):
            create_chart(rm_data, rm, year, output_dir)


if __name__ == "__main__":
    main()
