"""
Hydrograph Versus Seatek Sensors Project
This package contains modules for processing hydrograph and sensor data,
calculating correlations, and visualizing the results.

Modules:
    - data_processor: Functions for processing input data.
    - correlation_explanation: Functions to calculate and explain correlations.
    - import_logging: Functions to configure and manage logging.
    - utils: Utility functions for data validation, cleaning, and file handling.
    - visualization: Functions for setting up plot styles, creating visualizations, and saving plots.
"""

__all__ = [
		"process_data" ,
		"calculate_correlation" ,
		"interpret_correlation" ,
		"load_config" ,
		"process_all_files" ,
		"validate_numeric_data" ,
		"clean_data" ,
		"format_sensor_name" ,
		"load_excel_file" ,
		"create_output_dir" ,
		"log_start_of_process" ,
		"log_end_of_process" ,
		"DataVisualizationError" ,
		]