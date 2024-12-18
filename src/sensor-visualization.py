import logging
import sys
from datetime import datetime
from typing import Dict, Tuple
import os
from concurrent.futures import ProcessPoolExecutor  # Use concurrent.futures for Python 3.x or install futures for 2.x

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure


def get_project_root():
    """Return the root directory of the project."""
    try:
        # If __file__ exists, use it to identify the project root
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        # Fallback: If __file__ is not defined, use the current working directory
        logging.warning("'__file__' is not defined. Falling back to current working directory as the project root.")
        return os.getcwd()


logging.basicConfig(
        level=logging.WARNING,  # Set to WARNING to reduce logging overhead
        format="%(asctime)s - %(levelname)s - %(message)s"
        )

class DataVisualizationError(Exception):
    """Custom exception for errors during data visualization."""
    pass


def validate_numeric_data(data):
    """Validate and clean numeric data in a pandas Series."""
    return data[
        (data.notna())
        & (data != 0)
        & (data > 0)
        & (data != float("inf"))
        & (data != float("-inf"))
        ]


def clean_data(data, sensor_column):
    """Clean the data by validating and removing invalid entries."""
    try:
        cleaned_data = data.copy()
        if sensor_column not in cleaned_data.columns:
            raise DataVisualizationError("Required column '{}' not found in data".format(sensor_column))
        
        cleaned_data[sensor_column] = validate_numeric_data(cleaned_data[sensor_column])
        cleaned_data = cleaned_data.dropna(subset=[sensor_column])
        
        if len(cleaned_data) < 2:
            raise DataVisualizationError("Insufficient valid data points after cleaning")
        
        return cleaned_data
    except Exception as e1:
        raise DataVisualizationError("Error during data cleaning: {}".format(str(e1)))


def setup_plot_style():
    """Set up the plot style using seaborn."""
    sns.set_style("whitegrid", {
            "grid.linestyle": "--",
            "grid.alpha": 0.3,
            "axes.edgecolor": "0.2",
            "axes.linewidth": 1.2,
            "grid.color": "0.8",
            })
    plt.rcParams.update({
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial"],
            "font.size": 10,
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "figure.titlesize": 16,
            "figure.dpi": 100,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "figure.figsize": (12, 8),
            })


def format_sensor_name(sensor):
    """Format the sensor name for display in the plot."""
    return sensor.replace("_", " ").title()


def create_sensor_visualization(plot_data, rm, year, sensor):
    """Create a scatter plot visualization of sensor data over time."""
    try:
        fig, ax = plt.subplots()
        fig.patch.set_facecolor("white")
        
        # Convert time to hours
        time_hours = plot_data["Time (Seconds)"] / 3600
        
        # Create scatter plot
        scatter = ax.scatter(
                time_hours,
                plot_data[sensor],
                c=plot_data[sensor],  # Color points by sensor value
                cmap='viridis',
                alpha=0.7,
                s=50
                )
        
        # Add colorbar
        plt.colorbar(scatter, ax=ax, label="{} Value [mm]".format(format_sensor_name(sensor)))
        
        # Calculate statistics
        stats = plot_data[sensor].agg(['mean', 'std', 'min', 'max']).to_dict()
        
        # Set labels and title
        ax.set_xlabel("Time (Hours)", fontsize=12, labelpad=10)
        ax.set_ylabel("Sensor Reading [mm]", fontsize=12, labelpad=10)
        
        title = (
                "River Mile {} | {} | Year {}\n"
                "Mean: {:.2f} mm | Std: {:.2f} mm\n"
                "Range: [{:.2f}, {:.2f}] mm"
        ).format(rm, format_sensor_name(sensor), year, stats['mean'], stats['std'], stats['min'], stats['max'])
        ax.set_title(title, pad=20)
        
        # Customize grid
        ax.grid(True, linestyle="--", alpha=0.3, zorder=1)
        
        # Add trend line
        z = np.polyfit(time_hours, plot_data[sensor].dropna(), 1)
        p = np.poly1d(z)
        ax.plot(time_hours, p(time_hours), "r--", alpha=0.8, label="Trend Line (slope: {:.2e})".format(z[0]))
        
        ax.legend()
        plt.tight_layout()
        
        return fig, stats
    except Exception as e2:
        raise DataVisualizationError("Error creating visualization: {}".format(str(e2)))


