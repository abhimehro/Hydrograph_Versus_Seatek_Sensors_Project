import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class DataProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.summary_data = None
        self.river_mile_data = {}

    def load_data(self) -> None:
        """Load all data from the Excel file."""
        try:
            # Read the summary sheet
            self.summary_data = pd.read_excel(self.file_path, sheet_name=0)
            logging.info(f"Loaded summary data with {len(self.summary_data)} river miles")

            # Read all sheets for river mile data
            excel_file = pd.ExcelFile(self.file_path)
            sheet_names = excel_file.sheet_names

            # Process each river mile sheet
            for sheet_name in sheet_names[1:]:  # Skip the summary sheet
                if sheet_name.startswith('RM_'):
                    rm_data = pd.read_excel(excel_file, sheet_name=sheet_name)
                    self.river_mile_data[sheet_name] = rm_data
                    logging.info(f"Loaded data for {sheet_name}")

        except Exception as e:
            logging.error(f"Error loading data: {str(e)}")
            raise


class Visualizer:
    def __init__(self):
        self.setup_plot_style()

    @staticmethod
    def setup_plot_style() -> None:
        """Set up enhanced plot styling using seaborn with professional formatting."""
        # Set up the base style
        sns.set_style("whitegrid", {
            "grid.linestyle": ":",  # Dotted grid lines
            "grid.alpha": 0.25,  # Subtle grid
            "axes.edgecolor": "#333333",  # Darker edge color
            "axes.linewidth": 1.5,  # Slightly thicker axes
            "grid.color": "#CCCCCC",  # Light grey grid
            "axes.spines.top": False,  # Remove top spine
            "axes.spines.right": False,  # Remove right spine
        })

        # Update matplotlib parameters for professional appearance
        plt.rcParams.update({
            # Font settings
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 11,

            # Title and label settings
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "axes.labelweight": "medium",
            "figure.titlesize": 16,

            # Figure settings
            "figure.dpi": 300,  # Higher DPI for clarity
            "figure.figsize": (12, 8),
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.2,

            # Legend settings
            "legend.frameon": True,
            "legend.framealpha": 0.8,
            "legend.edgecolor": "#CCCCCC",
            "legend.facecolor": "white",

            # Tick settings
            "xtick.major.size": 5,
            "ytick.major.size": 5,
            "xtick.minor.size": 3,
            "ytick.minor.size": 3,
            "xtick.major.width": 1.2,
            "ytick.major.width": 1.2,
            "xtick.direction": "out",
            "ytick.direction": "out",

            # Other aesthetic settings
            "lines.linewidth": 2,
            "scatter.marker": "o",
        })

    def create_visualization(
            self,
            data: pd.DataFrame,
            river_mile: float,
            year: int,
            sensor: str
    ) -> Tuple[Figure, Dict[str, float]]:
        """Create a visualization for sensor data with improved formatting."""
        """Create a visualization for sensor data."""
        try:
            fig, ax = plt.subplots()
            fig.patch.set_facecolor("white")

            # Convert time to hours
            time_hours = data["Time (Seconds)"] / 3600

            # Format sensor name and create figure
            sensor_name = sensor.replace('_', ' ').title()
            fig, ax = plt.subplots()
            fig.patch.set_facecolor("white")

            # Create scatter plot with enhanced styling
            scatter = ax.scatter(
                time_hours,
                data[sensor],
                c=data[sensor],
                cmap='viridis',
                alpha=0.8,
                s=60,
                edgecolor='white',
                linewidth=0.5
            )

            # Add customized colorbar
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label(f"{sensor_name} Value (cm)", fontsize=11, labelpad=10)
            cbar.ax.tick_params(labelsize=10)

            # Calculate statistics
            stats = {
                "mean": data[sensor].mean(),
                "std": data[sensor].std(),
                "min": data[sensor].min(),
                "max": data[sensor].max()
            }

            # Add enhanced trend line
            z = np.polyfit(time_hours, data[sensor], 1)
            p = np.poly1d(z)
            trend_line = ax.plot(time_hours, p(time_hours), "--",
                                 color='#FF4B4B',  # Bright red
                                 alpha=0.9,
                                 linewidth=2,
                                 label=f"Trend Line (slope: {z[0]:.2e})")

            # Customize axes
            ax.set_xlabel("Time (Hours)", fontsize=12, labelpad=10)
            ax.set_ylabel(f"{sensor_name} Reading (cm)", fontsize=12, labelpad=10)

            # Add grid with custom styling
            ax.grid(True, linestyle=':', alpha=0.3, which='both')
            ax.minorticks_on()

            # Create professional title with proper spacing
            title_lines = [
                f"River Mile {river_mile} | {sensor_name} | Year {year}",
                f"Mean: {stats['mean']:.2f} cm | Standard Deviation: {stats['std']:.2f} cm",
                f"Range: [{stats['min']:.2f}, {stats['max']:.2f}] cm"
            ]
            ax.set_title('\n'.join(title_lines), pad=20, linespacing=1.3)

            # Enhance legend
            ax.legend(loc='upper right',
                      bbox_to_anchor=(1.0, 1.0),
                      frameon=True,
                      facecolor='white',
                      edgecolor='#CCCCCC',
                      framealpha=0.9,
                      fontsize=10)

            # Add subtle background color
            ax.set_facecolor('#F8F9FA')

            # Adjust layout
            plt.tight_layout()

            ax.grid(True, linestyle="--", alpha=0.3)
            ax.legend()
            plt.tight_layout()

            return fig, stats

        except Exception as e:
            logging.error(f"Error creating visualization: {str(e)}")
            raise


