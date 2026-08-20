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
from typing import Any

from src.hydrograph_seatek_analysis.core.config import Config
from src.hydrograph_seatek_analysis.core.logger import configure_root_logger
from src.hydrograph_seatek_analysis.data.validator import DataValidator
from src.hydrograph_seatek_analysis.utils.security import is_safe_path


def parse_args() -> argparse.Namespace:
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


def _print_summary_validation(results: dict, config: Config) -> None:
    """Print summary file validation results."""
    print(" 📋 SUMMARY FILE ".center(51, "="))
    if results["summary"]:
        print(f"  ✅ File: {results['summary']['file']}")
        print(f"  📊 Rows: {results['summary']['rows']:,}")
        print(f"  📑 Columns: {', '.join(results['summary']['columns'])}")
        req_icon = "✅" if results["summary"]["required_columns_present"] else "❌"
        print(
            f"  {req_icon} Required columns present: {results['summary']['required_columns_present']}"
        )
        print(
            f"  🏞️  River miles: {', '.join(str(rm) for rm in results['summary']['river_miles'])}"
        )
    else:
        print("  ❌ VALIDATION FAILED: Missing or invalid summary data file")
        print(
            f"     💡 Please ensure '{config.summary_file.name}' is in the '{config.summary_file.parent}' directory."
        )


def _print_hydrograph_validation(results: dict, config: Config) -> None:
    """Print hydrograph file validation results."""
    print("\n" + " 🌊 HYDROGRAPH FILE ".center(51, "="))
    if results["hydrograph"]:
        print(f"  ✅ File: {results['hydrograph']['file']}")
        print(
            f"  📑 River mile sheets: {', '.join(results['hydrograph']['river_mile_sheets'])}"
        )

        for sheet in results["hydrograph"]["sheets"]:
            print(f"\n  📄 Sheet: {sheet['name']}")
            print(f"    📊 Rows: {sheet['rows']:,}")
            req_icon = "✅" if sheet["required_columns_present"] else "❌"
            print(
                f"    {req_icon}  Required columns present: {sheet['required_columns_present']}"
            )
            if sheet["years"]:
                print(f"    📅 Years: {', '.join(str(y) for y in sheet['years'])}")
            if sheet["time_range"]:
                print(
                    f"    ⏱️  Time range: {float(sheet['time_range'][0]):,.0f} to {float(sheet['time_range'][1]):,.0f}"
                )
    else:
        print("  ❌ VALIDATION FAILED: Missing or invalid hydrograph data file")
        print(
            f"     💡 Please ensure '{config.hydro_file.name}' is in the '{config.hydro_file.parent}' directory."
        )


def _print_processed_validation(results: dict) -> None:
    """Print processed files validation results."""
    print("\n" + " ⚙️  PROCESSED FILES ".center(51, "="))
    if results["processed"]:
        for file_result in results["processed"]:
            if "error" in file_result:
                print(
                    f"  ❌ File: {file_result['file']} - ERROR: {file_result['error']}"
                )
                continue

            print(f"\n  ✅ File: {file_result['file']}")
            print(f"    🏞️  River mile: {file_result['river_mile']}")
            print(f"    📊 Rows: {file_result['rows']:,}")
            req_icon = "✅" if file_result["required_columns_present"] else "❌"
            print(
                f"    {req_icon}  Required columns present: {file_result['required_columns_present']}"
            )
            print(f"    📡 Sensor columns: {', '.join(file_result['sensor_columns'])}")

            if file_result["year_range"]:
                print(
                    f"    📅 Year range: {file_result['year_range'][0]} to {file_result['year_range'][1]}"
                )
            if file_result["time_range"]:
                print(
                    f"    ⏱️  Time range: {file_result['time_range'][0]:,.0f} to {file_result['time_range'][1]:,.0f}"
                )
    else:
        print("  ⚠️  No processed files found in the output directory.")
        print("     💡 Please run 'python seatek_processor.py' first to generate them.")


def _print_consistency_validation(results: dict) -> None:
    """Print river mile consistency validation results."""
    if results["river_mile_consistency"]:
        print("\n" + " 🔗 RIVER MILE CONSISTENCY ".center(51, "="))
        all_processed = results["river_mile_consistency"]["all_summary_rms_processed"]
        status_icon = "✅" if all_processed else "⚠️"
        print(
            f"  {status_icon} All summary river miles have processed data: {all_processed}"
        )

        if results["river_mile_consistency"]["missing_processed_rms"]:
            missing_rms_str = ", ".join(
                str(rm)
                for rm in results["river_mile_consistency"]["missing_processed_rms"]
            )
            print(f"  ❌ Missing processed data for river miles: {missing_rms_str}")

        if results["river_mile_consistency"]["extra_processed_rms"]:
            extra_rms_str = ", ".join(
                str(rm)
                for rm in results["river_mile_consistency"]["extra_processed_rms"]
            )
            print(f"  ⚠️  Extra processed data for river miles: {extra_rms_str}")  # fmt: skip


def main() -> int:
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
        config_kwargs: dict[str, Any] = {}
        if args.data_dir:
            config_kwargs["base_dir"] = Path(args.data_dir)

        config = Config(**config_kwargs)  # type: ignore[arg-type]

        # Run validation
        validator = DataValidator(config)
        results = validator.run_validation()

        # Output results
        if args.json or args.output:
            # Convert results to JSON
            json_results = json.dumps(results, indent=2, default=str)

            if args.output:
                # SECURITY: Validate output path to prevent arbitrary file write / path traversal
                output_path = Path(args.output)
                if not is_safe_path(Path.cwd(), output_path):
                    logger.error(
                        f"SECURITY: Attempted path traversal detected. Path outside current directory: {output_path}"
                    )
                    return 1

                # Write to file
                with open(output_path.resolve(), "w") as f:
                    f.write(json_results)
                logger.info(f"Validation results written to {args.output}")
            else:
                # Print to stdout
                print(json_results)
        else:
            # Print human-readable results
            print("\n" + "=" * 10 + " ✨ DATA VALIDATION RESULTS ✨ " + "=" * 10 + "\n")

            _print_summary_validation(results, config)
            _print_hydrograph_validation(results, config)
            _print_processed_validation(results)
            _print_consistency_validation(results)

            # Overall verdict
            print("\n" + " 🏁 OVERALL VALIDATION ".center(51, "="))
            overall_status = "✅ PASSED" if results["overall_valid"] else "❌ FAILED"
            print(f"  STATUS: {overall_status}")
            print("=" * 51 + "\n")

        # Return appropriate exit code
        return 0 if results["overall_valid"] else 1

    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
