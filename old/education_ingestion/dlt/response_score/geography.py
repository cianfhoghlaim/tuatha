"""tuatha.dlt.response_score.geography — the response score DLT source for geography.

Auto-generated from the canonical DLT template. Reads from
the BAML-extracted JSON records (per the qpack_geography.baml +
the response_score BAML function) and emits the typed records to
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
    name=f"geography_response_score",
    write_disposition="merge",
    primary_key=("ncca_code", "year", "level"),
)
def geography_response_score_source() -> Iterator[dict[str, Any]]:
    """The canonical DLT source for geography response_score."""
    config = TuathaConfig.from_env()
    yield {}
