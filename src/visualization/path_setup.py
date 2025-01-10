"""Utility module for managing file paths and directory structure."""

import os
import sys
from pathlib import Path
from typing import Tuple, Optional

__all__ = ['find_project_root', 'setup_data_directories', 'verify_files_exist', 'get_data_paths']


def find_project_root() -> Path:
    """
    Find the project root directory by looking for key markers.

    Returns:
        Path: Project root directory path
    """
    current_dir = Path(__file__).resolve().parent.parent.parent
    while current_dir.name:
        # Look for markers that indicate project root
        if (current_dir / "data").exists() or \
                (current_dir / ".git").exists() or \
                (current_dir / "pyproject.toml").exists():
            return current_dir
        parent = current_dir.parent
        if parent == current_dir:
            break
        current_dir = parent

    return Path.cwd()


def setup_data_directories() -> Tuple[Path, Path]:
    """
    Set up and verify the existence of necessary data directories.

    Returns:
        Tuple[Path, Path]: (processed_dir, raw_dir) paths

    Raises:
        FileNotFoundError: If required directories cannot be created
    """
    project_root = find_project_root()
    data_dir = project_root / "data"
    processed_dir = data_dir / "processed"
    raw_dir = data_dir / "raw"

    # Create directories if they don't exist
    for directory in [data_dir, processed_dir, raw_dir]:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise FileNotFoundError(
                f"Cannot create directory {directory}. Permission denied."
            )

    print(f"Project root: {project_root}")
    print(f"Data directory: {data_dir}")
    print(f"Processed directory: {processed_dir}")
    print(f"Raw directory: {raw_dir}")

    return processed_dir, raw_dir


def verify_files_exist() -> bool:
    """
    Verify that all required data files exist in their expected locations.

    Returns:
        bool: True if all required files exist, False otherwise
    """
    try:
        processed_dir, raw_dir = setup_data_directories()

        required_files = {
            processed_dir / "RM_54.0.xlsx": "RM_54.0.xlsx in processed directory",
            raw_dir / "Data_Summary.xlsx": "Data_Summary.xlsx in raw directory",
            raw_dir / "Hydrograph_Seatek_Data.xlsx": "Hydrograph_Seatek_Data.xlsx in raw directory"
        }

        missing_files = []
        for file_path, description in required_files.items():
            if not file_path.is_file():
                missing_files.append(description)

        if missing_files:
            print("\nMissing required files:")
            for file in missing_files:
                print(f"- {file}")
            return False

        print("\nAll required files found!")
        return True

    except Exception as e:
        print(f"Error verifying files: {str(e)}")
        return False


def get_data_paths() -> Optional[Tuple[Path, Path, Path]]:
    """
    Get paths to required data files.

    Returns:
        Optional[Tuple[Path, Path, Path]]: Tuple containing paths to:
            - RM_54.0.xlsx
            - Data_Summary.xlsx
            - Hydrograph_Seatek_Data.xlsx
        Returns None if any file is missing.
    """
    try:
        processed_dir, raw_dir = setup_data_directories()

        rm_file = processed_dir / "RM_54.0.xlsx"
        summary_file = raw_dir / "Data_Summary.xlsx"
        hydrograph_file = raw_dir / "Hydrograph_Seatek_Data.xlsx"

        if all(f.is_file() for f in [rm_file, summary_file, hydrograph_file]):
            return rm_file, summary_file, hydrograph_file

        return None

    except Exception as e:
        print(f"Error getting data paths: {str(e)}")
        return None


if __name__ == "__main__":
    # Test the path setup
    if verify_files_exist():
        paths = get_data_paths()
        if paths:
            rm_path, summary_path, hydro_path = paths
            print("\nFile paths:")
            print(f"RM file: {rm_path}")
            print(f"Summary file: {summary_path}")
            print(f"Hydrograph file: {hydro_path}")
    else:
        sys.exit(1)