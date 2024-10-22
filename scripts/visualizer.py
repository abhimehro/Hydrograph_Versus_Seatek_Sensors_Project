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
from matplotlib.lines import Line2D

def calculate_percentage_change(data):
    return data.pct_change().abs()

def process_rm_data(rm_data, rm, year, sensor):
    if rm_data.empty:
        print(f"No data for RM {rm}, Year {year}. Skipping chart generation.")
        return

    # Set seaborn theme for better aesthetics
    sns.set_theme(style="whitegrid", palette="Set2")

    fig, ax1 = plt.subplots(figsize=(12, 10))
    fig.patch.set_facecolor('lightgray')
    time_hours = rm_data["Time_(Seconds)"] / 3600

    # Plot Hydrograph (Lagged) as scatter points
    hydrograph_data = rm_data["Hydrograph_(Lagged)"]
    ax1.scatter(time_hours, hydrograph_data, color='blue', label='Hydrograph (Lagged)', s=50)
    ax1.set_xlabel('Time (Hours)', fontsize=14)
    ax1.set_ylabel('Hydrograph Flow Rate (in GPM)', fontsize=14)
    ax1.grid(True)

    # Create a second axis for the sensor data
    ax2 = ax1.twinx()

    # Plot Sensor data
    sensor_data = rm_data[sensor]
    sensor_title = sensor.replace('_', ' ')  # Replace underscores with spaces
    ax2.plot(time_hours, sensor_data, color='orange', label=sensor_title, linewidth=2, linestyle='--')
    ax2.set_ylabel('Sediment Bed Levels (in NAVD88)', fontsize=14)
    ax2.grid(False)

    # Calculate significant changes using percentage change
    hydrograph_pct_change = calculate_percentage_change(hydrograph_data)
    sensor_pct_change = calculate_percentage_change(sensor_data)
    threshold = 0.05  # Define a threshold for significant change (5%)

    significant_changes = (hydrograph_pct_change > threshold) & (sensor_pct_change > threshold)
    for idx in significant_changes[significant_changes].index:
        ax1.axvline(x=time_hours[idx], color='purple', linestyle='--', linewidth=1)
        ax2.axvline(x=time_hours[idx], color='purple', linestyle='--', linewidth=1)

    # Calculate and display correlation coefficient
    correlation = hydrograph_data.corr(sensor_data)
    plt.figtext(0.85, 0.02, f'Correlation: {correlation:.2f}', fontsize=12, color='black', bbox=dict(facecolor='white', edgecolor='black'))

    # Plot high and low points for Hydrograph
    hydrograph_low = hydrograph_data.min()
    hydrograph_high = hydrograph_data.max()
    ax1.scatter(time_hours[hydrograph_data.idxmin()], hydrograph_low, color='red', s=70, zorder=5, marker='v', label='Hydrograph Low')
    ax1.scatter(time_hours[hydrograph_data.idxmax()], hydrograph_high, color='green', s=70, zorder=5, marker='^', label='Hydrograph High')

    # Plot high and low points for Sensor data
    sensor_low = sensor_data.min()
    sensor_high = sensor_data.max()
    ax2.scatter(time_hours[sensor_data.idxmin()], sensor_low, color='red', s=70, zorder=5, marker='x', label='Sensor Low')
    ax2.scatter(time_hours[sensor_data.idxmax()], sensor_high, color='green', s=70, zorder=5, marker='*', label='Sensor High')

    # Set title and legend
    actual_year = year  # Use the actual year directly
    plt.title(f"RM {rm} Seatek Vs. Hydrograph Chart - Year {actual_year} - {sensor_title}", fontsize=20, fontweight='bold')

    # Custom legend with title and colors
    legend_elements = [
        Line2D([0], [0], color='blue', linestyle='None', marker='o', label='Hydrograph (Lagged)', markersize=6),
        Line2D([0], [0], color='orange', linestyle='--', label=sensor_title, linewidth=2),
        Line2D([0], [0], color='purple', linestyle='--', label='Significant Change', linewidth=1),
        Line2D([0], [0], color='red', linestyle='None', marker='v', label='Hydrograph Low', markersize=7),
        Line2D([0], [0], color='green', linestyle='None', marker='^', label='Hydrograph High', markersize=7),
        Line2D([0], [0], color='red', linestyle='None', marker='x', label='Sensor Low', markersize=7),
        Line2D([0], [0], color='green', linestyle='None', marker='*', label='Sensor High', markersize=7)
    ]
    ax1.legend(handles=legend_elements, loc="upper left", fontsize=12, ncol=1, title="Legend")

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, f"RM_{rm}_Year_{actual_year}_{sensor}.png"), dpi=300, bbox_inches="tight")
    plt.close()

def main():
    os.makedirs("output", exist_ok=True)
    data_summary_path = 'data/Data_Summary.xlsx'

    if not os.path.exists(data_summary_path):
        print(f"File not found: {data_summary_path}")
        return

    data_summary = pd.read_excel(data_summary_path)

    for _, row in data_summary.iterrows():
        rm = row["River_Mile"]
        if pd.isna(rm):
            continue

        print(f"Processing River Mile: {rm}")
        start_year = int(row["Start_Year"].split()[0]) if isinstance(row["Start_Year"], str) else int(row["Start_Year"])
        end_year = int(row["End_Year"].split()[0]) if isinstance(row["End_Year"], str) else int(row["End_Year"])
        num_sensors = int(row["Num_Sensors"])

        try:
            rm_file_path = f'data/RM_{rm}.xlsx'
            print(f"Looking for file: {rm_file_path}")
            if not os.path.exists(rm_file_path):
                print(f"File not found: {rm_file_path}")
                continue

            rm_data = pd.read_excel(rm_file_path)
            print(f"Loaded data for RM {rm}:")
            print(rm_data.head())  # Print the first few rows of the data to verify its contents

            sensors = [f"Sensor_{i}" for i in range(1, num_sensors + 1)]
            available_sensors = [sensor for sensor in sensors if sensor in rm_data.columns]

            if not available_sensors:
                print(f"No sensor data found for RM {rm}. Skipping.")
                continue

            for year in range(start_year, end_year + 1):
                for sensor in available_sensors:
                    year_data = rm_data[rm_data["Year"] == year]  # Directly compare with the actual year
                    if not year_data.empty:
                        process_rm_data(year_data, rm, year, sensor)
                    else:
                        print(f"No data for RM {rm}, Year {year}. Skipping.")

        except FileNotFoundError:
            print(f"File for RM {rm} not found. Skipping.")
        except Exception as e:
            print(f"Error processing RM {rm}: {str(e)}")

if __name__ == "__main__":
    main()



