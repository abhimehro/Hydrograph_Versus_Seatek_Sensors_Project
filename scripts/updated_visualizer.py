"""
Hydrograph vs. Seatek Sensors Visualization Script
Author: Abhi Mehrotra

A comprehensive script for analyzing and visualizing hydrograph and sensor data relationships.
Features:
- Multi-year and multi-sensor data processing
- Advanced data cleaning and validation
- Professional-grade visualizations
- Statistical analysis and correlation interpretation
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict , List , Tuple

import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class DataVisualizationError(Exception):
	"""Custom exception for visualization-related errors."""
	pass


def get_project_root() -> Path:
	"""
	Get the absolute path to the project root directory.
 
	Returns:
	 Path: The project root directory path
  
	Raises:
	 FileNotFoundError: If the project directory doesn't exist
	"""
	project_path = Path('/Users/abhimehrotra/DataspellProjects/Hydrograph-Versus-Seatek-Sensors-Project')
	if not project_path.exists():
		raise FileNotFoundError(f"Project directory not found at: {project_path}")
	return project_path


def validate_numeric_data(data: pd.Series) -> pd.Series:
	"""
	Validate and clean numeric data by removing invalid values.
 
	Args:
	 data (pd.Series): Numeric data series to validate
  
	Returns:
	 pd.Series: Cleaned numeric data with invalid values removed
	"""
	return data[
		(data.notna()) &           # Remove NaN values
		(data != 0) &              # Remove zeros
		(data > 0) &               # Remove negative values
		(data != float('inf')) &   # Remove infinity
		(data != float('-inf'))    # Remove negative infinity
		]


def clean_data(data: pd.DataFrame, required_columns: List[str]) -> pd.DataFrame:
	"""
	Clean and prepare data for visualization by removing invalid values.
 
	Args:
	 data (pd.DataFrame): Input DataFrame containing sensor and hydrograph data
	 required_columns (List[str]): List of columns that need to be cleaned
  
	Returns:
	 pd.DataFrame: Cleaned DataFrame with invalid values removed
  
	Raises:
	 DataVisualizationError: If required columns are missing or data is insufficient
	"""
	try:
		cleaned_data = data.copy()
		
		# Validate each required column
		for col in required_columns:
			if col not in cleaned_data.columns:
				raise DataVisualizationError(f"Required column '{col}' not found in data")
			cleaned_data[col] = validate_numeric_data(cleaned_data[col])
		
		# Remove rows with any remaining invalid values
		cleaned_data = cleaned_data.dropna(subset=required_columns)
		
		# Ensure we have enough data points
		if len(cleaned_data) < 2:
			raise DataVisualizationError("Insufficient valid data points after cleaning")
		
		return cleaned_data
	
	except Exception as e:
		raise DataVisualizationError(f"Error during data cleaning: {str(e)}")


def setup_plot_style() -> None:
	"""
	Configure the global plotting style for consistent, professional visualizations.
	Sets both Seaborn and Matplotlib parameters for optimal display.
	"""
	# Set Seaborn style
	sns.set_style("whitegrid", {
			'grid.linestyle': '--',
			'grid.alpha': 0.3,
			'axes.edgecolor': '0.2',
			'axes.linewidth': 1.2,
			'grid.color': '0.8'
			})
	
	# Set Matplotlib parameters
	plt.rcParams.update({
			'font.family': 'sans-serif',
			'font.sans-serif': ['Arial'],
			'font.size': 10,
			'axes.titleweight': 'bold',
			'axes.titlesize': 14,
			'axes.labelsize': 12,
			'figure.titlesize': 16,
			'figure.dpi': 100,
			'savefig.dpi': 300,
			'savefig.bbox': 'tight',
			'figure.figsize': (15, 8)
			})


def interpret_correlation(correlation: float) -> str:
	"""
	Provide a detailed interpretation of the correlation coefficient.
 
	Args:
	 correlation (float): The calculated Pearson correlation coefficient
  
	Returns:
	 str: A detailed description of the correlation strength and direction
	"""
	abs_corr = abs(correlation)
	direction = "positive" if correlation >= 0 else "negative"
	
	if abs_corr >= 0.9:
		strength = "Very strong"
	elif abs_corr >= 0.7:
		strength = "Strong"
	elif abs_corr >= 0.5:
		strength = "Moderate"
	elif abs_corr >= 0.3:
		strength = "Weak"
	else:
		strength = "Very weak or no"
	
	return f"{strength} {direction} relationship"


def format_sensor_name(sensor: str) -> str:
	"""
	Format sensor name for display by removing underscores and maintaining proper spacing.
 
	Args:
	 sensor (str): The original sensor name (e.g., 'Sensor_1')
  
	Returns:
	 str: Formatted sensor name (e.g., 'Sensor 1')
	"""
	return ' '.join(sensor.split('_'))


def create_visualization(
		plot_data: pd.DataFrame,
		rm: float,
		year: int,
		sensor: str,
		column_mappings: Dict[str, str]
		) -> Tuple[plt.Figure, float]:
	"""
	Create a professional visualization chart with enhanced styling and data representation.
 
	Args:
		plot_data (pd.DataFrame): DataFrame containing the filtered data
		rm (float): River mile number
		year (int): Year of the data
		sensor (str): Sensor column name
		column_mappings (Dict[str, str]): Dictionary mapping column names
  
	Returns:
		Tuple[plt.Figure, float]: (matplotlib figure object, correlation coefficient)
  
	Raises:
		DataVisualizationError: If visualization cannot be created
	"""
	try:
		# Set up the plot
		fig, ax1 = plt.subplots()
		fig.patch.set_facecolor('white')
		
		# Get time data
		time_hours = plot_data['Time_(Hours)']
		
		# Plot hydrograph data (blue dots)
		ax1.set_xlabel('Time (Hours)', fontsize=12, labelpad=10)
		ax1.set_ylabel('Hydrograph Discharge [gpm]', color='blue', fontsize=12, labelpad=10)
		hydrograph_scatter = ax1.scatter(
				time_hours,
				plot_data[column_mappings['hydrograph']],
				color='blue',
				label='Hydrograph',
				s=40,
				alpha=0.7,
				zorder=3
				)
		
		# Configure primary axis
		ax1.tick_params(axis='y', labelcolor='blue', labelsize=10)
		ax1.grid(True, linestyle='--', alpha=0.3, zorder=1)
		
		# Create secondary y-axis for sensor data
		ax2 = ax1.twinx()
		ax2.set_ylabel('Seatek Sensor Reading [mm]', color='orange', fontsize=12, labelpad=10)
		
		# Plot sensor line and points
		sensor_line = ax2.plot(
				time_hours,
				plot_data[sensor],
				color='orange',
				label=format_sensor_name(sensor),
				linewidth=1.5,
				alpha=0.7,
				zorder=2
				)[0]
		
		sensor_scatter = ax2.scatter(
				time_hours,
				plot_data[sensor],
				color='orange',
				s=25,
				alpha=0.7,
				zorder=4
				)
		
		# Configure secondary axis
		ax2.tick_params(axis='y', labelcolor='orange', labelsize=10)
		
		# Calculate statistics
		n_points = len(plot_data)
		correlation = plot_data[column_mappings['hydrograph']].corr(plot_data[sensor])
		correlation_strength = interpret_correlation(correlation)
		
		# Create comprehensive title
		title = (
				f"River Mile {rm} | {format_sensor_name(sensor)} | Year {year}\n"
				f"Correlation Coefficient: {correlation:.2f} | n={n_points} points\n"
				f"Interpretation: {correlation_strength} (n = number of paired observations)"
		)
		plt.title(title, pad=20)
		
		# Create custom legend with line and points
		legend_elements = [
				mpatches.Patch(color='blue', alpha=0.7, label='Hydrograph'),
				mlines.Line2D([0], [0], color='orange', alpha=0.7,
				              label=format_sensor_name(sensor),
				              marker='o', markersize=5, linewidth=1.5)
				]
		
		# Add enhanced legend
		legend = ax1.legend(
				handles=legend_elements,
				loc='upper right',
				bbox_to_anchor=(1.15, 1),
				fontsize=10,
				framealpha=0.9
				)
		legend.get_frame().set_linewidth(1.0)
		
		# Final adjustments
		plt.tight_layout()
		
		return fig, correlation
	
	except Exception as e:
		raise DataVisualizationError(f"Error creating visualization: {str(e)}")

def save_visualization(
		fig: plt.Figure,
		output_path: Path,
		dpi: int = 300
		) -> None:
	"""
	Save visualization with error handling.
 
	Args:
	 fig (plt.Figure): The matplotlib figure to save
	 output_path (Path): Path where the figure should be saved
	 dpi (int, optional): Resolution for the saved image.
	 Defaults to 300.
  
	Raises:
	 DataVisualizationError: If saving fails
	"""
	try:
		fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
		plt.close(fig)
	except Exception as e:
		raise DataVisualizationError(f"Error saving visualization: {str(e)}")


def process_rm_data(rm_data: pd.DataFrame, rm: float, sensor: str) -> int:
	"""
	Process and visualize data for a specific river mile and sensor.
 
	Args:
	 rm_data (pd.DataFrame): DataFrame containing the river mile data
	 rm (float): River mile number
	 sensor (str): Name of the sensor column
  
	Returns:
	 int: Number of charts generated
	"""
	try:
		# Define column mappings
		column_mappings = {
				'time': 'Time (Seconds)',
				'hydrograph': 'Hydrograph (Lagged)',
				'year': 'Year'
				}
		
		# Validate required columns
		required_columns = [
				column_mappings['time'],
				column_mappings['hydrograph'],
				column_mappings['year'],
				sensor
				]
		if not all(col in rm_data.columns for col in required_columns):
			print(f"Missing required columns for RM {rm}")
			return 0
		
		# Set up output directory
		project_root = get_project_root()
		output_dir = project_root / "output" / f"RM_{rm}"
		output_dir.mkdir(parents=True, exist_ok=True)
		
		charts_generated = 0
		
		# Process each year
		for year in sorted(rm_data[column_mappings['year']].unique()):
			try:
				# Filter and clean data for the year
				year_data = rm_data[rm_data[column_mappings['year']] == year].copy()
				year_data = clean_data(year_data, [column_mappings['hydrograph'], sensor])
				
				# Convert time to hours
				year_data['Time_(Hours)'] = year_data[column_mappings['time']] / 3600
				
				# Create and save visualization
				fig, correlation = create_visualization(
						year_data, rm, year, sensor, column_mappings
						)
				
				output_path = output_dir / f"RM_{rm}_Year_{year}_{format_sensor_name(sensor)}.png"
				save_visualization(fig, output_path)
				
				print(f"Generated chart: {output_path} (Correlation: {correlation:.2f})")
				charts_generated += 1
			
			except DataVisualizationError as e:
				print(f"Error processing Year {year}: {str(e)}")
				continue
		
		return charts_generated
	
	except Exception as e:
		print(f"Error processing RM {rm}, {sensor}: {str(e)}")
		return 0


def main() -> None:
	"""
	Main function to coordinate data loading, processing, and visualization generation.
	Handles the overall workflow and provides progress updates.
	"""
	try:
		print(f"Starting visualization process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
		
		# Set global plot style
		setup_plot_style()
		
		# Set up directories
		project_root = get_project_root()
		data_dir = project_root / "data"
		
		# Load and validate summary data
		data_summary_path = data_dir / 'Data_Summary.xlsx'
		if not data_summary_path.exists():
			raise FileNotFoundError(f"Data summary file not found: {data_summary_path}")
		
		data_summary = pd.read_excel(data_summary_path)
		total_charts = 0
		
		# Process each river mile
		for _, row in data_summary.iterrows():
			rm = row["River_Mile"]
			if pd.isna(rm):
				continue
			
			print(f"\nProcessing River Mile: {rm}")
			rm_file_path = data_dir / f'RM_{rm}.xlsx'
			
			if not rm_file_path.exists():
				print(f"File not found: {rm_file_path}")
				continue
			
			try:
				# Load and process data
				rm_data = pd.read_excel(rm_file_path)
				available_sensors = [col for col in rm_data.columns if col.startswith('Sensor_')]
				
				if not available_sensors:
					print(f"No sensor columns found in data for RM {rm}")
					continue
				
				print(f"Found sensors: {[format_sensor_name(s) for s in available_sensors]}")
				
				# Process each sensor
				for sensor in available_sensors:
					charts = process_rm_data(rm_data, rm, sensor)
					total_charts += charts
			
			except Exception as e:
				print(f"Error processing RM {rm}: {str(e)}")
				continue
		
		print(f"\nProcessing complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
		print(f"Total charts generated: {total_charts}")
	except Exception as e:
		print(f"Critical error in main function: {str(e)}")
		sys.exit(1)

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\nVisualization process interrupted by user.")
		sys.exit(1)
	except Exception as e:
		print(f"Unexpected error occurred: {str(e)}")
		print("For detailed error information, check the logs or contact support.")
		sys.exit(1)
