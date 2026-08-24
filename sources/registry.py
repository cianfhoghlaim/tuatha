"""tuatha/sources/registry.py — the per-source policy catalogue.

Operator-facing view of every official source in the corpus. Per the
cianchosaint source-catalogue pattern: each source has a uniform schema
(URL + DLT source linkage + OSINT allowlist flag + coverage + cadence).

W1 will populate this from the official_doc_fetcher (rung 1).
"""
from __future__ import annotations

from typing import Any


SOURCES: list[dict[str, Any]] = [
    # 8 jurisdictions
    {"id": "ncca.ie", "jurisdiction": "Ireland", "name": "NCCA"},
    {"id": "aqa.org.uk", "jurisdiction": "England", "name": "AQA"},
    {"id": "ocr.org.uk", "jurisdiction": "England", "name": "OCR"},
    {"id": "qualifications.pearson.com", "jurisdiction": "England", "name": "Pearson"},
    {"id": "sqa.org.uk", "jurisdiction": "Scotland", "name": "SQA"},
    {"id": "wjec.co.uk", "jurisdiction": "Wales", "name": "WJEC"},
    {"id": "ccea.org.uk", "jurisdiction": "Northern Ireland", "name": "CCEA"},
    {"id": "gov.im/education", "jurisdiction": "Isle of Man", "name": "IoM Education"},
    # 5 safeguarding bodies
    {"id": "gov.ie/education", "category": "safeguarding", "name": "gov.ie Education"},
    {"id": "gov.uk/dfe", "category": "safeguarding", "name": "UK DfE"},
    {"id": "education.gov.scot", "category": "safeguarding", "name": "Scotland Education"},
    {"id": "gov.wales/education", "category": "safeguarding", "name": "Wales Education"},
    {"id": "ccea.org.uk/safeguarding", "category": "safeguarding", "name": "CCEA Safeguarding"},
]
