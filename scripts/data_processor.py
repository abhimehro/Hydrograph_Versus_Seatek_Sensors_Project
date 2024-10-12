# scripts/data_processor.py
"""
Processes the input DataFrame by extracting and transforming data for each year and sensor.

The function iterates over a range of years (1 to 20) and extracts relevant columns for each sensor.
It then renames the columns to a standardized format and appends the processed data to a list.
Finally, it concatenates all the processed data into a single DataFrame.

Args:
    df (pd.DataFrame): The input DataFrame containing the raw data with columns in the format
                       "Time (Seconds)", "Hydrograph (Lagged) for YXX", "Sensor XX for YXX", and "RM".

Returns:
    pd.DataFrame: A concatenated DataFrame containing the processed data with columns "Time (Seconds)",
                  "Hydrograph", "Sensor_Value", "RM", "Year", and "Sensor".
"""

import pandas as pd


def process_data(df):
    processed_data = []
    for year in range(1, 21):
        for sensor in [
            col.split()[1] for col in df.columns if col.startswith("Sensor")
        ]:
            year_data = df[
                [
                    "Time (Seconds)",
                    f"Hydrograph (Lagged) for Y{year:02d}",
                    f"Sensor {sensor} for Y{year:02d}",
                    "RM",
                ]
            ]
            year_data["Year"] = year
            year_data["Sensor"] = f"Sensor {sensor}"
            year_data = year_data.rename(
                columns={
                    f"Hydrograph (Lagged) for Y{year:02d}": "Hydrograph",
                    f"Sensor {sensor} for Y{year:02d}": "Sensor_Value",
                }
            )
            processed_data.append(year_data)
    return pd.concat(process_data, ignore_index=True)
