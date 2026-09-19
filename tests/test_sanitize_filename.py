"""Tests for filename sanitization."""

from src.hydrograph_seatek_analysis.utils.security import sanitize_filename


def test_sanitize_filename_removes_path_traversal():
    """Test that path traversal characters are neutralized."""
    malicious_input = "../../../etc/passwd"
    sanitized = sanitize_filename(malicious_input)
    assert ".." not in sanitized
    assert "/" not in sanitized
    assert sanitized == "______etc_passwd"


def test_sanitize_filename_allows_normal_chars():
    """Test that normal characters are kept."""
    normal_input = "Sensor-1_A.txt"
    sanitized = sanitize_filename(normal_input)
    assert sanitized == "Sensor-1_A.txt"


def test_sanitize_filename_handles_numbers():
    """Test with numeric input."""
    assert sanitize_filename(2023) == "2023"
    assert sanitize_filename("2023") == "2023"


def test_sanitize_filename_strips_leading_trailing_dots():
    """Test stripping dots and spaces at edges."""
    assert sanitize_filename(".hidden_file") == "hidden_file"
    assert sanitize_filename(" file ") == "file"
    assert sanitize_filename("..file..") == "_file_"


def test_sanitize_filename_replaces_invalid_chars():
    """Test replacing special characters like |<>*?:"""
    assert sanitize_filename("file|name<>.txt") == "file_name__.txt"
    assert sanitize_filename("file*name?.txt") == "file_name_.txt"


def test_sanitize_filename_limits_length():
    """Test that filename length is limited to prevent DoS."""
    long_input = "A" * 300
    sanitized = sanitize_filename(long_input)
    assert len(sanitized) == 200
    assert sanitized == "A" * 200


def test_sanitize_filename_removes_newlines():
    """Test that newlines are removed to prevent log injection."""
    assert sanitize_filename("file\nname") == "file_name"
    assert sanitize_filename("file\rname") == "file_name"


def test_sanitize_filename_preserves_unicode_name_uniqueness():
    """Distinct Unicode names should not resolve to the same path component."""
    first = sanitize_filename("Sensor_é")
    second = sanitize_filename("Sensor_ø")

    assert first != second
    assert first.isascii() and second.isascii()
    assert len(first) <= 200 and len(second) <= 200


def test_sanitize_filename_unicode_digest_respects_max_length():
    """Unicode names retain an ASCII digest within the requested limit."""
    sanitized = sanitize_filename("Sensor_é", max_length=20)

    assert sanitized.isascii()
    assert len(sanitized) <= 20
