# scripts/visualizer.py
"""
This script visualizes sensor data against hydrograph data for different river miles (RM) and years.

Functions:
    load_data(file_path):
        Loads data from a CSV file into a pandas DataFrame.

    process_rm_data(data, rm, year, sensors):
        Processes and plots sensor data against hydrograph data for a specific river mile (RM) and year.
        Saves the plot as a PNG file in the output directory.

    main():
        Main function that loads the summary data, iterates through each row, and generates plots for each river mile (RM) and year range specified in the summary.

Usage:
    Run the script directly to generate the charts.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd


def load_data(file_path):
    return pd.read_csv(file_path)


def process_rm_data(data, rm, year, sensors):
    year_data = data[data["Year"] == year]

    plt.figure(figsize=(12, 6))
    plt.plot(
        year_data["Time (Seconds)"],
        year_data["Hydrograph (Lagged)"],
        label="Hydrograph (Lagged)",
    )

    for sensor in sensors:
        plt.plot(
            year_data["Time (Seconds)"],
            year_data[f"Sensor_{sensor}"],
            label=f"Sensor {sensor}",
        )
    plt.title(f"Sensor Seatek Vs. Hydrograph - RM {rm} Year {year}")
    plt.xlabel("Time (in seconds)")
    plt.ylabel("Values")
    plt.legend()
    plt.grid(True)

    output_dir = f"output/charts/RM_{rm}"
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(f"{output_dir}/RM_{rm}_Year_{year}.png")
    plt.close()


def main():
    summary = load_data("data/Data_Summary.csv")

    for _, row in summary.iterrows():
        rm = row["River_Mile"]
        sensors = [int(s) for s in row["Notes"].split(",")]
        start_year = int(row["Start_Year"].split()[0])
        end_year = int(row["End_Year"].split()[0])

        rm_data = load_data(f"data/RM_{rm}.csv")

        for year in range(start_year, end_year + 1):
            process_rm_data(rm_data, rm, year, sensors)

    print("All charts have been generated.")


if __name__ == "__main__":
    main()
