"""Security utilities for the Seatek data processing pipeline."""

import logging
import re
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


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    Sanitize a filename string to prevent path traversal and other vulnerabilities.

    Args:
        filename: The untrusted filename string (e.g., from an Excel column or sheet)
        max_length: Maximum allowed length for the filename

    Returns:
        A sanitized string safe for use as a path component.
    """
    if not isinstance(filename, str):
        filename = str(filename)

    # Keep only word characters (letters, digits, underscore), dashes, dots, and whitespace
    sanitized = re.sub(r"[^\w\-\.\s]", "_", filename)
    # Prevent directory traversal dots like ..
    sanitized = re.sub(r"\.{2,}", "_", sanitized)
    # Strip leading/trailing whitespaces and dots
    sanitized = sanitized.strip(". ")

    # Ensure we never return an empty filename after sanitization
    if not sanitized:
        sanitized = "unknown"
    # SECURITY: Limit filename length to prevent path-length DoS or file system errors
    return (sanitized or "_")[:max_length]
