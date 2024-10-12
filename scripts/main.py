# scripts/main.py

import sys
from pathlib import Path

from scripts.data_loader import load_data
from scripts.data_processor import (
    process_rm_data,  # Add this line to import process_rm_data
)

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

        sensors = ["sensor1", "sensor2", "sensor3"]  # Define the sensors list
        for year in range(1, 21):
            year_data = rm_data[rm_data["Year"] == year]
            if not year_data.empty:
                process_rm_data(year_data, rm, year, sensors)
            process_rm_data(year_data, rm, year, sensors)


if __name__ == "__main__":
    main()
