import sys
from unittest import mock

sys.modules["pandas"] = mock.MagicMock()
sys.modules["numpy"] = mock.MagicMock()
sys.modules["matplotlib"] = mock.MagicMock()
sys.modules["matplotlib.pyplot"] = mock.MagicMock()
sys.modules["matplotlib.figure"] = mock.MagicMock()
sys.modules["matplotlib.axes"] = mock.MagicMock()
sys.modules["matplotlib.lines"] = mock.MagicMock()
sys.modules["seaborn"] = mock.MagicMock()
sys.modules["matplotlib.dates"] = mock.MagicMock()
sys.modules["matplotlib.ticker"] = mock.MagicMock()

from utils.security import sanitize_filename


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
