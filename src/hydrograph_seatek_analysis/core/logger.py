"""Logging configuration for the Hydrograph and Seatek Sensor Analysis package."""

import logging
import logging.handlers
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from utils.security import is_safe_path, sanitize_filename


@dataclass
class FileLogConfig:
    """Configuration for file-based logging."""

    path: Union[str, Path]
    size_limit: int = 10_000_000  # 10MB
    backup_count: int = 5


# Try to import colorlog, but provide fallback if not available
try:
    import colorlog

    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False


def setup_logger(
    name: str,
    level: int = logging.INFO,
    console: bool = True,
    file_config: Optional[FileLogConfig] = None,
) -> logging.Logger:
    """
    Create a configured logger with color support (if available).

    Args:
        name: Logger name
        level: Logging level
        console: Whether to log to console
        file_config: Optional configuration for file logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()

    logger.setLevel(level)
    logger.propagate = False

    # Create formatters
    if HAS_COLORLOG and console:
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create console handler if requested
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # Create file handler if file_config is provided
    if file_config:
        log_path = Path(file_config.path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=file_config.size_limit,
            backupCount=file_config.backup_count,
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def configure_root_logger(
    level: int = logging.INFO,
    log_dir: Optional[Union[str, Path]] = None,
    log_filename: str = "app.log",
) -> None:
    """
    Configure the root logger for the application.

    Args:
        level: Logging level
        log_dir: Directory for log files
        log_filename: Name of the log file
    """
    log_file = None
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # SECURITY: Sanitize the filename to prevent path traversal
        safe_filename = sanitize_filename(log_filename)
        log_file = log_path / safe_filename

        # SECURITY: Verify that the resolved path is safely within the log directory
        if not is_safe_path(log_path, log_file):
            log_file = log_path / "app.log"

    # Configure the root logger
    file_config = FileLogConfig(path=log_file) if log_file else None
    setup_logger(name="", level=level, file_config=file_config)  # Root logger
