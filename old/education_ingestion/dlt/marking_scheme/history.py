"""tuatha.dlt.marking_scheme.history — the marking scheme DLT source for history.

Auto-generated from the canonical DLT template. Reads from
the BAML-extracted JSON records (per the qpack_history.baml +
the marking_scheme BAML function) and emits the typed records to
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
    name=f"history_marking_scheme",
    write_disposition="merge",
    primary_key=("ncca_code", "year", "level"),
)
def history_marking_scheme_source() -> Iterator[dict[str, Any]]:
    """The canonical DLT source for history marking_scheme."""
    config = TuathaConfig.from_env()
    yield {}
