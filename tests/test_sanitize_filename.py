"""Tests for filename sanitization."""

import hashlib

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


def test_sanitize_filename_removes_unicode() -> None:
    """Test that Unicode homoglyphs are replaced to prevent bypass."""
    # The 'а' in this string is a Cyrillic homoglyph (U+0430), not an ASCII 'a'
    homoglyph_input = "file_nаme.txt"
    sanitized = sanitize_filename(homoglyph_input)
    digest = hashlib.sha256(homoglyph_input.encode("utf-8")).hexdigest()[:12]
    assert sanitized == f"file_n_me.txt_{digest}"


def test_sanitize_filename_preserves_unicode_name_uniqueness() -> None:
    """Distinct Unicode names must not resolve to the same path component."""
    assert sanitize_filename("Sensor_é") != sanitize_filename("Sensor_ø")
