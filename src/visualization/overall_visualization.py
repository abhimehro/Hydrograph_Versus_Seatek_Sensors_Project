# overall_visualization.py

"""
Overall Visualization Script
---------------------------
Description: Process and visualize combined Seatek and hydrograph data.
Purpose: Process and visualize combined Seatek and hydrograph data.

Author: Abhi Mehrotra
Date: January 2025
---------------------------
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.axes import Axes


def configure_logging() -> None:
    """Configure logging settings."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('combined_visualization.log', mode='a')
        ]
    )


class CombinedDataProcessor:
    """Handles combined Seatek and hydrograph data processing."""

    def __init__(self, file_path: str):
        """
        Initialize the data processor.

        Args:
            file_path: Path to the Excel data file
        """
        self.file_path = file_path
        self.summary_data = None
        self.river_mile_data = {}
        self.hydrograph_column = None


    def load_data(self) -> None:
        """Load and validate all data from the Excel file."""
        try:
            with pd.ExcelFile(self.file_path) as excel_file:
                # Load summary sheet
                self.summary_data = pd.read_excel(excel_file, sheet_name=0)
                logging.info(f"Loaded summary data with {len(self.summary_data)} river miles")

                # Load river mile sheets
                valid_sheets = 0
                for sheet_name in excel_file.sheet_names[1:]:
                    if sheet_name.startswith('RM_'):
                        data = pd.read_excel(excel_file, sheet_name=sheet_name)
                        logging.info(f"\nProcessing sheet: {sheet_name}")
                        logging.info(f"Columns found: {list(data.columns)}")

                        # Only add sheets that have sensor data
                        if 'Sensor_1' in data.columns or 'Sensor_2' in data.columns:
                            self.river_mile_data[sheet_name] = data
                            self._validate_sheet_data(sheet_name, data)
                            valid_sheets += 1
                            logging.info(f"Added {sheet_name} to processing list - contains sensor data")
                        else:
                            logging.warning(f"Skipping {sheet_name} - no sensor data found")

                logging.info(f"\nSummary:")
                logging.info(f"Total sheets processed: {len(excel_file.sheet_names[1:])}")
                logging.info(f"Sheets with valid sensor data: {valid_sheets}")

                if valid_sheets == 0:
                    raise ValueError("No sheets with valid sensor data found")

        except Exception as e:
            logging.error(f"Error loading data: {str(e)}")
            raise


    def _validate_sheet_data(self, sheet_name: str, data: pd.DataFrame) -> None:
        """
        Validate data structure and content.

        Args:
            sheet_name: Name of the sheet being validated
            data: DataFrame to validate

        Raises:
            ValueError: If required columns are missing
        """
        # Debug logging for exact column names
        logging.info(f"Sheet: {sheet_name}")
        logging.info(f"Available columns: {list(data.columns)}")
        logging.info(f"Data types:\n{data.dtypes}")
        logging.info(f"First few rows:\n{data.head()}")

        # Correct column names as they appear in the Excel file
        required_columns = {'Time (Seconds)', 'Year'}
        hydrograph_column = 'Hydrograph (Lagged)'
        sensor_columns = ['Sensor_1', 'Sensor_2']

        # Check for required columns
        missing_columns = required_columns - set(data.columns)
        if missing_columns:
            logging.error(f"Missing required columns in {sheet_name}: {missing_columns}")
            logging.error(f"Available columns: {list(data.columns)}")
            raise ValueError(f"Invalid data structure in {sheet_name}")

        # Check for sensor columns
        found_sensors = [col for col in sensor_columns if col in data.columns]
        if not found_sensors:
            logging.warning(f"No sensor columns found in {sheet_name}")
        else:
            logging.info(f"Found sensor columns: {found_sensors}")
            # Check data in sensor columns
            for sensor in found_sensors:
                unique_values = data[sensor].unique()
                logging.info(f"Unique values in {sensor}: {unique_values}")

        # Check for hydrograph column
        if hydrograph_column in data.columns:
            self.hydrograph_column = hydrograph_column
            logging.info(f"Found hydrograph column in {sheet_name}: {self.hydrograph_column}")
        else:
            self.hydrograph_column = None
            logging.warning(f"No hydrograph column found in {sheet_name}")

    def process_combined_data(
            self,
            data: pd.DataFrame,
            sensor: str,
            hydrograph_col: str = None
    ) -> Tuple[pd.DataFrame, Dict[str, int]]:
        logging.info(f"\nProcessing data for {sensor}")
        logging.info(f"Input data shape: {data.shape}")
        logging.info(f"Column names: {data.columns.tolist()}")
        logging.info(f"First few rows of {sensor} data:\n{data[sensor].head(10)}")

        metrics = {
            'original_rows': len(data),
            'invalid_sensor_rows': 0,
            'invalid_hydro_rows': 0,
            'zero_values': 0,
            'null_values': 0
        }

        processed = data.copy()

        try:
            # Convert sensor data directly to numeric, as they are already numbers
            processed[sensor] = pd.to_numeric(processed[sensor], errors='coerce')

            # Log the unique values to see what we're working with
            logging.info(f"Unique values in {sensor}: {processed[sensor].unique()}")

            # Keep all rows where sensor data is a valid number
            valid_mask = processed[sensor].notna()
            processed = processed[valid_mask].copy()

            if not processed.empty:
                # Sort by time
                processed.sort_values('Time (Seconds)', inplace=True)
                logging.info(f"Processed {len(processed)} rows of valid data")
                logging.info(f"Sample of processed data:\n{processed[[sensor, 'Time (Seconds)']].head()}")
                return processed, metrics
            else:
                logging.warning(f"No valid data after processing for {sensor}")
                return pd.DataFrame(), metrics

        except Exception as e:
            logging.error(f"Error processing data: {str(e)}")
            logging.error("Exception details:", exc_info=True)
            return pd.DataFrame(), metrics


    def _log_processing_metrics(self, metrics: Dict[str, int]) -> None:
        """
        Log data processing metrics.

        Args:
            metrics: Dictionary containing processing metrics
        """
        logging.info(
            f"Data processing metrics:\n"
            f"  Original rows: {metrics['original_rows']}\n"
            f"  Invalid sensor rows: {metrics['invalid_sensor_rows']}\n"
            f"  Invalid hydrograph rows: {metrics['invalid_hydro_rows']}\n"
            f"  Zero values found: {metrics['zero_values']}\n"
            f"  Null values found: {metrics['null_values']}"
        )


