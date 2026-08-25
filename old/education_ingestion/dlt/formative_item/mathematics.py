"""tuatha.dlt.formative_item.mathematics — the formative item DLT source for mathematics.

Auto-generated from the canonical DLT template. Reads from
the BAML-extracted JSON records (per the qpack_mathematics.baml +
the formative_item BAML function) and emits the typed records to
the oideachais_lc_mathematics DuckLake schema.
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
    name=f"mathematics_formative_item",
    write_disposition="merge",
    primary_key=("ncca_code", "year", "level"),
)
def mathematics_formative_item_source() -> Iterator[dict[str, Any]]:
    """The canonical DLT source for mathematics formative_item."""
    config = TuathaConfig.from_env()
    yield {}
