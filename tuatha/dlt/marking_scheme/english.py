"""tuatha.dlt.marking_scheme.english — the marking scheme DLT source for english.

Auto-generated from the canonical DLT template. Reads from
the BAML-extracted JSON records (per the qpack_english.baml +
the marking_scheme BAML function) and emits the typed records to
the oideachais_lc_english DuckLake schema.
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
    name=f"english_marking_scheme",
    write_disposition="merge",
    primary_key=("ncca_code", "year", "level"),
)
def english_marking_scheme_source() -> Iterator[dict[str, Any]]:
    """The canonical DLT source for english marking_scheme."""
    config = TuathaConfig.from_env()
    yield {}