class DataAnalyzer:
    def __init__(self, data_processor: DataProcessor, visualizer: Visualizer):
        self.data_processor = data_processor
        self.visualizer = visualizer
        self.output_base_dir = "output"

    def process_all_data(self) -> None:
        """Process and visualize data for all river miles."""
        try:
            for rm_sheet, rm_data in self.data_processor.river_mile_data.items():
                river_mile = float(rm_sheet.split('_')[1])
                self._process_river_mile(river_mile, rm_data)

        except Exception as e:
            logging.error(f"Error processing data: {str(e)}")
            raise

    def _process_river_mile(self, river_mile: float, data: pd.DataFrame) -> None:
        """Process data for a single river mile."""
        sensors = [col for col in data.columns if col.startswith("Sensor_")]
        years = data["Year"].unique()

        for sensor in sensors:
            for year in years:
                self._process_year_data(river_mile, data, year, sensor)

    def _process_year_data(
            self,
            river_mile: float,
            data: pd.DataFrame,
            year: int,
            sensor: str
    ) -> bool:
        """
        Process and visualize data for a specific year and sensor.
        Returns True if visualization was created successfully, False otherwise.
        """
        try:
            # Filter data for the specific year
            year_data = data[data["Year"] == year].copy()

            # Check for sufficient valid data
            valid_data = year_data[
                year_data[sensor].notna() &
                (year_data[sensor] > 0) &
                (year_data[sensor] != float("inf"))
                ]

            if len(valid_data) < 2:
                logging.warning(
                    f"Insufficient valid data for RM {river_mile}, "
                    f"Year {year}, {sensor} (found {len(valid_data)} points)"
                )
                return False

            # Check if output path already exists
            output_dir = self._create_output_dir(river_mile, sensor)
            output_path = os.path.join(
                output_dir,
                f"RM_{river_mile}_Year_{year}_{sensor}.png"
            )

            if os.path.exists(output_path):
                logging.info(
                    f"Visualization already exists for RM {river_mile}, "
                    f"Year {year}, {sensor}. Skipping."
                )
                return True

            # Create visualization
            fig, stats = self.visualizer.create_visualization(
                valid_data, river_mile, year, sensor
            )

            # Save visualization
            fig.savefig(output_path, bbox_inches="tight", dpi=300)
            plt.close(fig)

            logging.info(
                f"Generated visualization for RM {river_mile}, "
                f"Year {year}, {sensor} "
                f"(Mean: {stats['mean']:.2f}, Points: {len(valid_data)})"
            )
            return True

        except Exception as e:
            logging.error(
                f"Error processing year {year} for RM {river_mile}, "
                f"{sensor}: {str(e)}"
            )
            return False

    def _create_output_dir(self, river_mile: float, sensor: str) -> str:
        """Create output directory for sensor visualizations within existing river mile directory."""
        # Construct paths
        rm_base_dir = os.path.join(self.output_base_dir, f"RM_{river_mile}")
        sensor_dir = os.path.join(rm_base_dir, "sensor_charts", sensor)

        # Check if base river mile directory exists
        if not os.path.exists(rm_base_dir):
            logging.warning(f"Base directory for RM_{river_mile} does not exist. Creating it...")

        # Create sensor directory
        os.makedirs(sensor_dir, exist_ok=True)
        logging.info(f"Created/verified sensor directory: {sensor_dir}")

        return sensor_dir


def main():
    """Main function to run the visualization process."""
    # Get the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the default data file path
    default_data_path = os.path.join(
        script_dir,
        "..",
        "data",
        "processed",
        "Hydrograph_Seatek_Data (Series 26 - Trial Runs).xlsx"
    )

    # Use the default path or accept a command-line argument
    data_file = sys.argv[1] if len(sys.argv) > 1 else default_data_path

    try:
        # Initialize components
        processor = DataProcessor(data_file)
        processor.load_data()

        visualizer = Visualizer()
        analyzer = DataAnalyzer(processor, visualizer)

        # Process and visualize all data
        analyzer.process_all_data()

        logging.info("Data processing and visualization completed successfully!")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()