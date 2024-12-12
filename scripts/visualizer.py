# scripts/visualizer.py
"""
This script visualizes sensor data against hydrograph data for different river miles (RM) and years.

Functions:
    process_rm_data(data, rm, year, sensors):
        Processes and plots sensor data against hydrograph data for a specific river mile (RM) and year.
        Save the plot as a PNG file in the output directory.
    Main():
        Main function that loads the summary data, iterates through each row, and generates plots for each river mile (RM) and year range specified in the summary.

Usage:
    Run the script directly to generate the charts.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.lines import Line2D


def calculate_percentage_change(data):
    return data.pct_change().abs()


def process_rm_data(rm_data, rm, year, sensor):
    # Filter data for the specific year
    year_data = rm_data[rm_data["Year"] == year].copy()

    if year_data.empty:
        print(f"No data for RM {rm}, Year {year}. Skipping chart generation.")
        return

    if not any(pd.notna(year_data["Hydrograph_(Lagged)"])) and not any(
        pd.notna(year_data[sensor])
    ):
        print(f"No valid hydrograph or sensor data for RM {rm}, Year {year}. Skipping.")
        return

    # Set style and figure size
    sns.set_theme(style="whitegrid")
    fig, ax1 = plt.subplots(figsize=(15, 8))
    fig.patch.set_facecolor("white")

    plt.subplots_adjust(right=0.85, left=0.1, bottom=0.12, top=0.9)

    time_hours = year_data["Time_(Seconds)"] / 3600

    # Plot hydrograph data (blue points)
    mask_hydro = pd.notna(year_data["Hydrograph_(Lagged)"])
    if any(mask_hydro):
        ax1.scatter(
            time_hours[mask_hydro],
            year_data["Hydrograph_(Lagged)"][mask_hydro],
            color="blue",
            label="Hydrograph (Lagged)",
            s=40,
            zorder=3,
        )

    ax1.set_xlabel("Time (in Hours)", fontsize=12, labelpad=10)
    ax1.set_ylabel("Hydrograph Discharges [gpm]", fontsize=12, labelpad=10)
    ax1.grid(True, alpha=0.2, linestyle="--")

    ax2 = ax1.twinx()

    # Plot sensor data (orange lines and points)
    mask_sensor = pd.notna(year_data[sensor])
    if any(mask_sensor):
        ax2.plot(
            time_hours[mask_sensor],
            year_data[sensor][mask_sensor],
            color="orange",
            label=sensor.replace("_", " "),
            linewidth=1.0,
            linestyle="-",
            zorder=1,
        )

        ax2.scatter(
            time_hours[mask_sensor],
            year_data[sensor][mask_sensor],
            color="orange",
            s=25,
            zorder=2,
        )

    ax2.set_ylabel("Seatek Sensor Readings [mm]", fontsize=12, labelpad=10)
    ax2.grid(False)

    valid_mask = mask_hydro & mask_sensor
    if sum(valid_mask) > 1:
        correlation = year_data["Hydrograph_(Lagged)"][valid_mask].corr(
            year_data[sensor][valid_mask]
        )
        plt.figtext(
            0.87,
            0.02,
            f"Correlation: {correlation:.2f}",
            fontsize=10,
            bbox=dict(
                facecolor="white", edgecolor="black", alpha=0.9, pad=5, boxstyle="round"
            ),
        )

    if any(mask_hydro):
        hydro_data = year_data["Hydrograph_(Lagged)"][mask_hydro]
        ax1.scatter(
            time_hours[hydro_data.idxmin()],
            hydro_data.min(),
            color="red",
            s=70,
            zorder=4,
            marker="v",
            label="Hydrograph Low",
        )
        ax1.scatter(
            time_hours[hydro_data.idxmax()],
            hydro_data.max(),
            color="green",
            s=70,
            zorder=4,
            marker="^",
            label="Hydrograph High",
        )

    if any(mask_sensor):
        sensor_data = year_data[sensor][mask_sensor]
        ax2.scatter(
            time_hours[sensor_data.idxmin()],
            sensor_data.min(),
            color="red",
            s=70,
            zorder=4,
            marker="x",
            label="Sensor Low",
        )
        ax2.scatter(
            time_hours[sensor_data.idxmax()],
            sensor_data.max(),
            color="green",
            s=70,
            zorder=4,
            marker="*",
            label="Sensor High",
        )

    plt.title(
        f"RM {rm} Seatek Vs. Hydrograph Chart\nYear {year} - {sensor.replace('_', ' ')}",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    legend_elements = [
        Line2D(
            [0],
            [0],
            color="blue",
            linestyle="None",
            marker="o",
            label="Hydrograph (Lagged)",
            markersize=6,
        ),
        Line2D(
            [0],
            [0],
            color="orange",
            linestyle="-",
            marker="o",
            label=sensor.replace("_", " "),
            markersize=6,
        ),
        Line2D(
            [0],
            [0],
            color="red",
            linestyle="None",
            marker="v",
            label="Hydrograph Low",
            markersize=7,
        ),
        Line2D(
            [0],
            [0],
            color="green",
            linestyle="None",
            marker="^",
            label="Hydrograph High",
            markersize=7,
        ),
        Line2D(
            [0],
            [0],
            color="red",
            linestyle="None",
            marker="x",
            label="Sensor Low",
            markersize=7,
        ),
        Line2D(
            [0],
            [0],
            color="green",
            linestyle="None",
            marker="*",
            label="Sensor High",
            markersize=7,
        ),
    ]

    ax1.legend(
        handles=legend_elements,
        bbox_to_anchor=(1.0, 1.0),
        loc="upper right",
        fontsize=10,
        ncol=1,
        title="Legend",
        framealpha=0.9,
    )

    if sum(valid_mask) > 1:
        correlation = year_data["Hydrograph_(Lagged)"][valid_mask].corr(
            year_data[sensor][valid_mask]
        )
        plt.figtext(
            0.98,
            0.02,
            f"Correlation: {correlation:.2f}",
            fontsize=9,
            bbox=dict(
                facecolor="white",
                edgecolor="black",
                alpha=0.9,
                pad=3,
                boxstyle="round,pad=0.3",
            ),
            horizontalalignment="right",
            verticalalignment="bottom",
        )

    plt.subplots_adjust(right=0.85, left=0.1, bottom=0.12, top=0.9)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(
        os.path.join(output_dir, f"RM_{rm}_Year_{year}_{sensor}.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def main():
    os.makedirs("output", exist_ok=True)
    data_summary_path = "data/Data_Summary.xlsx"

    if not os.path.exists(data_summary_path):
        print(f"File not found: {data_summary_path}")
        return

    data_summary = pd.read_excel(data_summary_path)

    for _, row in data_summary.iterrows():
        rm = row["River_Mile"]
        if pd.isna(rm):
            continue

        print(f"Processing River Mile: {rm}")

        start_year = int(str(row["Start_Year"]).split()[0])
        end_year = int(str(row["End_Year"]).split()[0])

        try:
            rm_file_path = f"data/RM_{rm}.xlsx"
            if not os.path.exists(rm_file_path):
                print(f"File not found: {rm_file_path}")
                continue

            rm_data = pd.read_excel(rm_file_path)
            print(f"Loaded data for RM {rm}")

            available_sensors = [
                col for col in rm_data.columns if col.startswith("Sensor_")
            ]

            if not available_sensors:
                print(f"No sensor columns found in data for RM {rm}")
                continue

            print(f"Found sensors: {available_sensors}")

            rm_data["Year"] = pd.to_numeric(rm_data["Year"], errors="coerce")

            for year in range(start_year, end_year + 1):
                year_data = rm_data[rm_data["Year"] == year]
                if not year_data.empty:
                    for sensor in available_sensors:
                        sensor_data = year_data[sensor].dropna()
                        hydro_data = year_data["Hydrograph_(Lagged)"].dropna()

                        if not sensor_data.empty or not hydro_data.empty:
                            print(f"Processing RM {rm}, Year {year}, {sensor}")
                            process_rm_data(rm_data, rm, year, sensor)
                        else:
                            print(
                                f"No valid data for {sensor} or Hydrograph in RM {rm}, Year {year}"
                            )

        except Exception as e:
            print(f"Error processing RM {rm}: {str(e)}")


if __name__ == "__main__":
    main()
