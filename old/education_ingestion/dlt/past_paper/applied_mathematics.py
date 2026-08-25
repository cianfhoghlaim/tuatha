"""tuatha.dlt.past_paper.applied_mathematics — the past paper DLT source for applied_mathematics.

Auto-generated from the canonical DLT template. Reads from
the BAML-extracted JSON records (per the qpack_applied_mathematics.baml +
the past_paper BAML function) and emits the typed records to
the oideachais_lc_applied_mathematics DuckLake schema.
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
    name=f"applied_mathematics_past_paper",
    write_disposition="merge",
    primary_key=("ncca_code", "year", "level"),
)
def applied_mathematics_past_paper_source() -> Iterator[dict[str, Any]]:
    """The canonical DLT source for applied_mathematics past_paper."""
    config = TuathaConfig.from_env()
    yield {}
