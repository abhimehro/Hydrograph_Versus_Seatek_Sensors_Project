"""Tests for the logger module."""

import logging
import tempfile
from pathlib import Path

import pytest

from src.hydrograph_seatek_analysis.core.logger import setup_logger, configure_root_logger


def test_setup_logger_default():
    """Test that setup_logger creates a logger with default settings."""
    logger = setup_logger("test_logger")
    
    assert logger.name == "test_logger"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1  # Console handler
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert not logger.propagate


def test_setup_logger_with_file():
    """Test that setup_logger creates a logger with a file handler."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "test.log"
        logger = setup_logger("test_logger", log_file=log_file)
        
        assert logger.name == "test_logger"
        assert len(logger.handlers) == 2  # Console handler and file handler
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert isinstance(logger.handlers[1], logging.handlers.RotatingFileHandler)
        assert logger.handlers[1].baseFilename == str(log_file)


def test_setup_logger_custom_level():
    """Test that setup_logger respects custom log levels."""
    logger = setup_logger("test_logger", level=logging.DEBUG)
    
    assert logger.level == logging.DEBUG


def test_configure_root_logger():
    """Test that configure_root_logger configures the root logger."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir)
        configure_root_logger(level=logging.WARNING, log_dir=log_dir)
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING
        
        # Check for handlers (one for console, one for file)
        assert len(root_logger.handlers) > 0