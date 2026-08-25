"""tuatha.education.state.persistent_state — the Phase 5 persistent state.

Stores learner progress + mastery evidence + badge ledger. Reads/writes
DuckDB (Phase 1 rung-1+2 tables). Designed to be swapped for Cognee +
Letta in Phase 6 (per the build plan).

The state model:
- learner_progress (student_id, subject, level, rung1_sha256_last_seen)
- mastery_evidence (student_id, subject, lo_code, rung5_root_at_unlock)
- badge_ledger (student_id, subject, badge_id, rung5_root, rung1_sha256)
"""
from __future__ import annotations

import duckdb
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _resolve_db_path() -> Path:
    p = (Path(__file__).resolve().parent.parent.parent
         / "sources" / "duckdb" / "tuatha_official_documents.duckdb")
    s = str(p)
    return Path("/tmp/" + s[len("/private/tmp/"):]) if s.startswith("/private/tmp/") else p


DB_PATH = _resolve_db_path()


DDL = """
CREATE TABLE IF NOT EXISTS learner_progress (
    student_id        VARCHAR NOT NULL,
    subject           VARCHAR NOT NULL,
    level             VARCHAR NOT NULL,
    rung1_sha256_last  VARCHAR NOT NULL,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, subject)
);

CREATE TABLE IF NOT EXISTS mastery_evidence (
    student_id      VARCHAR NOT NULL,
    subject         VARCHAR NOT NULL,
    lo_code         VARCHAR NOT NULL,
    rung5_root      VARCHAR NOT NULL,
    unlocked_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, subject, lo_code)
);

CREATE TABLE IF NOT EXISTS badge_ledger (
    student_id      VARCHAR NOT NULL,
    subject         VARCHAR NOT NULL,
    badge_id        VARCHAR NOT NULL,
    rung5_root      VARCHAR NOT NULL,
    rung1_sha256    VARCHAR NOT NULL,
    minted_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, badge_id)
);
"""


class Phase5PersistentState:
    """The Phase 5 persistent state layer."""

    def __init__(self):
        self.db_path = DB_PATH

    def setup(self):
        con = duckdb.connect(str(self.db_path))
        con.execute(DDL)
        con.close()

    def note_progress(self, student_id: str, subject: str, level: str,
                       rung1_sha256: str):
        con = duckdb.connect(str(self.db_path))
        con.execute(
            "INSERT OR REPLACE INTO learner_progress "
            "(student_id, subject, level, rung1_sha256_last) "
            "VALUES (?, ?, ?, ?)",
            [student_id, subject, level, rung1_sha256])
        con.close()

    def note_mastery(self, student_id: str, subject: str, lo_code: str,
                       rung5_root: str):
        con = duckdb.connect(str(self.db_path))
        con.execute(
            "INSERT OR REPLACE INTO mastery_evidence "
            "(student_id, subject, lo_code, rung5_root) VALUES (?, ?, ?, ?)",
            [student_id, subject, lo_code, rung5_root])
        con.close()

    def mint_badge(self, student_id: str, subject: str, badge_id: str,
                    rung5_root: str, rung1_sha256: str):
        con = duckdb.connect(str(self.db_path))
        con.execute(
            "INSERT OR REPLACE INTO badge_ledger "
            "(student_id, subject, badge_id, rung5_root, rung1_sha256) "
            "VALUES (?, ?, ?, ?, ?)",
            [student_id, subject, badge_id, rung5_root, rung1_sha256])
        con.close()

    def get_progress(self, student_id: str):
        con = duckdb.connect(str(self.db_path), read_only=True)
        rows = con.execute(
            "SELECT subject, level, rung1_sha256_last, updated_at FROM learner_progress "
            "WHERE student_id = ?", [student_id]).fetchall()
        con.close()
        return [{"subject": r[0], "level": r[1],
                 "rung1_sha256_last": r[2], "updated_at": str(r[3])}
                for r in rows]

    def get_mastery(self, student_id: str):
        con = duckdb.connect(str(self.db_path), read_only=True)
        rows = con.execute(
            "SELECT subject, lo_code, rung5_root, unlocked_at FROM mastery_evidence "
            "WHERE student_id = ?", [student_id]).fetchall()
        con.close()
        return [{"subject": r[0], "lo_code": r[1],
                 "rung5_root": r[2], "unlocked_at": str(r[3])}
                for r in rows]

    def get_badges(self, student_id: str):
        con = duckdb.connect(str(self.db_path), read_only=True)
        rows = con.execute(
            "SELECT subject, badge_id, rung5_root, rung1_sha256, minted_at FROM badge_ledger "
            "WHERE student_id = ?", [student_id]).fetchall()
        con.close()
        return [{"subject": r[0], "badge_id": r[1],
                 "rung5_root": r[2], "rung1_sha256": r[3], "minted_at": str(r[4])}
                for r in rows]


def make_phase5_state() -> Phase5PersistentState:
    s = Phase5PersistentState()
    s.setup()
    return s
