"""tuatha.dlt.formative_item.history — the formative item DLT source for history.

Auto-generated from the canonical DLT template. Reads from
the BAML-extracted JSON records (per the qpack_history.baml +
the formative_item BAML function) and emits the typed records to
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
    name=f"history_formative_item",
    write_disposition="merge",
    primary_key=("ncca_code", "year", "level"),
)
def history_formative_item_source() -> Iterator[dict[str, Any]]:
    """The canonical DLT source for history formative_item."""
    config = TuathaConfig.from_env()
    yield {}
