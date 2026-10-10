"""Tests for filename sanitization."""

from src.hydrograph_seatek_analysis.utils.security import sanitize_filename


def test_sanitize_filename_removes_path_traversal() -> None:
    """Test that path traversal characters are neutralized."""
    malicious_input = "../../../etc/passwd"
    sanitized = sanitize_filename(malicious_input)
    assert ".." not in sanitized
    assert "/" not in sanitized
    assert sanitized == "______etc_passwd"


def test_sanitize_filename_allows_normal_chars() -> None:
    """Test that normal characters are kept."""
    normal_input = "Sensor-1_A.txt"
    sanitized = sanitize_filename(normal_input)
    assert sanitized == "Sensor-1_A.txt"


def test_sanitize_filename_handles_numbers() -> None:
    """Test with numeric input."""
    assert sanitize_filename("2023") == "2023"


def test_sanitize_filename_strips_leading_trailing_dots() -> None:
    """Test stripping dots and spaces at edges."""
    assert sanitize_filename(".hidden_file") == "hidden_file"
    assert sanitize_filename(" file ") == "file"
    assert sanitize_filename("..file..") == "_file_"


def test_sanitize_filename_replaces_invalid_chars() -> None:
    """Test replacing special characters like |<>*?:"""
    assert sanitize_filename("file|name<>.txt") == "file_name__.txt"
    assert sanitize_filename("file*name?.txt") == "file_name_.txt"


def test_sanitize_filename_limits_length() -> None:
    """Test that filename length is limited to prevent DoS."""
    long_input = "A" * 300
    sanitized = sanitize_filename(long_input)
    assert len(sanitized) == 200
    assert sanitized == "A" * 200


def test_sanitize_filename_removes_newlines() -> None:
    """Test that newlines are removed to prevent log injection."""
    assert sanitize_filename("file\nname") == "file_name"
    assert sanitize_filename("file\rname") == "file_name"
