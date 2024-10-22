# scripts/main.py

import os
import pandas as pd
import sys
from pathlib import Path

# Manually set the project root
project_root = Path("/Users/abhimehrotra/Applications/DataSpell.app/Contents/plugins/python-ce/helpers/pydev")
sys.path.append(str(project_root / "scripts"))

def main():
    os.makedirs("output", exist_ok=True)
    data_summary_path = "data/Data_Summary.csv"

    if not os.path.exists(data_summary_path):
        print(f"File not found: {data_summary_path}")
        return

    data_summary = pd.read_csv(data_summary_path)

    for _, row in data_summary.iterrows():
        rm = row["River_Mile"]
        if pd.isna(rm):
            continue

        print(f"Processing River Mile: {rm}")
        num_sensors = int(row["Num_Sensors"])

        try:
            rm_file_path = f"data/RM_{rm}.csv"
            print(f"Looking for file: {rm_file_path}")
            rm_data = pd.read_csv(rm_file_path)
            sensors = [f"Sensor {i+1}" for i in range(1, num_sensors + 1)]
            available_sensors = [sensor for sensor in sensors if sensor in rm_data.columns]

            if not available_sensors:
                print(f"No sensor data found for RM {rm}. Skipping.")
                continue

            for year in range(1, 21):  # Changed loop to iterate over years 1-20
                year_data = rm_data[rm_data["Year"] == year]

        except FileNotFoundError:
            print(f"File for RM {rm} not found. Skipping.")
        except Exception as e:
            print(f"Error processing RM {rm}: {str(e)}")

if __name__ == "__main__":
    main()
