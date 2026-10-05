"""Tests for filename sanitization."""

import re

import pytest

from src.hydrograph_seatek_analysis.utils.security import sanitize_filename


def test_sanitize_filename_removes_path_traversal():
    """Test that path traversal characters are neutralized."""
    malicious_input = "../../../etc/passwd"
    sanitized = sanitize_filename(malicious_input)
    assert ".." not in sanitized
    assert "/" not in sanitized
    assert sanitized.rsplit("-", 1)[0] == "______etc_passwd"


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
    assert sanitize_filename(".hidden_file").rsplit("-", 1)[0] == "hidden_file"
    assert sanitize_filename(" file ").rsplit("-", 1)[0] == "file"
    assert sanitize_filename("..file..").rsplit("-", 1)[0] == "_file_"


def test_sanitize_filename_replaces_invalid_chars():
    """Test replacing special characters like |<>*?:"""
    assert sanitize_filename("file|name<>.txt").rsplit("-", 1)[0] == "file_name__.txt"
    assert sanitize_filename("file*name?.txt").rsplit("-", 1)[0] == "file_name_.txt"


def test_sanitize_filename_limits_length():
    """Test that filename length is limited to prevent DoS."""
    long_input = "A" * 300
    sanitized = sanitize_filename(long_input)
    assert len(sanitized) == 200
    assert sanitized.rsplit("-", 1)[0] == "A" * 183


def test_sanitize_filename_removes_newlines():
    """Test that newlines are removed to prevent log injection."""
    assert sanitize_filename("file\nname").rsplit("-", 1)[0] == "file_name"
    assert sanitize_filename("file\rname").rsplit("-", 1)[0] == "file_name"


@pytest.mark.parametrize(
    "names",
    [
        ("Sensor/1", "Sensor?1", "Sensor_1"),
        ("Sensor_é", "Sensor_ø", "Sensor__"),
        ("Sensor\n1", "Sensor\r1", "Sensor_1"),
        ("Sensor..1", "Sensor...1", "Sensor_1"),
        ("Sensor_1", ".Sensor_1", " Sensor_1 "),
        ("", ".", " ", "unknown"),
        ("A" * 200, "A" * 200 + "x", "A" * 200 + "y"),
    ],
)
def test_sanitize_filename_disambiguates_collisions(names):
    """Lossy transformations keep distinct originals stable, safe and bounded."""
    sanitized = [sanitize_filename(name) for name in names]
    assert len(set(sanitized)) == len(names)
    assert sanitized == [sanitize_filename(name) for name in reversed(names)][::-1]
    for component in sanitized:
        assert re.fullmatch(r"[A-Za-z0-9_. -]+", component)
        assert ".." not in component
        assert component == component.strip(". ")
        assert len(component) <= 200


def test_sanitize_filename_stable_disambiguator():
    """The suffix depends on the original input, independently of process state."""
    assert sanitize_filename("Sensor/1") == "Sensor_1-de8d6fcb62e54c83"


@pytest.mark.parametrize("max_length", [1, 8, 16, 17, 18, 40])
def test_sanitize_filename_short_limits(max_length):
    """The disambiguator fits even when the limit cannot fit the readable stem."""
    first = sanitize_filename("Sensor/1", max_length=max_length)
    second = sanitize_filename("Sensor?1", max_length=max_length)
    assert 0 < len(first) <= max_length
    assert first != second
    assert first == sanitize_filename("Sensor/1", max_length=max_length)


@pytest.mark.parametrize("max_length", [0, -1])
def test_sanitize_filename_rejects_nonpositive_limits(max_length):
    """A filename must have room for a nonempty component."""
    with pytest.raises(ValueError, match="max_length"):
        sanitize_filename("Sensor_1", max_length=max_length)
