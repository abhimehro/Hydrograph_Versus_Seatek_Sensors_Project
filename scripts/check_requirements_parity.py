#!/usr/bin/env python3
"""Verify that ``==`` dependency pins stay aligned across manifests."""

# This repo declares exact pins in five places that must not drift
# (docs/technical/installation.md):
#
# - ``pyproject.toml`` ``[tool.poetry.dependencies]``           <-> requirements.txt
# - ``pyproject.toml`` ``[tool.poetry.group.dev.dependencies]`` <-> requirements-ci.txt
# - ``poetry.lock`` ``[[package]]`` entries                      covers both
# - ``.pre-commit-config.yaml`` hook ``rev:`` pins               mirrors pyproject
#
# Dependabot bumps a dependency in only one manifest per PR, so pins drift
# silently (Lesson 0fy: a poetry-side mypy bump was green while the CI
# typecheck job still installed the old mypy from requirements-ci.txt).
# Running this check in CI before dependency installation turns that drift
# into a visible failure on the PR that introduces it.
#
# Exits 0 when every manifest agrees, 1 with a mismatch report otherwise.
# Stdlib only; requires Python 3.11+ for tomllib.

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"
REQUIREMENTS_TXT = REPO_ROOT / "requirements.txt"
REQUIREMENTS_CI = REPO_ROOT / "requirements-ci.txt"
POETRY_LOCK = REPO_ROOT / "poetry.lock"
PRE_COMMIT_CONFIG = REPO_ROOT / ".pre-commit-config.yaml"

