"""tuatha.dlt.past_paper.geography — the past paper DLT source for geography.

Auto-generated from the canonical DLT template. Reads from
the BAML-extracted JSON records (per the qpack_geography.baml +
the past_paper BAML function) and emits the typed records to
the oideachais_lc_geography DuckLake schema.
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
    name=f"geography_past_paper",
    write_disposition="merge",
    primary_key=("ncca_code", "year", "level"),
)
def geography_past_paper_source() -> Iterator[dict[str, Any]]:
    """The canonical DLT source for geography past_paper."""
    config = TuathaConfig.from_env()
    yield {}
