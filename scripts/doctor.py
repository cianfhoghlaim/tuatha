#!/usr/bin/env python3
"""Boundary + hygiene gate for the tuatha repository.

Run via ``mise run tuatha:doctor``.

The checks encode invariants that are easy to violate accidentally and
expensive to discover late:

1. **No cross-repo imports.** tuatha and cianfhoghlaim share a lakehouse
   namespace but not a Python path. An ``import cianfhoghlaim`` resolves
   on the author's machine and nowhere else, so it fails silently into a
   permanently-disabled fallback branch.
2. **No dangling mise task targets.** A ``depends`` entry naming a task
   that does not exist makes the whole task unrunnable.
3. **Licence coherence.** ``pyproject.toml`` and the licence file must
   agree, and no contradicting licence file may sit beside them.
4. **No machine-specific absolute paths.** A hardcoded ``/Users/<name>``
   path works for exactly one developer.
5. **Every relative import resolves.** A module copied without its
   dependencies imports cleanly right up until something tries to use
   it. The ADK layer sat in that state for its whole life.
6. **Every tracked Python file parses.**

Exits 0 when every check passes, 1 otherwise, printing one line per
failure.
"""

from __future__ import annotations

import ast
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

#: Directories excluded from every check. ``old/`` is the hard archive:
#: it preserves superseded code verbatim and is not importable.
EXCLUDED_PARTS = {"old", ".git", ".venv", "node_modules", "__pycache__", ".baml_client"}

#: The repo tuatha must never import from. See tuatha/corpus/CONTRACT.md.
FOREIGN_ROOTS = ("cianfhoghlaim", "cianchosaint", "ciandlithe", "gemini_hackathon")

#: Matches an absolute path into a specific user's home directory.
HOME_PATH = re.compile(r"/Users/(?!\{)[A-Za-z0-9._-]+/")


@dataclass
class Report:
    """Accumulates failures across checks."""

    failures: list[str] = field(default_factory=list)
    checked: dict[str, int] = field(default_factory=dict)

    def fail(self, message: str) -> None:
        self.failures.append(message)

    def counted(self, check: str, n: int) -> None:
        self.checked[check] = n


def python_files() -> list[Path]:
    """Return every in-scope Python file, archive excluded."""
    return [
        p
        for p in REPO.rglob("*.py")
        if not EXCLUDED_PARTS & set(p.relative_to(REPO).parts)
    ]


def check_no_cross_repo_imports(report: Report) -> None:
    """Fail on any import whose root package is a sibling repository."""
    files = python_files()
    for path in files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:
            continue  # reported by check_files_parse
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                root = name.split(".", 1)[0]
                if root in FOREIGN_ROOTS:
                    rel = path.relative_to(REPO)
                    report.fail(
                        f"cross-repo import: {rel}:{node.lineno} imports {name!r} "
                        f"(root package {root!r} is a sibling repo, not a dependency)"
                    )
    report.counted("cross-repo imports", len(files))


def check_mise_tasks(report: Report) -> None:
    """Fail on a ``depends`` entry naming an undefined task."""
    mise = REPO / "mise.toml"
    if not mise.exists():
        report.fail("mise.toml is missing")
        return

    data = tomllib.loads(mise.read_text(encoding="utf-8"))
    tasks = data.get("tasks", {})
    defined = set(tasks)

    for name, body in tasks.items():
        if not isinstance(body, dict):
            continue
        for dep in body.get("depends", []):
            if dep not in defined:
                report.fail(
                    f"dangling mise dependency: task {name!r} depends on {dep!r}, "
                    f"which is not defined in mise.toml"
                )
    report.counted("mise tasks", len(defined))


def check_licence(report: Report) -> None:
    """Fail when the declared licence and the licence file disagree."""
    pyproject = REPO / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    declared = data.get("project", {}).get("license")

    if not isinstance(declared, str):
        report.fail(
            f"pyproject.toml declares license={declared!r}; expected an SPDX string"
        )
        return

    licence_files = [p for p in REPO.glob("LICENSE*") if p.is_file()]
    if not licence_files:
        report.fail("no LICENSE file found at the repository root")
        return

    for path in licence_files:
        head = path.read_text(encoding="utf-8", errors="replace")[:400]
        if declared == "BUSL-1.1" and "Business Source License" not in head:
            report.fail(
                f"licence mismatch: pyproject declares {declared!r} but "
                f"{path.name} does not contain the Business Source License text"
            )
        if declared != "MIT" and head.lstrip().startswith("MIT License"):
            report.fail(
                f"licence mismatch: pyproject declares {declared!r} but "
                f"{path.name} contains MIT License text"
            )
    report.counted("licence files", len(licence_files))


def check_no_home_paths(report: Report) -> None:
    """Fail on absolute paths into a specific user's home directory."""
    files = python_files()
    for path in files:
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
        ):
            match = HOME_PATH.search(line)
            if match:
                rel = path.relative_to(REPO)
                report.fail(
                    f"machine-specific path: {rel}:{lineno} contains "
                    f"{match.group(0)!r}; read it from the environment instead"
                )
    report.counted("home-path scan", len(files))


def check_relative_imports(report: Report) -> None:
    """Fail on a relative import that names a module which is not there.

    Copying a module without its dependencies produces code that parses,
    lints and imports at package level, then fails only when something
    actually calls it — or, worse, sits behind a bare ``except
    ImportError`` and silently disables a feature.
    """
    files = python_files()
    for path in files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:
            continue  # reported by check_files_parse
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or not node.level:
                continue
            base = path.parent
            for _ in range(node.level - 1):
                base = base.parent
            target = base / (node.module or "").replace(".", "/")
            resolved = (
                target.with_suffix(".py").exists()
                or (target / "__init__.py").exists()
                or target.is_dir()
            )
            if not resolved:
                dots = "." * node.level
                report.fail(
                    f"unresolvable relative import: {path.relative_to(REPO)}:"
                    f"{node.lineno} imports from {dots}{node.module or ''}, "
                    "which does not exist in this checkout"
                )
    report.counted("relative imports", len(files))


def check_files_parse(report: Report) -> None:
    """Fail on any Python file that does not parse."""
    files = python_files()
    for path in files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            report.fail(f"syntax error: {path.relative_to(REPO)}:{exc.lineno} {exc.msg}")
    report.counted("parsed files", len(files))


CHECKS = (
    ("cross-repo imports", check_no_cross_repo_imports),
    ("mise task graph", check_mise_tasks),
    ("licence coherence", check_licence),
    ("machine-specific paths", check_no_home_paths),
    ("relative imports", check_relative_imports),
    ("python syntax", check_files_parse),
)


def main() -> int:
    report = Report()
    for label, check in CHECKS:
        before = len(report.failures)
        check(report)
        status = "FAIL" if len(report.failures) > before else "ok"
        count = report.checked.get(label, report.checked.get(label.split()[0], ""))
        print(f"  {status:>4}  {label}" + (f"  ({count} inspected)" if count else ""))

    if report.failures:
        print(f"\n{len(report.failures)} failure(s):\n")
        for failure in report.failures:
            print(f"  - {failure}")
        return 1

    print("\ntuatha:doctor — all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
