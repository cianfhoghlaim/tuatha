"""tuatha/sources/ireland_fetcher.py — rung-1 (Document) + rung-2 (Location) layer.

Ireland-first fetcher. Scans the local NCCA PDF tree at
$TUATHA_CORPUS_ROOT/{subject}/{language}/, computes
sha256 + page_count + first_page_text, and emits one row per
PDF (rung 1) + one row per page (rung 2).

The 148 NCCA PDFs are path-only referenced; the real files
live at $TUATHA_CORPUS_ROOT (default: ~/dev/cianchosaint/leaving_certificate/).

Per G12, this script NEVER commits the source PDFs to the
public repo. Only derived metadata (sha256, page references,
learning outcome codes) is persisted.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

import duckdb
import pypdf

DEFAULT_CORPUS_ROOT = Path(
    os.environ.get(
        "TUATHA_CORPUS_ROOT",
        str(Path.home() / "dev" / "cianchosaint" / "leaving_certificate"),
    )
)

NCCA_LANGUAGES = ["en", "ga"]


def _resolve_db_path() -> Path:
    p = (
        Path(__file__).resolve().parent
        / "duckdb"
        / "tuatha_official_documents.duckdb"
    )
    s = str(p)
    if s.startswith("/private/tmp/"):
        return Path("/tmp/" + s[len("/private/tmp/"):])
    return p


DUCKDB_PATH = _resolve_db_path()
DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)

RUNG1_DDL = """
CREATE TABLE IF NOT EXISTS official_documents (
    source_key         VARCHAR  NOT NULL,
    source_name        VARCHAR  NOT NULL,
    jurisdiction       VARCHAR  NOT NULL,
    level              VARCHAR  NOT NULL,
    language           VARCHAR  NOT NULL,
    subject            VARCHAR  NOT NULL,
    pdf_path           VARCHAR  NOT NULL,
    file_size_bytes    BIGINT   NOT NULL,
    page_count         INTEGER  NOT NULL,
    sha256_hash        VARCHAR  NOT NULL,
    source_kind        VARCHAR  NOT NULL DEFAULT 'local_filesystem',
    fetched_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (jurisdiction, language, subject, pdf_path)
);
"""

RUNG2_DDL = """
CREATE TABLE IF NOT EXISTS pdf_page_metadata (
    source_key         VARCHAR  NOT NULL,
    pdf_path           VARCHAR  NOT NULL,
    page_number        INTEGER  NOT NULL,
    fonts_detected     VARCHAR[],
    image_count        INTEGER  NOT NULL DEFAULT 0,
    has_text_layer     BOOLEAN   NOT NULL DEFAULT true,
    first_page_text    TEXT,
    extracted_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pdf_path, page_number)
);
"""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_stat(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def page_count(path: Path) -> int:
    try:
        return len(pypdf.PdfReader(str(path)).pages)
    except Exception:
        return 0


def first_page_text(path: Path, max_chars: int = 500) -> str:
    try:
        pages = pypdf.PdfReader(str(path)).pages
        if not pages:
            return ""
        return (pages[0].extract_text() or "")[:max_chars]
    except Exception:
        return ""


def discover_pdfs(corpus_root: Path):
    for subject_path in sorted(corpus_root.iterdir()):
        if not subject_path.is_dir():
            continue
        subject = subject_path.name
        for lang in NCCA_LANGUAGES:
            lang_path = subject_path / lang
            if not lang_path.is_dir():
                continue
            for pdf_path in sorted(lang_path.glob("*.pdf")):
                yield ("Ireland", subject, pdf_path)


def run() -> int:
    con = duckdb.connect(str(DUCKDB_PATH))
    con.execute(RUNG1_DDL)
    con.execute(RUNG2_DDL)

    n_docs, n_pages = 0, 0
    for jurisdiction, subject, pdf_path in discover_pdfs(DEFAULT_CORPUS_ROOT):
        size = safe_stat(pdf_path)
        sha = sha256_file(pdf_path)
        pages = page_count(pdf_path)
        lang = pdf_path.parent.name
        level = "LC" if "Leaving" in pdf_path.name else "JC"

        con.execute(
            "INSERT OR REPLACE INTO official_documents "
            "(source_key, source_name, jurisdiction, level, language, "
            "subject, pdf_path, file_size_bytes, page_count, "
            "sha256_hash, source_kind) VALUES (?, ?, ?, ?, ?, ?, ?, "
            "?, ?, ?, 'local_filesystem')",
            [
                f"ncca.{subject}.{lang}", f"NCCA {subject.upper()} "
                f"({lang.upper()})",
                jurisdiction, level, lang, subject,
                str(pdf_path), size, pages, sha,
            ],
        )
        n_docs += 1
        for page_num in range(1, pages + 1):
            first_text = first_page_text(pdf_path) if page_num == 1 else ""
            con.execute(
                "INSERT OR REPLACE INTO pdf_page_metadata "
                "(source_key, pdf_path, page_number, "
                "fonts_detected, image_count, has_text_layer, "
                "first_page_text) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    f"ncca.{subject}.{lang}", str(pdf_path),
                    page_num, [], 0, pages > 0, first_text,
                ],
            )
            n_pages += 1

    con.close()
    print(
        f"  ingested {n_docs} documents ({n_pages} pages) "
        f"into {DUCKDB_PATH}"
    )
    return n_docs


if __name__ == "__main__":
    run()
