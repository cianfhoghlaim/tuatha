"""tuatha.ci.dagger — the Dagger pipeline for the new tuatha/ sub-project.

Per the parent's CI pattern.
"""
from __future__ import annotations

import dagger


async def pipeline(source: dagger.Directory) -> str:
    """The canonical Dagger pipeline for the new tuatha/ sub-project."""
    return await (
        dagger.container()
        .from_("python:3.12-slim")
        .with_directory("/src", source)
        .with_workdir("/src")
        .with_exec(["pip", "install", "-e", ".[dev]"])
        .with_exec(["ruff", "check", "."])
        .with_exec(["pytest", "-q"])
        .stdout()
    )
