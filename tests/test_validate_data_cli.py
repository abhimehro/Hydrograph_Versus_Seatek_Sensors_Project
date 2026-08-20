"""Regression tests for validate_data.py JSON output-path handling."""

import argparse
import json
from types import SimpleNamespace

import validate_data


def _run_main(monkeypatch, tmp_path, output_path):
    """Run the CLI main path with validation dependencies isolated."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        validate_data,
        "parse_args",
        lambda: argparse.Namespace(json=True, output=str(output_path), data_dir=None),
    )
    monkeypatch.setattr(validate_data, "configure_root_logger", lambda **_: None)
    monkeypatch.setattr(validate_data, "Config", lambda **_: object())
    monkeypatch.setattr(
        validate_data,
        "DataValidator",
        lambda _: SimpleNamespace(
            run_validation=lambda: {"overall_valid": True, "summary": {"ok": True}}
        ),
    )
    return validate_data.main()


def test_json_output_uses_validated_in_directory_path(monkeypatch, tmp_path):
    """A validated output path inside the working directory is written as JSON."""
    output_path = tmp_path / "validation.json"

    assert _run_main(monkeypatch, tmp_path, output_path) == 0
    assert json.loads(output_path.read_text(encoding="utf-8")) == {
        "overall_valid": True,
        "summary": {"ok": True},
    }


def test_json_output_rejects_parent_traversal(monkeypatch, tmp_path):
    """A ../ traversal path exits non-zero and creates no file outside the root."""
    outside_path = tmp_path / ".." / f"{tmp_path.name}-traversal-validation.json"

    assert _run_main(monkeypatch, tmp_path, outside_path) == 1
    assert not outside_path.resolve().exists()


def test_json_output_rejects_absolute_path_outside_working_directory(
    monkeypatch, tmp_path
):
    """An absolute path outside the working directory exits non-zero without a write."""
    outside_path = tmp_path.parent / f"{tmp_path.name}-absolute-validation.json"
    assert outside_path.is_absolute()

    assert _run_main(monkeypatch, tmp_path, outside_path) == 1
    assert not outside_path.exists()


def test_json_output_rejects_symlink_escape(monkeypatch, tmp_path):
    """A path through an in-root symlink to an outside directory is rejected."""
    outside_dir = tmp_path.parent / f"{tmp_path.name}-outside"
    outside_dir.mkdir()
    output_link = tmp_path / "output-link"
    output_link.symlink_to(outside_dir, target_is_directory=True)
    escaped_output = output_link / "validation.json"

    assert _run_main(monkeypatch, tmp_path, escaped_output) == 1
    assert not (outside_dir / "validation.json").exists()
