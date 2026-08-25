"""tuatha.baml_runtime.extractor — rung-3 to rung-4 BAML runner."""
from __future__ import annotations
import asyncio, hashlib, json
from pathlib import Path
from typing import Any
import duckdb
from . import SUBJECTS, CATEGORY_TO_FUNCTION, extract_for_row


def _resolve_db_path() -> Path:
    p = (Path(__file__).resolve().parent.parent.parent
         / "sources" / "duckdb" / "tuatha_official_documents.duckdb")
    s = str(p)
    return Path("/tmp/" + s[len("/private/tmp/"):]) if s.startswith("/private/tmp/") else p


DB_PATH = _resolve_db_path()
CATEGORIES = list(CATEGORY_TO_FUNCTION.keys())
RUNG4_DDL = """
CREATE TABLE IF NOT EXISTS baml_extractions (
    ingest_id    VARCHAR  NOT NULL,
    subject      VARCHAR  NOT NULL,
    category     VARCHAR  NOT NULL,
    language     VARCHAR  NOT NULL,
    rung1_sha256 VARCHAR  NOT NULL,
    source_page  INT,
    output_json  VARCHAR,
    confidence   FLOAT,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ingest_id)
);
"""


def _read_rung1_rows(db, subject, language):
    sql = ("SELECT source_key, source_name, jurisdiction, level, language, "
           "subject, pdf_path, file_size_bytes, page_count, sha256_hash, "
           "source_kind, first_page_text "
           "FROM (SELECT * FROM official_documents WHERE subject = ? AND language = ?) "
           "JOIN (SELECT pdf_path AS p_path, MAX(first_page_text) AS first_page_text "
           "FROM pdf_page_metadata WHERE page_number = 1 GROUP BY p_path) "
           "ON pdf_path = p_path")
    rows = db.execute(sql, [subject, language]).fetchall()
    cols = [d[0] for d in db.description]
    return [dict(zip(cols, r)) for r in rows]


async def run_for_subject(db, subject, language="en"):
    rows = _read_rung1_rows(db, subject, language)
    n_extracted = 0; n_failed = 0
    for r in rows:
        for cat in CATEGORIES:
            ingest_id = hashlib.sha256((r["sha256_hash"] + ":" + cat).encode()).hexdigest()[:16]
            output = await extract_for_row(subject, cat, language, r)
            if output is None:
                n_failed += 1; continue
            try:
                if hasattr(output, "model_dump"):
                    output_json = json.dumps(output.model_dump()); confidence = getattr(output, "confidence", None) or 1.0
                elif hasattr(output, "dict"):
                    output_json = json.dumps(output.dict()); confidence = 1.0
                else:
                    output_json = json.dumps(output); confidence = 1.0
            except Exception:
                output_json = json.dumps(str(output)); confidence = 0.0
            db.execute(
                "INSERT OR REPLACE INTO baml_extractions "
                "(ingest_id, subject, category, language, rung1_sha256, source_page, output_json, confidence) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [ingest_id, subject, cat, language, r["sha256_hash"], r["page_count"],
                 output_json, confidence],
            )
            n_extracted += 1
    return n_extracted, n_failed


async def run_all_subjects():
    db = duckdb.connect(str(DB_PATH))
    db.execute(RUNG4_DDL)
    total_e = 0; total_f = 0
    for subject in SUBJECTS:
        for language in ("en", "ga"):
            try: e, f = await run_for_subject(db, subject, language); total_e += e; total_f += f
            except Exception: total_f += 1
    db.close()
    print(f"  Phase 2: extracted={total_e} failed={total_f} "
          f"(across {len(SUBJECTS)} subjects × 2 languages × {len(CATEGORIES)} categories)")


if __name__ == "__main__":
    asyncio.run(run_all_subjects())
