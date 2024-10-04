# scripts/visualizer.py
"""
This script visualizes sensor data against hydrograph data for different river miles (RM) and years.

Functions:
    create_chart(data, rm, year):
        Creates and saves a chart comparing sensor data to hydrograph data for a specific river mile (RM) and year.
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
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def create_chart(data, rm, year):
    plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")

    plt.plot(
        data["Time (Seconds)"],
        data["Hydrograph (Lagged)"],
        "b-o",
        label="Hydrograph (Lagged)",
        markersize=2,
    )
    plt.plot(
        data["Time (Seconds)"],
        data["Sensor 1"],
        "orange",
        marker="o",
        linestyle="-",
        label="Sensor 1",
        markersize=2,
    )
    plt.plot(
        data["Time (Seconds)"], data["Sensor 2"], "g-o", label="Sensor 2", markersize=2
    )

    plt.xlabel("Time (in seconds)")
    plt.ylabel("Values")
    plt.title(f"Sensor Seatek Vs. Hydrograph - Year {year}")

    plt.xlim(0, 3500)
    plt.ylim(0, 12)

    plt.legend()
    plt.tight_layout()
    plt.savefig(f"output/charts/RM_{rm}_Year_{year}.png", dpi=300)
    plt.close()


def load_data(file_path):
    """
    Loads data from a CSV file into a pandas DataFrame.
    """
    return pd.read_csv(file_path)


def process_rm_data(data, rm, year, sensors):  # noqa: F811
    plt.figure(figsize=(12, 6))

    # Set style to match the image
    plt.style.use("seaborn-whitegrid")

    # Plot data
    plt.plot(
        data["Time (Seconds)"],
        data["Hydrograph (Lagged)"],
        "b-o",
        label="Hydrograph (Lagged)",
        markersize=4,
    )
    for sensor in sensors:
        plt.plot(
            data["Time (Seconds)"],
            data[f"Sensor {sensor}"],
            marker="o",
            linestyle="-",
            label=f"Sensor {sensor}",
            markersize=4,
        )

    # Set labels and title
    plt.xlabel("Time (in seconds)")
    plt.ylabel("Values")
    plt.title(f"Sensor Seatek Vs. Hydrograph - RM {rm} Year {year}")

    # Set axis limits
    plt.xlim(0, 3500)
    plt.ylim(0, 12)

    # Add legend
    plt.legend()

    # Save the figure
    plt.savefig(f"output/charts/RM_{rm}_Year_{year}.png", dpi=300, bbox_inches="tight")
    plt.close()


def process_rm_data(data, rm, year, sensors):  # noqa: F811
    plt.figure(figsize=(12, 6))

    # Set style to match the image
    plt.style.use("seaborn-whitegrid")

    # Plot data
    plt.plot(
        data["Time (Seconds)"],
        data["Hydrograph (Lagged)"],
        "b-o",
        label="Hydrograph (Lagged)",
        markersize=4,
    )
    for sensor in sensors:
        plt.plot(
            data["Time (Seconds)"],
            data[f"Sensor {sensor}"],
            marker="o",
            linestyle="-",
            label=f"Sensor {sensor}",
            markersize=4,
        )

    # Set labels and title
    plt.xlabel("Time (in seconds)")
    plt.ylabel("Values")
    plt.title(f"Sensor Seatek Vs. Hydrograph - RM {rm} Year {year}")

    # Set axis limits
    plt.xlim(0, 3500)
    plt.ylim(0, 12)

    # Add legend
    plt.legend()

    # Save the figure
    plt.savefig(f"output/charts/RM_{rm}_Year_{year}.png", dpi=300, bbox_inches="tight")
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
