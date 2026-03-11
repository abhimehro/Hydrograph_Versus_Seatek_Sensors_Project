#!/usr/bin/env python3

"""
Seatek Sensor and Hydrograph Data Visualization
---------------------------------------------
Description: Processes and visualizes Seatek sensor data with hydrograph measurements.
Converts Seatek readings to NAVD88 elevations and creates professional visualizations.

Key Features:
- NAVD88 conversion with river mile-specific offsets
- Proper time axis in minutes
- Dual-axis visualization for Seatek and Hydrograph data
- Professional styling and formatting
- Comprehensive error handling and logging

Author: Abhi Mehrotra
Date: January 2025
Version: 2.0.0
"""

import logging.handlers
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt

from utils.chart_generator import ChartGenerator
from utils.config import Config
from utils.data_loader import DataLoader
from utils.processor import SeatekDataProcessor
from utils.security import sanitize_filename


def setup_logging() -> None:
    """Configure logging settings."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.handlers.RotatingFileHandler(
                log_dir / 'sensor_visualization.log',
                maxBytes=10_000_000,  # 10MB
                backupCount=5
            )
        ]
    )


def verify_environment() -> bool:
    """Verify all required components are in place."""
    try:
        config = Config()
        required_dirs = [
            config.data_dir / 'raw',
            config.data_dir / 'processed',
            config.output_dir
        ]

        for directory in required_dirs:
            directory.mkdir(parents=True, exist_ok=True)

        return True
    except Exception as e:
        logging.error(f"Environment verification failed: {str(e)}")
        return False


def main() -> None:
    """Main execution function."""
    logger = logging.getLogger(__name__)
    try:
        # Setup
        setup_logging()
        logger.info("Starting Seatek data processing")

        if not verify_environment():
            logger.error("Environment verification failed. Exiting.")
            sys.exit(1)

        # Initialize components
        config = Config()
        data_loader = DataLoader(config)
        chart_generator = ChartGenerator()

        # Verify output directory
        output_dir = config.output_dir
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
        logger.info(f"Output directory: {output_dir}")

        if not os.access(output_dir, os.W_OK):
            logger.error(f"Output directory is not writable: {output_dir}")
            sys.exit(1)

        # Load data
        logger.info("Loading data...")
        summary_data, hydro_data = data_loader.load_all_data()

        # Initialize processor and visualizer
        processor = SeatekDataProcessor(config.processed_dir, summary_data)

        # Process data
        logger.info("Processing data...")
        processor.load_data()

        # Generate visualizations
        logger.info("Generating visualizations...")
        for rm_data in processor.river_mile_data.values():
            for sensor in rm_data.sensors:
                # Optimization: Extract unique years from the pre-grouped dictionary cache
                # keys rather than repeatedly calling .unique() on the entire DataFrame.
                for year in sorted(rm_data.year_data_cache.keys()):
                    try:
                        processed_data, metrics = processor.process_data(
                            rm_data.river_mile,
                            year,
                            sensor
                        )

                        if not processed_data.empty:
                            chart = chart_generator.create_chart(
                                processed_data,
                                rm_data.river_mile,
                                year,
                                sensor
                            )

                            if chart:
                                safe_year = sanitize_filename(str(year))
                                safe_sensor = sanitize_filename(str(sensor))
                                output_path = (config.output_dir /
                                               f"RM_{rm_data.river_mile:.1f}" /
                                               f"Year_{safe_year}_{safe_sensor}.png")
                                output_path.parent.mkdir(parents=True, exist_ok=True)

                                # Construct metadata for a11y
                                sensor_num = sensor.split("_")[1] if "_" in sensor else sensor
                                metadata = {
                                    "Title": (
                                        f"River Mile {rm_data.river_mile:.1f} - Year {year} "
                                        f"Sensor {sensor_num}"
                                    ),
                                    "Description": (
                                        "Chart showing Seatek "
                                        f"Sensor {sensor_num} data (NAVD88) and "
                                        "Hydrograph flow (GPM) over time for "
                                        f"River Mile {rm_data.river_mile:.1f} in Year {year}."
                                    ),
                                    "Author": "Hydrograph vs Seatek Sensors Analysis Project",
                                }

                                chart.savefig(output_path, dpi=300, bbox_inches='tight', metadata=metadata)
                                plt.close(chart)  # Free memory
                                logger.info(f"Generated: {output_path}")
                            else:
                                logger.error(f"Failed to create chart for RM {rm_data.river_mile}, Year {year}, Sensor {sensor}")

                    except Exception as e:
                        logger.error(f"Error processing RM {rm_data.river_mile} "
                                     f"Year {year} Sensor {sensor}: {str(e)}")
                        continue

        logger.info("Processing completed successfully")

    except Exception as e:
        logger.error(f"Fatal error in main execution: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
