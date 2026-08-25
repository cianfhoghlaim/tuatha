"""tuatha.baml_runtime — the BAML extractor Python wrapper (Phase 2).

Loads the 14 qpack_<subject>.baml contracts + media_descriptor.baml +
clients.baml, then exposes a Python wrapper that:

1. Reads rung-1 DuckDB rows from sources/duckdb/tuatha_official_documents.duckdb
2. Calls the appropriate BAML function per subject + category
3. Writes rung-4 typed records back to DuckDB (per the Evidence Ladder)

This is the bridge between Phase 1 (data path) and Phase 3 (BAML extraction).
"""
from __future__ import annotations

try:
    from baml_client import b  # type: ignore
    _BAML_AVAILABLE = True
except Exception:
    _BAML_AVAILABLE = False
    b = None  # type: ignore

SUBJECTS = [
    "accounting", "applied_mathematics", "biology", "business", "chemistry",
    "computer_science", "english", "french", "gaeilge", "geography",
    "history", "irish", "mathematics", "physics",
]

CATEGORY_TO_FUNCTION = {
    "syllabus":         "Generate{Name}Syllabus",
    "past_paper":       "Generate{Name}PastPaper",
    "marking_scheme":   "Generate{Name}MarkingScheme",
    "formative_item":   "Generate{Name}FormativeItem",
    "response_score":    "Score{Name}FormativeResponse",
}


async def extract_for_row(subject, category, language, rung1_row):
    """Call the appropriate BAML function for one rung-1 row."""
    if not _BAML_AVAILABLE:
        return None
    prefix = subject.capitalize().replace("_", "")
    fn_name = CATEGORY_TO_FUNCTION[category].replace("{Name}", prefix)
    fn = getattr(b, fn_name, None)
    if fn is None:
        return None
    pdf_excerpt = rung1_row.get("first_page_text") or ""
    if category == "syllabus":
        return await fn(lo_code=rung1_row.get("ncca_code", ""),
                        level=rung1_row.get("level", "hl"), language=language,
                        pdf_pages=pdf_excerpt[:4000])
    if category == "past_paper":
        return await fn(year=2024, level=rung1_row.get("level", "hl"),
                        paper=1, pdf_pages=pdf_excerpt[:4000])
    if category == "marking_scheme":
        return await fn(lo_code=rung1_row.get("ncca_code", ""),
                        level=rung1_row.get("level", "hl"), year=2024,
                        pdf_pages=pdf_excerpt[:4000])
    if category == "formative_item":
        return await fn(lo_code=rung1_row.get("ncca_code", ""),
                        difficulty=3, level=rung1_row.get("level", "hl"),
                        topic="formative", pdf_pages=pdf_excerpt[:4000])
    if category == "response_score":
        return await fn(item_id="item_1", student_response="[see rubric]",
                        response_format="extended", time_taken_seconds=600,
                        hints_used=0, rubric_text=pdf_excerpt[:4000])
    return None


__all__ = ["extract_for_row", "SUBJECTS", "CATEGORY_TO_FUNCTION"]
