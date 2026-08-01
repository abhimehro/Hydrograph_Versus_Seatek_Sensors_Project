"""CLI reporting utilities for data validation."""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

from src.hydrograph_seatek_analysis.core.config import Config
from src.hydrograph_seatek_analysis.utils.security import is_safe_path


class ValidationReporter:
    """Handles formatting and outputting validation results."""

    def __init__(self, logger: logging.Logger):
        """Initialize with a logger."""
        self.logger = logger

    def handle_json_output(
        self, args: argparse.Namespace, results: Dict[str, Any]
    ) -> bool:
        """Handle writing results to JSON format."""
        json_results = json.dumps(results, indent=2, default=str)

        if not args.output:
            print(json_results)
            return True

        output_path = Path(args.output)

        # SECURITY: Validate output path to prevent path traversal
        if not is_safe_path(Path.cwd(), output_path):
            self.logger.error(
                f"SECURITY: Attempted path traversal detected. "
                f"Path outside current directory: {args.output}"
            )
            print(
                f"Error: Output path '{args.output}' is invalid "
                f"(must be within current directory).",
                file=sys.stderr,
            )
            return False

        with open(output_path, "w") as f:
            f.write(json_results)
        self.logger.info(f"Validation results written to {output_path}")
        return True

    def _print_sheet_result(self, sheet: Dict[str, Any]) -> None:
        """Print a single hydrograph sheet validation result."""
        print(f"\n  📄 Sheet: {sheet['name']}")
        print(f"    📊 Rows: {sheet['rows']:,}")
        req_icon = "✅" if sheet["required_columns_present"] else "❌"
        print(
            f"    {req_icon}  Required columns present: "
            f"{sheet['required_columns_present']}"
        )
        if sheet["years"]:
            years_str = ", ".join(str(y) for y in sheet["years"])
            print(f"    📅 Years: {years_str}")
        if sheet["time_range"]:
            t0 = float(sheet["time_range"][0])
            t1 = float(sheet["time_range"][1])
            print(f"    ⏱️  Time range: {t0:,.0f} to {t1:,.0f}")

    def _print_single_processed_file(self, file_result: Dict[str, Any]) -> None:
        """Print a single processed file validation result."""
        if "error" in file_result:
            print(f"  ❌ File: {file_result['file']} - ERROR: {file_result['error']}")
            return

        print(f"\n  ✅ File: {file_result['file']}")
        print(f"    🏞️  River mile: {file_result['river_mile']}")
        print(f"    📊 Rows: {file_result['rows']:,}")
        req_icon = "✅" if file_result["required_columns_present"] else "❌"
        print(
            f"    {req_icon}  Required columns present: "
            f"{file_result['required_columns_present']}"
        )
        sensor_cols = ", ".join(file_result["sensor_columns"])
        print(f"    📡 Sensor columns: {sensor_cols}")

        if file_result["year_range"]:
            y0 = file_result["year_range"][0]
            y1 = file_result["year_range"][1]
            print(f"    📅 Year range: {y0} to {y1}")
        if file_result["time_range"]:
            t0 = file_result["time_range"][0]
            t1 = file_result["time_range"][1]
            print(f"    ⏱️  Time range: {t0:,.0f} to {t1:,.0f}")

    def print_human_readable_results(
        self, results: Dict[str, Any], config: Config
    ) -> None:
        """Print validation results in a human-readable format."""
        print("\n" + "=" * 10 + " ✨ DATA VALIDATION RESULTS ✨ " + "=" * 10 + "\n")

        self._print_summary(results, config)
        self._print_hydrograph(results, config)
        self._print_processed(results)
        self._print_consistency(results)
        self._print_overall(results)

    def _print_summary(self, results: Dict[str, Any], config: Config) -> None:
        print(" 📋 SUMMARY FILE ".center(51, "="))
        if results["summary"]:
            print(f"  ✅ File: {results['summary']['file']}")
            print(f"  📊 Rows: {results['summary']['rows']:,}")
            cols_str = ", ".join(results["summary"]["columns"])
            print(f"  📑 Columns: {cols_str}")
            req_icon = "✅" if results["summary"]["required_columns_present"] else "❌"
            print(
                f"  {req_icon} Required columns present: "
                f"{results['summary']['required_columns_present']}"
            )
            rm_str = ", ".join(str(rm) for rm in results["summary"]["river_miles"])
            print(f"  🏞️  River miles: {rm_str}")
        else:
            print("  ❌ VALIDATION FAILED: Missing or invalid summary data file")
            print(
                f"     💡 Please ensure '{config.summary_file.name}' is in the "
                f"'{config.summary_file.parent}' directory."
            )

    def _print_hydrograph(self, results: Dict[str, Any], config: Config) -> None:
        print("\n" + " 🌊 HYDROGRAPH FILE ".center(51, "="))
        if results["hydrograph"]:
            print(f"  ✅ File: {results['hydrograph']['file']}")
            rm_sheets = ", ".join(results["hydrograph"]["river_mile_sheets"])
            print(f"  📑 River mile sheets: {rm_sheets}")
            for sheet in results["hydrograph"]["sheets"]:
                self._print_sheet_result(sheet)
        else:
            print("  ❌ VALIDATION FAILED: Missing or invalid hydrograph data file")
            print(
                f"     💡 Please ensure '{config.hydro_file.name}' is in the "
                f"'{config.hydro_file.parent}' directory."
            )

    def _print_processed(self, results: Dict[str, Any]) -> None:
        print("\n" + " ⚙️  PROCESSED FILES ".center(51, "="))
        if results["processed"]:
            for file_result in results["processed"]:
                self._print_single_processed_file(file_result)
        else:
            print("  ⚠️  No processed files found in the output directory.")
            print(
                "     💡 Please run 'python seatek_processor.py' first to "
                "generate them."
            )

    def _print_consistency(self, results: Dict[str, Any]) -> None:
        if results["river_mile_consistency"]:
            print("\n" + " 🔗 RIVER MILE CONSISTENCY ".center(51, "="))
            all_processed = results["river_mile_consistency"][
                "all_summary_rms_processed"
            ]
            status_icon = "✅" if all_processed else "⚠️"
            print(
                f"  {status_icon} All summary river miles have processed data: "
                f"{all_processed}"
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
                print(f"  ⚠️  Extra processed data for river miles: {extra_rms_str}")

    def _print_overall(self, results: Dict[str, Any]) -> None:
        print("\n" + " 🏁 OVERALL VALIDATION ".center(51, "="))
        overall_status = "✅ PASSED" if results["overall_valid"] else "❌ FAILED"
        print(f"  STATUS: {overall_status}")
        print("=" * 51 + "\n")