class CombinedVisualizer:
    """Manages combined data visualization."""

    def __init__(self):
        self._setup_style()

    def _setup_style(self) -> None:
        """Configure plot styling."""
        sns.set_style("whitegrid", {
            "grid.linestyle": ":",
            "grid.alpha": 0.2,
            "axes.edgecolor": "#333333",
            "axes.linewidth": 1.2,
            "grid.color": "#CCCCCC",
        })

        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial"],
            "font.size": 11,
            "figure.figsize": (12, 8),
            "figure.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.2
        })


    def create_visualization(
            self,
            data: pd.DataFrame,
            river_mile: float,
            year: int,
            sensor: str,
            hydrograph_col: str = None
    ) -> Optional[Figure]:
        try:
            logging.info(f"\nCreating visualization for {sensor}")
            logging.info(f"Data shape: {data.shape}")
            logging.info(f"Sample data to plot:\n{data[[sensor, 'Time (Seconds)']].head()}")

            # Create figure and axes
            fig, ax1 = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor("white")

            # Convert time to hours
            time_hours = data['Time (Seconds)'] / 3600

            # Plot sensor data
            ax1.scatter(time_hours,
                        data[sensor],
                        color='#FF7F0E',  # Orange for Seatek
                        alpha=0.7,
                        s=45,
                        label='Seatek Sensor Data')

            logging.info(f"Plotted {len(data)} points")

            # Customize axes
            ax1.set_xlabel('Time (Hours)', fontsize=12, labelpad=10)
            ax1.set_ylabel('Depth (cm)', color='#FF7F0E', fontsize=12, labelpad=10)

            # Format sensor name for title
            sensor_name = sensor.replace('Sensor_', 'Sensor ')
            title = f'River Mile {river_mile:.1f}\n{sensor_name} Data'
            plt.title(title, pad=20, fontsize=14)

            # Enhance styling
            ax1.tick_params(axis='y', labelcolor='#FF7F0E', labelsize=11)
            ax1.tick_params(axis='x', labelsize=11)

            # Add grid and enhance spines
            ax1.grid(True, alpha=0.2, linestyle=':')
            for spine in ax1.spines.values():
                spine.set_linewidth(1.2)

            # Enhanced legend
            ax1.legend(
                loc='upper right',
                framealpha=0.9,
                fontsize=11,
                edgecolor='#CCCCCC'
            )

            plt.tight_layout()
            logging.info("Successfully created visualization")
            return fig

        except Exception as e:
            logging.error(f"Visualization error: {str(e)}")
            logging.error("Exception details:", exc_info=True)
            return None



def verify_files_exist() -> bool:
    """Verify that all required files exist in the data directory."""
    project_root = Path("/Users/abhimehrotra/PycharmProjects/Hydrograph_Versus_Seatek_Sensors_Project")
    raw_dir = project_root / "data/raw"

    required_files = [
        raw_dir / "Data_Summary.xlsx",
        raw_dir / "Hydrograph_Seatek_Data.xlsx"
    ]

    logging.info(f"Current working directory: {Path.cwd()}")
    logging.info(f"Checking required files in directory: {raw_dir}")

    for file in required_files:
        logging.info(f"Checking file: {file} (absolute path: {file.resolve()})")

    missing_files = [str(file) for file in required_files if not file.exists()]

    if missing_files:
        logging.error(f"Missing required files:\n- " + "\n- ".join(missing_files))
        return False

    logging.info("All required files are present.")
    return True


