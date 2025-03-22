"""Logging configuration for the Hydrograph and Seatek Sensor Analysis package."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Union


# Try to import colorlog, but provide fallback if not available
try:
    import colorlog
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    console: bool = True,
    file_size_limit: int = 10_000_000,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Create a configured logger with color support (if available).

    Args:
        name: Logger name
        level: Logging level
        log_file: Optional path to log file
        console: Whether to log to console
        file_size_limit: Max file size before rotation
        backup_count: Number of backup files to keep

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
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler if requested
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Create file handler if log_file is provided
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=file_size_limit,
            backupCount=backup_count
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def configure_root_logger(
    level: int = logging.INFO,
    log_dir: Optional[Union[str, Path]] = None,
    log_filename: str = "app.log"
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
        log_file = log_path / log_filename
    
    # Configure the root logger
    setup_logger(
        name="",  # Root logger
        level=level,
        log_file=log_file
    )