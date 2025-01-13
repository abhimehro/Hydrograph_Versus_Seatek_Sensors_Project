"""Utility module for managing file paths and directory structure.

This module provides comprehensive file and path management functionality including:
- Project structure validation
- File accessibility checking
- Path normalization
- Memory-efficient file handling
"""

import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Type aliases
PathLike = Union[str, Path]

# Constants
MAX_FILE_SIZE = 1024 * 1024 * 100  # 100MB
ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}
REQUIRED_DIRECTORIES = ['data', 'data/processed', 'data/raw', 'output']


class PathSetupError(Exception):
    """Custom exception for path setup errors."""
    pass


def normalize_path(file_path: PathLike) -> Path:
    """
    Normalize a file path to ensure consistent format.

    Args:
        file_path: Path-like object to normalize

    Returns:
        Path: Normalized absolute path

    Raises:
        PathSetupError: If path normalization fails
    """
    try:
        return Path(file_path).resolve().absolute()
    except Exception as e1:
        raise PathSetupError(f"Failed to normalize path: {str(e1)}")


def validate_file_type(file_path: Path) -> bool:
    """
    Validate if file has allowed extension.

    Args:
        file_path: Path to file to check

    Returns:
        bool: True if file type is allowed, False otherwise
    """
    return file_path.suffix.lower() in ALLOWED_EXTENSIONS


def check_file_size(file_path: Path) -> bool:
    """
    Check if file size is within acceptable limits.

    Args:
        file_path: Path to file to check

    Returns:
        bool: True if file size is acceptable, False otherwise
    """
    try:
        return file_path.stat().st_size <= MAX_FILE_SIZE
    except OSError:
        return False


def validate_excel_structure(file_path: Path) -> bool:
    """
    Validate Excel file structure and content.

    Args:
        file_path: Path to Excel file

    Returns:
        bool: True if structure is valid, False otherwise
    """
    try:
        # Read with minimal memory usage
        with pd.ExcelFile(file_path) as xls:
            sheets = xls.sheet_names
            if not sheets:
                return False

            # Check first sheet structure
            df = pd.read_excel(xls, sheet_name=sheets[0], nrows=1)
            required_cols = {'Time (Seconds)', 'Year'}
            return all(col in df.columns for col in required_cols)
    except Exception as e2:
        logger.error(f"Excel validation error for {file_path}: {str(e2)}")
        return False


def find_project_root() -> Path:
    """
    Find the project root directory by looking for key markers.

    Returns:
        Path: Project root directory path

    Raises:
        PathSetupError: If project root cannot be determined
    """
    try:
        current_dir = Path(__file__).resolve().parent.parent.parent
        while current_dir.name:
            if any((current_dir / marker).exists() for marker in
                   ['.git', 'pyproject.toml', 'setup.py']):
                return current_dir
            if current_dir.parent == current_dir:
                break
            current_dir = current_dir.parent

        raise PathSetupError("Could not find project root directory")
    except Exception as e3:
        raise PathSetupError(f"Error finding project root: {str(e3)}")


def setup_project_structure() -> Dict[str, Path]:
    """
    Set up and validate project directory structure.

    Returns:
        Dict[str, Path]: Dictionary of project directories

    Raises:
        PathSetupError: If directory setup fails
    """
    try:
        project_root = find_project_root()
        directories = {}

        for dir_name in REQUIRED_DIRECTORIES:
            dir_path = project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            directories[dir_name] = dir_path

        return directories
    except Exception as e4:
        raise PathSetupError(f"Failed to setup project structure: {str(e4)}")


def verify_files_exist(required_files: Dict[Path, str]) -> Tuple[bool, List[str]]:
    """
    Verify existence and validity of required files.

    Args:
        required_files: Dictionary mapping file paths to descriptions

    Returns:
        Tuple[bool, List[str]]: (Success status, List of error messages)
    """
    errors = []

    for file_path, description in required_files.items():
        try:
            if not file_path.is_file():
                errors.append(f"Missing {description}")
                continue

            if not validate_file_type(file_path):
                errors.append(f"Invalid file type for {description}")
                continue

            if not check_file_size(file_path):
                errors.append(f"File too large: {description}")
                continue

            if not validate_excel_structure(file_path):
                errors.append(f"Invalid Excel structure: {description}")
                continue

        except Exception as e5:
            errors.append(f"Error checking {description}: {str(e5)}")

    return len(errors) == 0, errors


def check_file_accessibility(file_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Check if file is accessible and readable.

    Args:
        file_path: Path to file to check

    Returns:
        Tuple[bool, Optional[str]]: (Success status, Error message if any)
    """
    try:
        if not file_path.exists():
            return False, "File does not exist"

        # Check read permissions
        if not os.access(file_path, os.R_OK):
            return False, "File is not readable"

        # Try opening file
        with open(file_path, 'rb') as f:
            f.read(1)

        return True, None

    except Exception as e6:
        return False, str(e6)


def get_data_paths() -> Optional[Tuple[Path, Path, Path]]:
    """
    Get paths to required data files.

    Returns:
        Optional[Tuple[Path, Path, Path]]: Tuple of required file paths,
        or None if validation fails
    """
    try:
        directories = setup_project_structure()

        rm_file = directories['data/processed'] / "RM_54.0.xlsx"
        summary_file = directories['data/raw'] / "Data_Summary.xlsx"
        hydro_file = directories['data/raw'] / "Hydrograph_Seatek_Data.xlsx"
        required_files = {
            rm_file: "River Mile data file",
            summary_file: "Summary data file",
            hydro_file: "Hydrograph data file"
}
        success, errors = verify_files_exist(required_files)
        if not success:
            for error in errors:
                logger.error(error)
            return None

        # Verify accessibility
        for file_path in [rm_file, summary_file, hydro_file]:
            success, error = check_file_accessibility(file_path)
            if not success:
                logger.error(f"Access error for {file_path}: {error}")
                return None

        return rm_file, summary_file, hydro_file

    except Exception as e6:
        logger.error(f"Error getting data paths: {str(e6)}")
        return None


def cleanup_output_directory(output_dir: Path) -> None:
    """
    Clean up output directory before processing.

    Args:
        output_dir: Path to output directory
    """
    try:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True)
    except Exception as e7:
        logger.warning(f"Error cleaning output directory: {str(e7)}")


def create_backup(file_path: Path) -> Optional[Path]:
    """
    Create backup of important files.

    Args:
        file_path: Path to file to back up

    Returns:
        Optional[Path]: Path to back up file if successful
    """
    try:
        backup_path = file_path.parent / f"{file_path.stem}_backup{file_path.suffix}"
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e8:
        logger.error(f"Backup failed for {file_path}: {str(e8)}")
        return None


if __name__ == "__main__":
    try:
        # Test all functionality
        logger.info("Testing path setup utilities...")

        # Verify project structure
        dirs = setup_project_structure()
        logger.info("Project directories created successfully")

        # Get and validate data paths
        paths = get_data_paths()
        if paths:
            rm_path, summary_path, hydro_path = paths
            logger.info("All required files found and validated")

            # Create backups
            for path in paths:
                if backup := create_backup(path):
                    logger.info(f"Backup created: {backup}")

        logger.info("Path setup tests completed successfully")

    except Exception as e:
        logger.error(f"Path setup tests failed: {str(e)}")
        sys.exit(1)