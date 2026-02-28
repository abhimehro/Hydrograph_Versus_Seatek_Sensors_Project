import pytest
from src.hydrograph_seatek_analysis.app import Application

def test_sanitize_filename_removes_path_traversal():
    """Test that path traversal characters are neutralized."""
    malicious_input = "../../../etc/passwd"
    sanitized = Application._sanitize_filename(malicious_input)
    assert ".." not in sanitized
    assert "/" not in sanitized
    assert sanitized == "._._._etc_passwd"

def test_sanitize_filename_allows_normal_chars():
    """Test that normal characters are kept."""
    normal_input = "Sensor-1_A.txt"
    sanitized = Application._sanitize_filename(normal_input)
    assert sanitized == "Sensor-1_A.txt"

def test_sanitize_filename_handles_numbers():
    """Test with numeric input."""
    assert Application._sanitize_filename(2023) == "2023"
    assert Application._sanitize_filename("2023") == "2023"

def test_sanitize_filename_strips_leading_trailing_dots():
    """Test stripping dots and spaces at edges."""
    assert Application._sanitize_filename(".hidden_file") == "hidden_file"
    assert Application._sanitize_filename(" file ") == "file"
    assert Application._sanitize_filename("..file..") == "_file_"

def test_sanitize_filename_replaces_invalid_chars():
    """Test replacing special characters like |<>*?:"""
    assert Application._sanitize_filename("file|name<>.txt") == "file_name__.txt"
    assert Application._sanitize_filename("file*name?.txt") == "file_name_.txt"
