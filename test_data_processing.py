#!/usr/bin/env python3

"""
Test script for data processing components without visualization.
"""

import logging
from pathlib import Path

from src.hydrograph_seatek_analysis.core.config import Config
from src.hydrograph_seatek_analysis.core.logger import configure_root_logger
from src.hydrograph_seatek_analysis.data.data_loader import DataLoader
from src.hydrograph_seatek_analysis.data.processor import SeatekDataProcessor


def test_data_processing():
    """Test data processing functionality."""
    # Configure logging
    configure_root_logger(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Testing data processing without visualization")
    
    try:
        # Initialize components
        config = Config()
        data_loader = DataLoader(config)
        
        # Load data
        logger.info("Loading data...")
        summary_data, hydro_data = data_loader.load_all_data()
        
        # Initialize processor
        processor = SeatekDataProcessor(
            data_dir=config.processed_dir,
            summary_data=summary_data,
            config=config
        )
        
        # Load river mile data
        processor.load_data()
        logger.info(f"Loaded data for {len(processor.river_mile_data)} river miles")
        
        # Test processing one sensor
        if processor.river_mile_data:
            rm_data = next(iter(processor.river_mile_data.values()))
            if rm_data.sensors:
                sensor = rm_data.sensors[0]
                year = sorted(rm_data.data['Year'].unique())[0]
                
                logger.info(f"Processing RM {rm_data.river_mile}, Year {year}, Sensor {sensor}")
                processed_data, metrics = processor.process_data(
                    rm_data.river_mile,
                    year,
                    sensor
                )
                
                logger.info(f"Processed data shape: {processed_data.shape}")
                logger.info(f"Metrics: Valid rows: {metrics.valid_rows}")
                
                return True
        
        logger.warning("No data to process")
        return False
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_data_processing()
    exit(0 if success else 1)