_PIN_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)\s*==\s*([^\s;#]+)")

_FIX_HINT = (
    "Fix by aligning the == pins across pyproject.toml, "
    "requirements*.txt, and poetry.lock (poetry lock)."
)


def _normalize(name: str) -> str:
    """PEP 503 normalization so ``foo_bar`` and ``foo-bar`` compare equal."""
    return re.sub(r"[-_.]+", "-", name).lower()


def pyproject_pins(path: Path) -> dict[str, dict[str, str]]:
    """Return {section: {normalized_name: version}} for ``==`` pins only."""
    # Sections are ``main`` plus one key per dependency group. Non-``==``
    # specs (e.g. ``python = "^3.12"``) are skipped: they declare no exact
    # pin for requirements files to mirror.
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    poetry = data.get("tool", {}).get("poetry", {})
    sections: dict[str, dict[str, str]] = {}

    def collect(target: dict[str, str], deps: dict[str, object]) -> None:
        for name, spec in deps.items():
            if _normalize(name) == "python":
                continue
            if isinstance(spec, str) and spec.startswith("=="):
                target[_normalize(name)] = spec[2:]

    collect(sections.setdefault("main", {}), poetry.get("dependencies", {}))
    for group_name, group in poetry.get("group", {}).items():
        collect(
            sections.setdefault(f"group.{group_name}", {}),
            group.get("dependencies", {}),
        )
    return sections


def requirements_pins(path: Path) -> dict[str, str]:
    """Return {normalized_name: version} for ``name==version`` lines."""
    # Comments, blank lines, options (``-r`` includes, ``-e``, index flags)
    # and non-``==`` lines are ignored.
    pins: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        match = _PIN_RE.match(line)
        if match:
            pins[_normalize(match.group(1))] = match.group(2)
    return pins


def lock_pins(path: Path) -> dict[str, str]:
    """Return {normalized_name: version} for every locked package."""
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return {_normalize(pkg["name"]): pkg["version"] for pkg in data.get("package", [])}


def pre_commit_revs(path: Path) -> dict[str, str]:
    """Return {tool_name: rev} for hook repos in .pre-commit-config.yaml."""
    # Each ``- repo: <url>`` block carries one ``rev:`` line. The tool name
    # is the URL's last path segment with a ``mirrors-`` prefix stripped
    # (``pre-commit/mirrors-mypy`` -> ``mypy``). Revs may be optionally
    # quoted and are returned without a leading ``v`` so ``v2.4.0``
    # compares equal to ``==2.4.0``.
    revs: dict[str, str] = {}
    current_repo: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        repo_match = re.match(r"\s*-\s*repo:\s*(\S+)", line)
        if repo_match:
            current_repo = repo_match.group(1)
            continue
        rev_match = re.match(r"""\s*rev:\s*(['"]?)([^'"\s]+)\1""", line)
        if rev_match and current_repo is not None:
            tool = current_repo.rstrip("/").rsplit("/", 1)[-1]
            tool = tool.removeprefix("mirrors-")
            revs[_normalize(tool)] = rev_match.group(2).removeprefix("v")
            current_repo = None
    return revs


def diff_pins(
    left_label: str,
    left: dict[str, str],
    right_label: str,
    right: dict[str, str],
) -> list[str]:
    """Report asymmetric or mismatched pins between two manifests."""
    problems: list[str] = []
    for name in sorted(set(left) | set(right)):
        if name not in left:
            problems.append(f"{name}: only in {right_label} ({right[name]})")
        elif name not in right:
            problems.append(f"{name}: only in {left_label} ({left[name]})")
        elif left[name] != right[name]:
            problems.append(
                f"{name}: {left_label} has {left[name]}, "
                f"{right_label} has {right[name]}"
            )
    return problems


def diff_pre_commit(declared: dict[str, str]) -> list[str]:
    """Report pyproject pins whose .pre-commit-config.yaml rev disagrees."""
    hook_revs = pre_commit_revs(PRE_COMMIT_CONFIG)
    problems: list[str] = []
    for tool in sorted(set(hook_revs) & set(declared)):
        if hook_revs[tool] != declared[tool]:
            problems.append(
                f"{tool}: pyproject.toml has {declared[tool]}, "
                f".pre-commit-config.yaml has {hook_revs[tool]}"
            )
    return problems


def manifest_problems(
    sections: dict[str, dict[str, str]], declared: dict[str, str]
) -> list[str]:
    """Report drift between pyproject pins and requirements/lock manifests."""
    runtime_pins = requirements_pins(REQUIREMENTS_TXT)
    ci_pins = requirements_pins(REQUIREMENTS_CI)
    locked = lock_pins(POETRY_LOCK)
    # The lockfile legitimately holds transitive-only packages; compare it
    # only on names pyproject actually declares.
    locked_declared = {n: v for n, v in locked.items() if n in declared}
    problems = diff_pins(
        "pyproject.toml [tool.poetry.dependencies]",
        sections.get("main", {}),
        "requirements.txt",
        runtime_pins,
    )
    problems += diff_pins(
        "pyproject.toml [tool.poetry.group.dev.dependencies]",
        sections.get("group.dev", {}),
        "requirements-ci.txt",
        ci_pins,
    )
    problems += diff_pins("pyproject.toml", declared, "poetry.lock", locked_declared)
    return problems


def collect_problems() -> tuple[list[str], int]:
    """Gather all drift reports plus the count of pins checked."""
    sections = pyproject_pins(PYPROJECT)
    declared = {name: ver for pins in sections.values() for name, ver in pins.items()}
    ci_pins = requirements_pins(REQUIREMENTS_CI)
    runtime_pins = requirements_pins(REQUIREMENTS_TXT)
    problems = manifest_problems(sections, declared)
    problems += diff_pre_commit(declared)
    return problems, len(declared) + len(ci_pins) + len(runtime_pins)


def main() -> int:
    """Run all parity checks and print a mismatch report."""
    problems, checked = collect_problems()
    if problems:
        lines = "\n".join(f"  - {problem}" for problem in problems)
        print(f"Dependency pin drift detected:\n{lines}\n{_FIX_HINT}", file=sys.stderr)
        return 1
    print(f"Pin parity OK: {checked} pins aligned across 5 manifests.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