def get_data_paths() -> Optional[Tuple[Path, Path, Path]]:
    """Get paths to required data files."""
    try:
        project_root = Path("/Users/abhimehrotra/PycharmProjects/Hydrograph_Versus_Seatek_Sensors_Project")
        rm_path = project_root / "data/processed"
        summary_path = project_root / "data/raw/Data_Summary.xlsx"
        hydro_path = project_root / "data/raw/Hydrograph_Seatek_Data.xlsx"

        paths = (rm_path, summary_path, hydro_path)

        if all(p.exists() for p in paths):
            return paths
        return None

    except Exception as e:
        logging.error(f"Error getting data paths: {str(e)}")
        return None


def check_file_accessibility(file_path: Path) -> bool:
    """Check if the file is accessible and can be read."""
    try:
        pd.read_excel(file_path)
        logging.info(f"File {file_path} is accessible and readable.")
        return True
    except Exception as e:
        logging.error(f"Error accessing file {file_path}: {str(e)}")
        return False


def main() -> None:
    """Main function to process and visualize combined data."""
    try:
        # First verify all files exist
        if not verify_files_exist():
            logging.error("Required files are missing. Please check file locations.")
            sys.exit(1)

        # Get verified paths
        paths = get_data_paths()
        if not paths:
            logging.error("Could not get valid paths to required files.")
            sys.exit(1)

        rm_path, summary_path, hydro_path = paths

        # Check file accessibility
        required_files = [summary_path, hydro_path]
        for file in required_files:
            if not check_file_accessibility(file):
                logging.error(f"File {file} is not accessible. Please check file permissions and integrity.")
                sys.exit(1)

        # Set up output directory structure
        output_dir = Path("output/combined")
        output_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created output directory: {output_dir.absolute()}")

        # Initialize processor with verified processed directory
        logging.info("Initializing data processor...")
        processor = CombinedDataProcessor(str(hydro_path))

        # Load and validate data
        logging.info("Loading and validating data...")
        processor.load_data()

        # Initialize visualizer
        logging.info("Initializing visualizer...")
        visualizer = CombinedVisualizer()

        # Process data and create visualizations
        logging.info("\nStarting data processing and visualization...")
        if not processor.river_mile_data:
            logging.warning("No valid river mile data to process")
        else:
            logging.info(f"Processing {len(processor.river_mile_data)} river mile sheets")

            # In the main processing loop:
            for sheet_name, data in processor.river_mile_data.items():
                try:
                    river_mile = float(sheet_name.split('_')[1])
                    sensors = [col for col in data.columns if col.startswith('Sensor_')]

                    logging.info(f"\nProcessing {sheet_name}")
                    logging.info(f"Found sensors: {sensors}")
                    logging.info(f"Data shape: {data.shape}")
                    for sensor in sensors:
                        logging.info(f"\nData for {sensor}:")
                        logging.info(f"Sample data:\n{data[[sensor, 'Time (Seconds)', 'Year']].head(10)}")
                        logging.info(f"Data types:\n{data[sensor].dtype}")
                        logging.info(f"Unique values:\n{data[sensor].unique()}")

                        # Process all data for this sensor at once
                        try:
                            # Process data
                            processed_data, metrics = processor.process_combined_data(
                                data,
                                sensor,
                                processor.hydrograph_column
                            )

                            if not processed_data.empty:
                                # Create visualization
                                fig = visualizer.create_visualization(
                                    processed_data,
                                    river_mile,
                                    1,  # Year is always 1 in your data
                                    sensor,
                                    processor.hydrograph_column
                                )

                                if fig:
                                    # Create output directory
                                    rm_output_dir = output_dir / f"RM_{river_mile:.1f}"
                                    rm_output_dir.mkdir(parents=True, exist_ok=True)

                                    # Save visualization
                                    output_path = rm_output_dir / f"RM_{river_mile:.1f}_{sensor}.png"
                                    fig.savefig(output_path, dpi=300, bbox_inches='tight')
                                    plt.close(fig)

                                    logging.info(f"Generated visualization: {output_path}")
                                else:
                                    logging.error("Failed to create visualization")
                            else:
                                logging.warning(f"No valid data to visualize for {sensor}")

                        except Exception as e:
                            logging.error(f"Error processing {sensor} at RM {river_mile}: {str(e)}")
                            logging.error("Exception details:", exc_info=True)
                            continue

                except Exception as e:
                    logging.error(f"Error processing sheet {sheet_name}: {str(e)}")
                    logging.error("Exception details:", exc_info=True)
                    continue

            logging.info("Combined visualization completed successfully")
            logging.info(f"Output files can be found in: {output_dir.absolute()}")

    except KeyboardInterrupt:
        logging.info("Process interrupted by user")
        sys.exit(0)

    except Exception as e:
        logging.error(f"Critical error: {str(e)}")
        logging.error("Exception details:", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()