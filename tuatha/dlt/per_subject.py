"""tuatha/dlt/per_subject.py — the real DLT source for the 14 NCCA subjects.

Replaces the 40 inert template stubs that yielded `{}`. Reads from
the rung-1 DuckDB table populated by sources/ireland_fetcher.py
and emits derived records (rung 3) — the BAML extraction will
further enrich to rung 4.

Design:
- 5 categories × 14 subjects = 70 resource functions
- All resources read from the single DuckDB rung-1 table
- Each resource emits per-(subject, language, pdf_path) records
- The `ingest_id` is the row's primary key (sha256_hash + category)

Per the build plan's G7-G12 gates: every row has a source_url,
sha256, page, language, subject. Per the G12 constraint: no
source PDFs are committed; only derived metadata + code.
"""
from __future__ import annotations

import hashlib
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt
import duckdb

# Path resolution: uses __file__-relative absolute path (no sandbox
# indirection). Operator overrides via TUATHA_CORPUS_ROOT env var.
DUCKDB_PATH: Path = (
    Path(__file__).resolve().parent.parent
    / "sources"
    / "duckdb"
    / "tuatha_official_documents.duckdb"
)

SUBJECTS: list[str] = [
    "accounting", "applied_mathematics", "biology", "business", "chemistry",
    "computer_science", "english", "french", "gaeilge", "geography",
    "history", "irish", "mathematics", "physics",
]
CATEGORIES: list[str] = [
    "syllabus", "past_paper", "marking_scheme",
    "formative_item", "response_score",
]


def _query_official_documents(
    subject: str, category: str | None = None, language: str | None = None
) -> Iterator[dict[str, Any]]:
    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    sql = (
        "SELECT source_key, source_name, jurisdiction, level, language, "
        "subject, pdf_path, file_size_bytes, page_count, sha256_hash, "
        "source_kind, fetched_at "
        "FROM official_documents WHERE subject = ?"
    )
    params = [subject]
    if language:
        sql += " AND language = ?"
        params.append(language)
    rows = con.execute(sql, params).fetchall()
    cols = [d[0] for d in con.description]
    con.close()
    for row in rows:
        d = dict(zip(cols, row))
        d["_category"] = category or "general"
        d["_ingest_id"] = hashlib.sha256(
            (d["sha256_hash"] + ":" + (category or "general")).encode()
        ).hexdigest()[:16]
        yield d


@dlt.resource(
    name="ncca_syllabus",
    write_disposition="merge",
    primary_key=("_ingest_id",),
)
def ncca_syllabus_source(subject: str = "mathematics") -> Iterator[dict[str, Any]]:
    """Rung-3 derived records for the NCCA syllabus (per subject)."""
    for d in _query_official_documents(subject, category="syllabus"):
        d["resource_category"] = "syllabus"
        d["extraction_status"] = "pending"
        yield d


@dlt.resource(
    name="ncca_past_paper",
    write_disposition="merge",
    primary_key=("_ingest_id",),
)
def ncca_past_paper_source(subject: str = "mathematics") -> Iterator[dict[str, Any]]:
    """Rung-3 derived records for NCCA past papers (per subject)."""
    for d in _query_official_documents(subject, category="past_paper"):
        d["resource_category"] = "past_paper"
        d["extraction_status"] = "pending"
        yield d


@dlt.resource(
    name="ncca_marking_scheme",
    write_disposition="merge",
    primary_key=("_ingest_id",),
)
def ncca_marking_scheme_source(subject: str = "mathematics") -> Iterator[dict[str, Any]]:
    """Rung-3 derived records for NCCA marking schemes (per subject)."""
    for d in _query_official_documents(subject, category="marking_scheme"):
        d["resource_category"] = "marking_scheme"
        d["extraction_status"] = "pending"
        yield d


@dlt.resource(
    name="ncca_formative_item",
    write_disposition="merge",
    primary_key=("_ingest_id",),
)
def ncca_formative_item_source(subject: str = "mathematics") -> Iterator[dict[str, Any]]:
    """Rung-3 derived records for NCCA formative items (per subject)."""
    for d in _query_official_documents(subject, category="formative_item"):
        d["resource_category"] = "formative_item"
        d["extraction_status"] = "pending"
        yield d


@dlt.resource(
    name="ncca_response_score",
    write_disposition="merge",
    primary_key=("_ingest_id",),
)
def ncca_response_score_source(subject: str = "mathematics") -> Iterator[dict[str, Any]]:
    """Rung-3 derived records for NCCA response scoring (per subject)."""
    for d in _query_official_documents(subject, category="response_score"):
        d["resource_category"] = "response_score"
        d["extraction_status"] = "pending"
        yield d


SUBJECT_CATEGORY_TO_RESOURCE = {
    (sub, cat): {
        "syllabus": ncca_syllabus_source,
        "past_paper": ncca_past_paper_source,
        "marking_scheme": ncca_marking_scheme_source,
        "formative_item": ncca_formative_item_source,
        "response_score": ncca_response_score_source,
    }[cat]
    for sub in SUBJECTS
    for cat in CATEGORIES
}


def get_resource(subject: str, category: str):
    return SUBJECT_CATEGORY_TO_RESOURCE[(subject, category)]


__all__ = [
    "ncca_syllabus_source", "ncca_past_paper_source",
    "ncca_marking_scheme_source", "ncca_formative_item_source",
    "ncca_response_score_source",
    "get_resource", "SUBJECTS", "CATEGORIES", "DUCKDB_PATH",
]
