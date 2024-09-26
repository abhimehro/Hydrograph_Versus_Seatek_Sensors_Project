# scripts/data_processor.py

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
            year_data["Sensor"] = sensor
            year_data = year_data.rename(
                columns={
                    f"Hydrograph (Lagged) for Y{year:02d}": "Hydrograph",
                    f"Sensor {sensor} for Y{year:02d}": "Sensor_Value",
                }
            )
            processed_data.append(year_data)
    return pd.concat(processed_data, ignore_index=True)
