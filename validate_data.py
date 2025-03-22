#!/usr/bin/env python3

"""
Seatek Data Validation Tool
---------------------------
Description: Validates the structure and content of Seatek and Hydrograph data files.

Author: Abhi Mehrotra
Date: March 2025
Version: 3.0.0
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from src.hydrograph_seatek_analysis.core.config import Config
from src.hydrograph_seatek_analysis.core.logger import configure_root_logger
from src.hydrograph_seatek_analysis.data.validator import DataValidator


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Validate Seatek and Hydrograph data files")
    
    parser.add_argument(
        "--json", 
        action="store_true",
        help="Output validation results as JSON"
    )
    
    parser.add_argument(
        "--output", 
        type=str,
        help="Output file for validation results"
    )
    
    parser.add_argument(
        "--data-dir", 
        type=str,
        help="Base data directory (overrides default)"
    )
    
    return parser.parse_args()


def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()
    
    # Configure logging
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    configure_root_logger(
        level=logging.INFO,
        log_dir=log_dir,
        log_filename="data_validation.log"
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting data validation")
    
    try:
        # Create config
        config_kwargs = {}
        if args.data_dir:
            config_kwargs["base_dir"] = Path(args.data_dir)
            
        config = Config(**config_kwargs)
        
        # Run validation
        validator = DataValidator(config)
        results = validator.run_validation()
        
        # Output results
        if args.json or args.output:
            # Convert results to JSON
            json_results = json.dumps(results, indent=2, default=str)
            
            if args.output:
                # Write to file
                with open(args.output, "w") as f:
                    f.write(json_results)
                logger.info(f"Validation results written to {args.output}")
            else:
                # Print to stdout
                print(json_results)
        else:
            # Print human-readable results
            print("\n===== DATA VALIDATION RESULTS =====\n")
            
            # Summary file validation
            print("SUMMARY FILE:")
            if results["summary"]:
                print(f"  File: {results['summary']['file']}")
                print(f"  Rows: {results['summary']['rows']}")
                print(f"  Columns: {', '.join(results['summary']['columns'])}")
                print(f"  Required columns present: {results['summary']['required_columns_present']}")
                print(f"  River miles: {results['summary']['river_miles']}")
            else:
                print("  VALIDATION FAILED")
            
            # Hydrograph file validation
            print("\nHYDROGRAPH FILE:")
            if results["hydrograph"]:
                print(f"  File: {results['hydrograph']['file']}")
                print(f"  River mile sheets: {results['hydrograph']['river_mile_sheets']}")
                
                for sheet in results["hydrograph"]["sheets"]:
                    print(f"\n  Sheet: {sheet['name']}")
                    print(f"    Rows: {sheet['rows']}")
                    print(f"    Required columns present: {sheet['required_columns_present']}")
                    if sheet['years']:
                        print(f"    Years: {sheet['years']}")
                    if sheet['time_range']:
                        print(f"    Time range: {sheet['time_range']}")
            else:
                print("  VALIDATION FAILED")
            
            # Processed files validation
            print("\nPROCESSED FILES:")
            if results["processed"]:
                for file_result in results["processed"]:
                    if "error" in file_result:
                        print(f"  File: {file_result['file']} - ERROR: {file_result['error']}")
                        continue
                        
                    print(f"\n  File: {file_result['file']}")
                    print(f"    River mile: {file_result['river_mile']}")
                    print(f"    Rows: {file_result['rows']}")
                    print(f"    Required columns present: {file_result['required_columns_present']}")
                    print(f"    Sensor columns: {file_result['sensor_columns']}")
                    
                    if file_result['year_range']:
                        print(f"    Year range: {file_result['year_range']}")
                    if file_result['time_range']:
                        print(f"    Time range: {file_result['time_range']}")
            else:
                print("  No processed files found")
            
            # River mile consistency
            if results["river_mile_consistency"]:
                print("\nRIVER MILE CONSISTENCY:")
                print(f"  All summary river miles have processed data: {results['river_mile_consistency']['all_summary_rms_processed']}")
                
                if results['river_mile_consistency']['missing_processed_rms']:
                    print(f"  Missing processed data for river miles: {results['river_mile_consistency']['missing_processed_rms']}")
                    
                if results['river_mile_consistency']['extra_processed_rms']:
                    print(f"  Extra processed data for river miles: {results['river_mile_consistency']['extra_processed_rms']}")
            
            # Overall verdict
            print("\nOVERALL VALIDATION:")
            print(f"  PASSED: {results['overall_valid']}")
            print("\n=====================================\n")
        
        # Return appropriate exit code
        return 0 if results["overall_valid"] else 1
        
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())