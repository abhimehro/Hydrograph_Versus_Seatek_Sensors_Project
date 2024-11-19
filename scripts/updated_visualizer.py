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
    Run the script directly to generate the chart
    
    # Import necessary libraries
import os
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.lines import Line2Ds.
"""


import os
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.lines import Line2D

def process_rm_data(rm_data, rm, year, sensor):
    year_data = filter_year_data(rm_data, year)
    if year_data.empty or not has_valid_data(year_data, sensor):
        return
    
    fig, ax1 = setup_plot()
    time_hours = year_data["Time_(Seconds)"] / 3600
    
    plot_hydrograph(ax1, year_data, time_hours)
    ax2 = plot_sensor_data(ax1, year_data, time_hours, sensor)
    
    finalize_plot(ax1, ax2, rm, year, sensor)
    save_plot(rm, year, sensor)

def filter_year_data(rm_data, year):
    return rm_data[rm_data["Year"] == year].copy()

def has_valid_data(year_data, sensor):
    if not any(pd.notna(year_data["Hydrograph_(Lagged)"])) and not any(pd.notna(year_data[sensor])):
        logging.info(f"No valid hydrograph or sensor data. Skipping.")
        return False
    return True

def setup_plot():
    sns.set_theme(style="whitegrid")
    fig, ax1 = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('white')
    plt.subplots_adjust(left=0.1, right=0.85, top=0.9, bottom=0.1)
    return fig, ax1

def plot_hydrograph(ax1, year_data, time_hours):
    mask_hydro = pd.notna(year_data["Hydrograph_(Lagged)"])
    if any(mask_hydro):
        ax1.scatter(time_hours[mask_hydro],
                    year_data["Hydrograph_(Lagged)"][mask_hydro],
                    color='blue', label='Hydrograph (Lagged)', s=40, zorder=3)
    ax1.set(xlabel='Time (in Hours)', ylabel='Hydrograph Discharges [gpm]')
    ax1.grid(True, alpha=0.2, linestyle='--')

def plot_sensor_data(ax1, year_data, time_hours, sensor):
    ax2 = ax1.twinx()
    mask_sensor = pd.notna(year_data[sensor])
    if any(mask_sensor):
        ax2.plot(time_hours[mask_sensor],
                 year_data[sensor][mask_sensor],
                 color='orange', label=sensor.replace('_', ' '), linewidth=1.0, linestyle='-', zorder=1)
        ax2.scatter(time_hours[mask_sensor],
                    year_data[sensor][mask_sensor],
                    color='orange', s=25, zorder=2)
        ax2.set_ylabel('Seatek Sensor Readings [mm]')
        ax2.grid(False)
    return ax2

def finalize_plot(ax1, ax2, rm, year, sensor):
    plt.title(f"RM {rm} Seatek Vs. Hydrograph Chart\nYear {year} - {sensor.replace('_', ' ')}",
              fontsize=16, fontweight='bold', pad=20)
    legend_elements = [
        Line2D([0], [0], color='blue', linestyle='None', marker='o', label='Hydrograph (Lagged)', markersize=6),
        Line2D([0], [0], color='orange', linestyle='-', marker='o', label=sensor.replace('_', ' '), markersize=6)
    ]
    ax1.legend(handles=legend_elements, loc="upper left", fontsize=10, ncol=1, framealpha=0.9)

def save_plot(rm, year, sensor):
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    with plt.savefig(output_dir / f"RM_{rm}_Year_{year}_{sensor}.png", dpi=300, bbox_inches="tight"):
        pass

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
		
		# Handle different year formats
		start_year = int(str(row["Start_Year"]).split()[0])
		end_year = int(str(row["End_Year"]).split()[0])
		
		try:
			rm_file_path = f'data/RM_{rm}.xlsx'
			if not os.path.exists(rm_file_path):
				print(f"File not found: {rm_file_path}")
				continue
			
			rm_data = pd.read_excel(rm_file_path)
			print(f"Loaded data for RM {rm}")
			
			# Find all sensor columns in the data
			available_sensors = [col for col in rm_data.columns if col.startswith('Sensor_')]
			
			if not available_sensors:
				print(f"No sensor columns found in data for RM {rm}")
				continue
			
			print(f"Found sensors: {available_sensors}")
			
			# Convert Year column to numeric, handling any string values
			rm_data["Year"] = pd.to_numeric(rm_data["Year"], errors='coerce')
			
			for year in range(start_year, end_year + 1):
				year_data = rm_data[rm_data["Year"] == year]
				if not year_data.empty:
					for sensor in available_sensors:
						# Check if we have any valid data for this sensor or hydrograph
						sensor_data = year_data[sensor].dropna()
						hydro_data = year_data["Hydrograph_(Lagged)"].dropna()
						
						if not sensor_data.empty or not hydro_data.empty:
							print(f"Processing RM {rm}, Year {year}, {sensor}")
							process_rm_data(rm_data, rm, year, sensor)
						else:
							print(f"No valid data for {sensor} or Hydrograph in RM {rm}, Year {year}")
		
		except Exception as e:
			print(f"Error processing RM {rm}: {str(e)}")

if __name__ == "__main__":
	main()

