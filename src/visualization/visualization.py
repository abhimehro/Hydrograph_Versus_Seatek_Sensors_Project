import logging
from pathlib import Path
from typing import List
from pandas import DataFrame, Series
from matplotlib.pyplot import rcParams
from seaborn import set_style
from src import create_visualization
from src import save_visualization

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Check if matplotlib is available to gracefully handle imports
try:
    from matplotlib.figure import Figure
    has_matplotlib = True
except ImportError:
    Figure = None
    has_matplotlib = False

# Helper: Get Project Root Directory
def get_project_root() -> Path:
    """Return the root directory of the project."""
    return Path(__file__).parent.parent

# Custom Exception for Errors in Data Visualization
class DataVisualizationError(Exception):
    """Custom exception for errors during data visualization."""
    pass

# Function: Validate Numeric Data
def validate_numeric_data(data: Series) -> Series:
    """
    Validate and clean numeric data in a pandas Series.

    Removes NaN, zero, negative, infinity, and -infinity values.
    Raises an error if no valid data exists.
    """
    initial_length = len(data)
    cleaned_data = data[
        (data.notna()) & (data > 0) & (data != float("inf")) & (data != float("-inf"))
    ]

    if cleaned_data.empty:
        logging.warning("All data points are invalid after validation.")
        raise DataVisualizationError("No valid numeric data found.")

    logging.info(
        f"Data cleaned: Removed {100 * (1 - len(cleaned_data) / initial_length):.2f}% of entries."
    )
    return cleaned_data

# Function: Clean and Validate DataFrame
def clean_data(data: DataFrame, required_columns: List[str]) -> DataFrame:
    """
    Clean and validate a DataFrame by:
    - Checking required columns exist.
    - Validating numeric data in required columns.
    - Dropping rows with invalid data.
    """
    if not all(col in data.columns for col in required_columns):
        missing_columns = [col for col in required_columns if col not in data.columns]
        raise DataVisualizationError(f"Missing required columns: {missing_columns}")

    # Clone data for processing
    cleaned_data = data.copy()

    for col in required_columns:
        cleaned_data[col] = validate_numeric_data(cleaned_data[col])

    cleaned_data = cleaned_data.dropna(subset=required_columns)

    if len(cleaned_data) < 2:
        raise DataVisualizationError("Insufficient valid data points after cleaning.")

    return cleaned_data

# Function: Set Plot Style (Seaborn + Matplotlib)
def setup_plot_style() -> None:
    """
    Set up the plot style using Seaborn and Matplotlib.
    Includes visual aesthetics for grid, lines, and font styling.
    """
    set_style(
        "whitegrid",
        {
            "grid.linestyle": "--",
            "grid.alpha": 0.3,
            "axes.edgecolor": "0.2",
            "axes.linewidth": 1.2,
            "grid.color": "0.8",
        },
    )
    rcParams.update(
        {
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
            "figure.figsize": (15, 8),
        }
    )

# Helper: Format Sensor Name
def format_sensor_name(sensor: str) -> str:
    """
    Format the sensor name for display in plots.
    Converts 'sensor_x' to 'Sensor X'.
    """
    return sensor.replace("_", " ").title()

# Function: Process River Mile Data
def process_rm_data(rm_data: DataFrame, rm: float, sensor: str) -> int:
    """
    Process river mile data and generate visualizations for a specific sensor.

    Args:
        - rm_data: DataFrame containing river data.
        - rm: River mile identifier.
        - sensor: Sensor column name.

    Returns:
        - Number of charts generated.
    """
    try:
        # Define column mappings
        COLUMN_MAPPINGS = {
            "time": "Time (Seconds)",
            "hydrograph": "Hydrograph (Lagged)",
            "year": "Year",
        }
        required_columns = [
            COLUMN_MAPPINGS["time"],
            COLUMN_MAPPINGS["hydrograph"],
            COLUMN_MAPPINGS["year"],
            sensor,
        ]

        # Validate columns in data
        if not all(col in rm_data.columns for col in required_columns):
            logging.warning(f"Missing required columns for RM {rm}: {required_columns}")
            return 0

        # Setup output directory
        output_dir = get_project_root() / "output" / f"RM_{rm}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Process data year by year
        charts_generated = 0
        for year in sorted(rm_data[COLUMN_MAPPINGS["year"]].unique()):
            try:
                # Filter and clean data for the current year
                year_data = rm_data[rm_data[COLUMN_MAPPINGS["year"]] == year].copy()
                year_data = clean_data(
                    year_data, [COLUMN_MAPPINGS["hydrograph"], sensor]
                )

                # Generate visualization
                fig, correlation = create_visualization(
                    year_data, rm, year, sensor, COLUMN_MAPPINGS
                )
                output_path = output_dir / f"RM_{rm}_Year_{year}_{format_sensor_name(sensor)}.png"

                # Save visualization
                save_visualization(fig, output_path)
                charts_generated += 1

            except DataVisualizationError as e:
                logging.error(f"DataVisualizationError for RM {rm}, year {year}: {str(e)}")
                continue

        return charts_generated

    except Exception as e:
        logging.error(f"Unexpected error processing data for RM {rm}: {str(e)}")
        return 0

# Main Script Logic
def main():
    """
    Entrypoint for the script. Processes file and generates charts.
    """
    import argparse
    from src import process_file  # Import dynamically to avoid circular imports

    # Command-line argument parser
    parser = argparse.ArgumentParser(description="Generate sensor visualizations.")
    parser.add_argument("file_path", type=str, help="Path to the input file.")
    args = parser.parse_args()

    try:
        file_path = Path(args.file_path)

        if not file_path.exists():
            logging.error(f"File not found: {file_path}")
            return

        logging.info(f"Starting processing for file: {file_path}")
        total_charts = process_file(file_path)
        logging.info(f"Processing complete. Total charts generated: {total_charts}")

    except Exception as e:
        logging.error(f"Critical error during processing: {str(e)}")

if __name__ == "__main__":
    main()
