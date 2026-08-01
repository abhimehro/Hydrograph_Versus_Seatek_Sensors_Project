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
import logging
import sys
from pathlib import Path

from src.hydrograph_seatek_analysis.core.config import Config
from src.hydrograph_seatek_analysis.core.logger import configure_root_logger
from src.hydrograph_seatek_analysis.data.validator import DataValidator
from src.hydrograph_seatek_analysis.visualization.cli_reporter import ValidationReporter


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate Seatek and Hydrograph data files"
    )

    parser.add_argument(
        "--json", action="store_true", help="Output validation results as JSON"
    )

    parser.add_argument("--output", type=str, help="Output file for validation results")

    parser.add_argument(
        "--data-dir", type=str, help="Base data directory (overrides default)"
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
        level=logging.INFO, log_dir=log_dir, log_filename="data_validation.log"
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
        reporter = ValidationReporter(logger)

        if args.json or args.output:
            if not reporter.handle_json_output(args, results):
                return 1
        else:
            reporter.print_human_readable_results(results, config)

        # Return appropriate exit code
        return 0 if results["overall_valid"] else 1

    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
