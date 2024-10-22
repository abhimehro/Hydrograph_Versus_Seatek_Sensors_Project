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
import seaborn as sns
import pandas as pd

# Function to process and plot data for a specific river mile (RM) and year
def process_rm_data(rm_data, rm, year, sensors):
    if rm_data.empty:
        print(f"No data for RM {rm}, Year {year - 1994}. Skipping chart generation.")
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    time_hours = rm_data["Time (Seconds)"] / 3600

    # Plot Hydrograph
    ax1.plot(time_hours, rm_data["Hydrograph (Lagged)"], label="Hydrograph (Lagged)", color="blue")
    ax1.set_ylabel("Hydrograph Flow Rate (GPM)")
    ax1.legend()

    # Plot Sensor data
    colors = sns.color_palette("husl", len(sensors))
    for i, sensor in enumerate(sensors):
        if sensor in rm_data.columns and not rm_data[sensor].isnull().all():
            ax2.plot(time_hours, rm_data[sensor], label=f"Sensor {i+1}", color=colors[i])

    ax2.set_xlabel("Time (Hours)")
    ax2.set_ylabel("Sediment Height (NAVD88)")
    ax2.legend()

    fig.suptitle(f"River Mile {rm} Seatek Vs. Hydrograph Chart - Year {year}", fontsize=16)
    plt.tight_layout()

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, f"RM_{rm}_Year_{year}.png"), dpi=300, bbox_inches="tight")
    plt.close()

# Main function to load data and generate plots
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
        start_year = int(row["Start_Year"].split()[0]) if isinstance(row["Start_Year"], str) else int(row["Start_Year"])
        end_year = int(row["End_Year"].split()[0]) if isinstance(row["End_Year"], str) else int(row["End_Year"])
        num_sensors = int(row["Num_Sensors"])

        try:
            rm_data = pd.read_csv(f"data/RM_{rm}.csv")
            sensors = [f"Sensor {i+1}" for i in range(num_sensors)]
            available_sensors = [sensor for sensor in sensors if sensor in rm_data.columns]

            if not available_sensors:
                print(f"No sensor data found for RM {rm}. Skipping.")
                continue

            for year in range(start_year, end_year + 1):
                year_data = rm_data[rm_data["Year"] == year - 1994]
                if not year_data.empty:
                    process_rm_data(year_data, rm, year, available_sensors)
                    print(f"Successfully processed RM {rm} for Year {year}")
                else:
                    print(f"No data found for RM {rm} Year {year}. Skipping.")

        except FileNotFoundError:
            print(f"File for RM {rm} not found. Skipping.")
        except Exception as e:
            print(f"Error processing RM {rm}: {str(e)}")

# Call the main() function to generate the charts
if __name__ == "__main__":
    main()

