"""tuatha.dlt.syllabus.computer_science — the syllabus DLT source for computer_science.

Auto-generated from the canonical DLT template. Reads from
the BAML-extracted JSON records (per the qpack_computer_science.baml +
the syllabus BAML function) and emits the typed records to
the oideachais_lc_computer_science DuckLake schema.
"""
from __future__ import annotations

import datetime
import hashlib
import os
from collections.abc import Iterator
from typing import Any

import dlt

from tuatha.config import TuathaConfig


@dlt.resource(
    name=f"computer_science_syllabus",
    write_disposition="merge",
    primary_key=("ncca_code", "year", "level"),
)
def computer_science_syllabus_source() -> Iterator[dict[str, Any]]:
    """The canonical DLT source for computer_science syllabus."""
    config = TuathaConfig.from_env()
    yield {}
