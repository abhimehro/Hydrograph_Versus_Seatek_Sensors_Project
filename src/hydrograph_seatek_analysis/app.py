"""
Main application module for Seatek and Hydrograph data processing.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, List, Tuple, Dict

import pandas as pd

from .core.config import Config
from .core.logger import configure_root_logger
from .data.data_loader import DataLoader
from .data.processor import SeatekDataProcessor
from .visualization.chart_generator import ChartGenerator


class Application:
    """Main application class for Seatek data processing."""
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename string to prevent path traversal and other vulnerabilities.

        Args:
            filename: The untrusted filename string (e.g., from an Excel column or sheet)

        Returns:
            A sanitized string safe for use as a path component.
        """
        import re
        if not isinstance(filename, str):
            filename = str(filename)

        # Keep only alphanumeric, dash, underscore, and space
        sanitized = re.sub(r'[^\w\-\.\s]', '_', filename)
        # Prevent directory traversal dots like ..
        sanitized = re.sub(r'\.{2,}', '_', sanitized)
        # Strip leading/trailing whitespaces and dots
        return sanitized.strip('. ')

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize application with optional config.
        
        Args:
            config: Optional configuration, if not provided, default config will be created
        """
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.data_loader = DataLoader(self.config)
        self.chart_generator = ChartGenerator(self.config)
        
        # Placeholder for processor (will be initialized after data is loaded)
        self.processor: Optional[SeatekDataProcessor] = None
        
    def setup(self) -> bool:
        """
        Set up application environment.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Setting up application environment")
            
            # Verify directories exist
            required_dirs = [
                self.config.data_dir,
                self.config.raw_data_dir,
                self.config.processed_dir,
                self.config.output_dir
            ]
            
            for directory in required_dirs:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Verified directory: {directory}")
                
            # Check output directory is writable
            if not Path(self.config.output_dir).exists():
                self.logger.error(f"Output directory does not exist: {self.config.output_dir}")
                return False
                
            if not Path(self.config.output_dir).is_dir():
                self.logger.error(f"Output path is not a directory: {self.config.output_dir}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up application: {e}")
            return False
            
    def load_data(self) -> bool:
        """
        Load data from files.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Loading data")
            
            # Load summary and hydrograph data
            summary_data, hydro_data = self.data_loader.load_all_data()
            
            # Initialize processor
            self.processor = SeatekDataProcessor(
                data_dir=self.config.processed_dir,
                summary_data=summary_data,
                config=self.config
            )
            
            # Load river mile data
            self.processor.load_data()
            
            self.logger.info(f"Loaded data for {len(self.processor.river_mile_data)} river miles")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return False
            
    def process_data(self) -> bool:
        """
        Process data and generate visualizations.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.processor:
            self.logger.error("Processor not initialized. Call load_data() first.")
            return False
            
        try:
            self.logger.info("Processing data and generating visualizations")
            success_count = 0
            error_count = 0
            
            # Process each river mile, year, and sensor
            for rm_data in self.processor.river_mile_data.values():
                for sensor in rm_data.sensors:
                    for year in sorted(rm_data.data['Year'].unique()):
                        try:
                            # Process data
                            processed_data, metrics = self.processor.process_data(
                                rm_data.river_mile,
                                year,
                                sensor
                            )
                            
                            if processed_data.empty:
                                self.logger.warning(
                                    f"No data to process for RM {rm_data.river_mile}, "
                                    f"Year {year}, Sensor {sensor}"
                                )
                                continue
                                
                            # Generate chart
                            chart, chart_metrics = self.chart_generator.create_chart(
                                processed_data,
                                rm_data.river_mile,
                                year,
                                sensor
                            )
                            
                            if chart:
                                # Save chart
                                safe_year = self._sanitize_filename(str(year))
                                safe_sensor = self._sanitize_filename(str(sensor))

                                output_path = (self.config.output_dir / 
                                               f"RM_{rm_data.river_mile:.1f}" /
                                               f"Year_{safe_year}_{safe_sensor}.png")
                                
                                if self.chart_generator.save_chart(chart, output_path):
                                    success_count += 1
                                else:
                                    error_count += 1
                            else:
                                self.logger.error(
                                    f"Failed to create chart for RM {rm_data.river_mile}, "
                                    f"Year {year}, Sensor {sensor}"
                                )
                                error_count += 1
                                
                        except Exception as e:
                            self.logger.error(
                                f"Error processing RM {rm_data.river_mile}, "
                                f"Year {year}, Sensor {sensor}: {str(e)}"
                            )
                            error_count += 1
                            continue
                            
            self.logger.info(f"Processed {success_count} charts successfully, {error_count} errors")
            return error_count == 0
            
        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
            return False
            
    def run(self) -> bool:
        """
        Run the full processing pipeline.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.setup():
            self.logger.error("Failed to set up application")
            return False
            
        if not self.load_data():
            self.logger.error("Failed to load data")
            return False
            
        if not self.process_data():
            self.logger.warning("Errors occurred during data processing")
            return False
            
        self.logger.info("Processing completed successfully")
        return True


def main() -> int:
    """
    Main entry point for the application.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Configure logging
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        configure_root_logger(
            level=logging.INFO,
            log_dir=log_dir,
            log_filename="sensor_visualization.log"
        )
        
        logger = logging.getLogger(__name__)
        logger.info("Starting Seatek data processing")
        
        # Create and run application
        app = Application()
        success = app.run()
        
        if success:
            logger.info("Application completed successfully")
            return 0
        else:
            logger.error("Application completed with errors")
            return 1
            
    except Exception as e:
        logging.error(f"Fatal error in main execution: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())