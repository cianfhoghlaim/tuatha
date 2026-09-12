"""Shared helpers for the Tuatha ANAM Dashboard notebook tabs."""

from __future__ import annotations

import os

import lancedb
import pyarrow as pa

#: Resolved from the environment (Infisical hydrates it in deployment).
LANCE_URI = os.environ.get("TUATHA_LANCE_URI", "s3://garage/lance")

TABLE_HADES = "cianfhoghlaim.tuatha.hades.boons"
TABLE_COMIC = "cianfhoghlaim.tuatha.comic.particles"
TABLE_GBA = "cianfhoghlaim.tuatha.gba.magic"
TABLE_ANAM = "cianfhoghlaim.tuatha.anam_particles"


def open_db() -> lancedb.DBConnection:
    """Open the Lance connection (s3:// in prod; file:// in dev)."""
    return lancedb.connect(LANCE_URI)


def query_via_lance_scan(db, table: str) -> pa.Table:
    """Federate a Lance table through DuckDB lance_scan().

    Per the lancedb skill "Ibis + DuckDB lance_scan()" — the canonical
    federated SQL pattern.
    """
    import duckdb

    con = duckdb.connect()
    con.execute("INSTALL lance; LOAD lance;")
    safe = table.replace(".", "_")
    con.execute(
        f"CREATE OR REPLACE VIEW {safe} AS "
        f"SELECT * FROM lance_scan('{LANCE_URI}/{table}')"
    )
    return con.execute(f"SELECT * FROM {safe}").arrow_table()


# Colour maths lives in tuatha.theming.color — the ANAM quality gate
# needs it too, and production code should not import from a notebook.
from tuatha.theming.color import delta_e, hex_to_rgb, rgb_to_lab  # noqa: E402

__all__ = [
    "LANCE_URI",
    "TABLE_ANAM",
    "TABLE_COMIC",
    "TABLE_GBA",
    "TABLE_HADES",
    "delta_e",
    "hex_to_rgb",
    "open_db",
    "query_via_lance_scan",
    "rgb_to_lab",
]
