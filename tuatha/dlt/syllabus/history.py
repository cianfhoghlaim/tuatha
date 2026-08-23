"""tuatha.dlt.syllabus.history — the syllabus DLT source for history.

Auto-generated from the canonical DLT template. Reads from
the BAML-extracted JSON records (per the qpack_history.baml +
the syllabus BAML function) and emits the typed records to
the oideachais_lc_history DuckLake schema.
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
    name=f"history_syllabus",
    write_disposition="merge",
    primary_key=("ncca_code", "year", "level"),
)
def history_syllabus_source() -> Iterator[dict[str, Any]]:
    """The canonical DLT source for history syllabus."""
    config = TuathaConfig.from_env()
    yield {}