def save_visualization(fig, output_path, dpi=300):
    """Save the visualization to a file."""
    try:
        fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
    except Exception as e3:
        raise DataVisualizationError("Error saving visualization: {}".format(str(e3)))


def process_rm_data(rm_data, rm, sensor):
    """Process data for a specific river mile and sensor, generating visualizations."""
    try:
        required_columns = ["Time (Seconds)", "Year", sensor]
        
        if not all(col in rm_data.columns for col in required_columns):
            logging.warning("Missing required columns for RM {}".format(rm))
            return 0
        
        output_dir = create_output_dir(rm)
        charts_generated = 0
        
        for year in range(1, 21):  # Generate plots for years 1-20
            try:
                year_data = rm_data[rm_data["Year"] == year].copy()
                year_data = clean_data(year_data, sensor)
                
                if len(year_data) < 2:
                    logging.warning("Insufficient data for RM {}, Year {}, {}".format(rm, year, sensor))
                    continue
                
                fig, stats = create_sensor_visualization(year_data, rm, year, sensor)
                output_path = os.path.join(output_dir, "RM_{}_Year_{}_{}.png".format(rm, year, format_sensor_name(sensor)))
                save_visualization(fig, output_path)
                
                logging.info(
                        "Generated chart: {} (Mean: {:.2f}, Std: {:.2f})".format(output_path, stats['mean'], stats['std'])
                        )
                charts_generated += 1
            
            except DataVisualizationError as e4:
                logging.error("Error processing Year {}: {}".format(year, str(e4)))
                continue
        
        return charts_generated
    
    except Exception as e4:
        logging.error("Error processing RM {}, {}: {}".format(rm, sensor, str(e4)))
        return 0


def create_output_dir(rm):
    """Create the output directory for a specific river mile."""
    output_dir = os.path.join(os.getcwd(), "output", "RM_{}".format(rm))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


def process_file(data_file):
    """Process a single data file."""
    try:
        rm = float(data_file.split("_")[1])
        logging.info("Processing River Mile: {}".format(rm))
        
        rm_data = pd.read_excel(data_file, engine='openpyxl', na_values=[''])
        sensors = ["Sensor_1", "Sensor_2"]
        
        total_charts = 0
        for sensor in sensors:
            if sensor in rm_data.columns:
                charts = process_rm_data(rm_data, rm, sensor)
                total_charts += charts
            else:
                logging.warning("Sensor {} not found in data for RM {}".format(sensor, rm))
        
        return total_charts
    except Exception as e4:
        logging.error("Error processing {}: {}".format(data_file, str(e4)))
        return 0


def main():
    """Main function to orchestrate the visualization process."""
    try:
        logging.info("Starting visualization process at {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        setup_plot_style()
        project_root = get_project_root()
        data_dir = os.path.join(project_root, "data")
        
        # Process each river mile data file in parallel
        with ProcessPoolExecutor() as executor:
            data_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.startswith("RM_") and f.endswith(".xlsx")]
            results = executor.map(process_file, data_files)
            total_charts = sum(results)
        
        logging.info("Processing complete at {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        logging.info("Total charts generated: {}".format(total_charts))
    
    except Exception as ex:
        logging.error("Unexpected error occurred: {}".format(str(ex)))
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Visualization process interrupted by user.")
        sys.exit(1)
    except Exception as e5:
        logging.error("Unexpected error occurred: {}".format(str(e5)))
        logging.error("For detailed error information, check the logs or contact support.")
        sys.exit(1)
