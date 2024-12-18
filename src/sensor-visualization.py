import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

def get_project_root() -> Path:
    """Return the root directory of the project."""
    return Path(__file__).parent.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class DataVisualizationError(Exception):
    """Custom exception for errors during data visualization."""
    pass

def validate_numeric_data(data: pd.Series) -> pd.Series:
    """Validate and clean numeric data in a pandas Series."""
    return data[
        (data.notna())
        & (data != 0)
        & (data > 0)
        & (data != float("inf"))
        & (data != float("-inf"))
    ]

def clean_data(data: pd.DataFrame, sensor_column: str) -> pd.DataFrame:
    """Clean the data by validating and removing invalid entries."""
    try:
        cleaned_data = data.copy()
        if sensor_column not in cleaned_data.columns:
            raise DataVisualizationError(f"Required column '{sensor_column}' not found in data")
        
        cleaned_data[sensor_column] = validate_numeric_data(cleaned_data[sensor_column])
        cleaned_data = cleaned_data.dropna(subset=[sensor_column])
        
        if len(cleaned_data) < 2:
            raise DataVisualizationError("Insufficient valid data points after cleaning")
        
        return cleaned_data
    except Exception as e:
        raise DataVisualizationError(f"Error during data cleaning: {str(e)}")

def setup_plot_style() -> None:
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

def format_sensor_name(sensor: str) -> str:
    """Format the sensor name for display in the plot."""
    return sensor.replace("_", " ").title()

def create_sensor_visualization(
    plot_data: pd.DataFrame,
    rm: float,
    year: int,
    sensor: str,
) -> Tuple[Figure, Dict[str, float]]:
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
        plt.colorbar(scatter, ax=ax, label=f"{format_sensor_name(sensor)} Value [mm]")
        
        # Calculate statistics
        stats = {
            "mean": plot_data[sensor].mean(),
            "std": plot_data[sensor].std(),
            "min": plot_data[sensor].min(),
            "max": plot_data[sensor].max(),
        }
        
        # Set labels and title
        ax.set_xlabel("Time (Hours)", fontsize=12, labelpad=10)
        ax.set_ylabel("Sensor Reading [mm]", fontsize=12, labelpad=10)
        
        title = (
            f"River Mile {rm} | {format_sensor_name(sensor)} | Year {year}\n"
            f"Mean: {stats['mean']:.2f} mm | Std: {stats['std']:.2f} mm\n"
            f"Range: [{stats['min']:.2f}, {stats['max']:.2f}] mm"
        )
        ax.set_title(title, pad=20)
        
        # Customize grid
        ax.grid(True, linestyle="--", alpha=0.3, zorder=1)
        
        # Add trend line
        z = np.polyfit(time_hours, plot_data[sensor], 1)
        p = np.poly1d(z)
        ax.plot(time_hours, p(time_hours), "r--", alpha=0.8, label=f"Trend Line (slope: {z[0]:.2e})")
        
        ax.legend()
        plt.tight_layout()
        
        return fig, stats
    except Exception as e:
        raise DataVisualizationError(f"Error creating visualization: {str(e)}")

def save_visualization(fig: Figure, output_path: Path, dpi: int = 300) -> None:
    """Save the visualization to a file."""
    try:
        fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
    except Exception as e:
        raise DataVisualizationError(f"Error saving visualization: {str(e)}")

def process_rm_data(rm_data: pd.DataFrame, rm: float, sensor: str) -> int:
    """Process data for a specific river mile and sensor, generating visualizations."""
    try:
        required_columns = ["Time (Seconds)", "Year", sensor]
        
        if not all(col in rm_data.columns for col in required_columns):
            logging.warning(f"Missing required columns for RM {rm}")
            return 0
            
        output_dir = create_output_dir(rm)
        charts_generated = 0
        
        for year in range(1, 21):  # Generate plots for years 1-20
            try:
                year_data = rm_data[rm_data["Year"] == year].copy()
                year_data = clean_data(year_data, sensor)
                
                if len(year_data) < 2:
                    logging.warning(f"Insufficient data for RM {rm}, Year {year}, {sensor}")
                    continue
                
                fig, stats = create_sensor_visualization(year_data, rm, year, sensor)
                output_path = output_dir / f"RM_{rm}_Year_{year}_{format_sensor_name(sensor)}.png"
                save_visualization(fig, output_path)
                
                logging.info(
                    f"Generated chart: {output_path} "
                    f"(Mean: {stats['mean']:.2f}, Std: {stats['std']:.2f})"
                )
                charts_generated += 1
                
            except DataVisualizationError as e:
                logging.error(f"Error processing Year {year}: {str(e)}")
                continue
                
        return charts_generated
        
    except Exception as e:
        logging.error(f"Error processing RM {rm}, {sensor}: {str(e)}")
        return 0

def create_output_dir(rm: float) -> Path:
    """Create the output directory for a specific river mile."""
    output_dir = get_project_root() / "output" / f"RM_{rm}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def main() -> None:
    """Main function to orchestrate the visualization process."""
    try:
        logging.info(f"Starting visualization process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        setup_plot_style()
        project_root = get_project_root()
        data_dir = project_root / "data"
        
        # Process each river mile data file
        total_charts = 0
        for data_file in data_dir.glob("RM_*.xlsx"):
            try:
                rm = float(data_file.stem.split("_")[1])
                logging.info(f"Processing River Mile: {rm}")
                
                rm_data = pd.read_excel(data_file)
                sensors = ["Sensor_1", "Sensor_2"]
                
                for sensor in sensors:
                    if sensor in rm_data.columns:
                        charts = process_rm_data(rm_data, rm, sensor)
                        total_charts += charts
                    else:
                        logging.warning(f"Sensor {sensor} not found in data for RM {rm}")
                        
            except Exception as e:
                logging.error(f"Error processing {data_file}: {str(e)}")
                continue
                
        logging.info(f"Processing complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Total charts generated: {total_charts}")
        
    except Exception as e:
        logging.critical(f"Critical error in main function: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Visualization process interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        logging.error("For detailed error information, check the logs or contact support.")
        sys.exit(1)
