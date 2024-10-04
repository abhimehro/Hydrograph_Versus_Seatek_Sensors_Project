import glob
import os

import pandas as pd

"""
This script processes Excel files containing hydrograph and sensor data, extracts relevant information,
and combines the processed data into a single CSV file.

Functions:
    process_rm_file(file_path: str) -> pd.DataFrame:
        Processes a single Excel file, extracts RM from the filename, reads the data, and processes it
        for each year and sensor. Returns a DataFrame with the processed data.

Script Execution:
    - Checks if the data directory exists.
    - Processes all Excel files in the data directory matching the pattern "RM-*.xlsx".
    - Combines all processed data into a single DataFrame.
    - Saves the combined data to a CSV file named "all_rm_data.csv".

Parameters:
    file_path (str): The path to the Excel file to be processed.

Returns:
    pd.DataFrame: A DataFrame containing the processed data for each year and sensor, or an empty DataFrame
    if an error occurs during processing.
"""


def process_rm_file(file_path):
    # Extract RM from filename
    try:
        rm = float(file_path.split("-")[1])
    except (IndexError, ValueError) as e:
        print(f"Error extracting RM from filename {file_path}: {e}")
        return pd.DataFrame()

    # Read the Excel file
    try:
        df = pd.read_excel(file_path, header=1)
    except Exception as e:
        print(f"Error reading Excel file {file_path}: {e}")
        return pd.DataFrame()

    # Get list of sensors
    sensors = [col.split()[1] for col in df.columns if col.startswith("Sensor")]

    # Process data for each year and sensor
    processed_data = []
    for year in range(1, 21):
        for sensor in sensors:
            try:
                year_data = df[
                    [
                        "Time (Seconds)",
                        f"Hydrograph (Lagged) for Y{year:02d}",
                        f"Sensor {sensor} for Y{year:02d}",
                    ]
                ]
                year_data["Year"] = year
                year_data["Sensor"] = sensor
                year_data["RM"] = rm
                year_data = year_data.rename(
                    columns={
                        f"Hydrograph (Lagged) for Y{year:02d}": "Hydrograph",
                        f"Sensor {sensor} for Y{year:02d}": "Sensor_Value",
                    }
                )
                processed_data.append(year_data)
            except KeyError as e:
                print(f"Missing column in file {file_path}: {e}")
                continue

    return (
        pd.concat(processed_data, ignore_index=True)
        if processed_data
        else pd.DataFrame()
    )


# Process all Excel files in the data directory
data_dir = "/Users/abhimehrotra/Hydrograph-Versus-Seatek-Sensors-Project/data"
if not os.path.isdir(data_dir):
    print(f"Data directory {data_dir} does not exist.")
    exit(1)

all_data = []

for file in glob.glob(os.path.join(data_dir, "RM-*.xlsx")):
    all_data.append(process_rm_file(file))

# Combine all processed data
if all_data:
    combined_data = pd.concat(all_data, ignore_index=True)
    # Save the combined data
    combined_data.to_csv("all_rm_data.csv", index=False)
else:
    print("No data processed.")
