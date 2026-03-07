"""Security utilities for the Seatek data processing pipeline."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def validate_file_size(file_path: Path, max_size_bytes: int) -> None:
    """
    Validate that a file exists and does not exceed the maximum allowed size.

    Args:
        file_path: Path to the file to check.
        max_size_bytes: Maximum allowed file size in bytes.

    Raises:
        ValueError: If the file size exceeds the maximum limit.
        FileNotFoundError: If the file does not exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size = file_path.stat().st_size
    if file_size > max_size_bytes:
        logger.error(f"File {file_path.name} size ({file_size} bytes) exceeds maximum limit ({max_size_bytes} bytes)")
        raise ValueError(f"File {file_path.name} exceeds maximum size of {max_size_bytes} bytes")
