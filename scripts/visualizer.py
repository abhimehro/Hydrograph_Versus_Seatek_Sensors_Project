# scripts/visualizer.py
"""
This script visualizes sensor data against hydrograph data for different river miles (RM) and years.

Functions:
    process_rm_data(data, rm, year, sensors):
        Processes and plots sensor data against hydrograph data for a specific river mile (RM) and year.
        Saves the plot as a PNG file in the output directory.
    main():
        Main function that loads the summary data, iterates through each row, and generates plots for each river mile (RM) and year range specified in the summary.

Usage:
    Run the script directly to generate the charts.
"""

# scripts/visualizer.py
import os

import matplotlib.pyplot as plt
import pandas as pd


def process_rm_data(rm_data, rm, year, sensors):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Filter out rows with missing data
    rm_data = rm_data.dropna(subset=["Time (Seconds)", "Hydrograph (Lagged)"] + sensors)

    # Convert time to hours for better readability
    time_hours = rm_data["Time (Seconds)"] / 3600

    # Plot Hydrograph
    ax1.plot(
        time_hours,
        rm_data["Hydrograph (Lagged)"],
        label="Hydrograph (Lagged)",
        color="blue",
    )
    ax1.set_ylabel("Hydrograph Flow Rate (GPM)")
    ax1.legend()

    # Plot Sensor data
    colors = ["orange", "green", "red", "purple"]
    for i, sensor in enumerate(sensors):
        if sensor in rm_data.columns:
            ax2.plot(
                time_hours, rm_data[sensor], label=f"Sensor {i+1}", color=colors[i]
            )

    ax2.set_xlabel("Time (Hours)")
    ax2.set_ylabel("Sediment Height (NAVD88)")
    ax2.legend()

    # Set title
    fig.suptitle(
        f"River Mile {rm} Seatek Vs. Hydrograph Chart - Year {year}", fontsize=16
    )

    # Adjust layout and save
    plt.tight_layout()
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(
        os.path.join(output_dir, f"RM_{rm}_Sensor_1_Year_{year}.jpg"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def main():
    os.makedirs("output", exist_ok=True)
    data_summary = pd.read_csv("data/Data_Summary.csv")

    for _, row in data_summary.iterrows():
        rm = row["River_Mile"]
        if pd.isna(rm):
            continue

        print(f"Processing River Mile: {rm}")

        start_year = row["Start_Year"]
        if isinstance(start_year, str):
            year = int(start_year.split()[0])
        else:
            year = int(start_year)

        num_sensors = int(row["Num_Sensors"])

        try:
            rm_data = pd.read_csv(f"data/RM_{rm}.csv")
            sensors = [f"Sensor {i+1}" for i in range(num_sensors)]
            available_sensors = [
                sensor for sensor in sensors if sensor in rm_data.columns
            ]

            if not available_sensors:
                print(f"No sensor data found for RM {rm}. Skipping.")
                continue

            process_rm_data(rm_data, rm, year, available_sensors)
            print(f"Successfully processed RM {rm}")
        except FileNotFoundError:
            print(f"File for RM {rm} not found. Skipping.")
        except Exception as e:
            print(f"Error processing RM {rm}: {str(e)}")


if __name__ == "__main__":
    main()
