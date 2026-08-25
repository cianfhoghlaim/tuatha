"""tuatha.tools — the corpus-backed tool surface.

This package used to hold 40 per-subject modules: eight near-identical
copies of five functions, each returning a hardcoded dict without ever
touching a corpus. Since subject is a parameter, one implementation
covers all eight — see :mod:`tuatha.tools.corpus_tools`. The originals
are preserved at ``old/education_ingestion/tools/``.

The tools read; they do not ingest. Ingestion is cianfhoghlaim's job
(see ``tuatha/corpus/CONTRACT.md``).
"""

from __future__ import annotations

from .corpus_tools import (
    bind_subject_tools,
    formative_item_generate,
    marking_scheme_lookup,
    past_paper_lookup,
    response_score,
    syllabus_lookup,
)

#: The subject-agnostic corpus tools, by name.
TOOLS = {
    "syllabus_lookup": syllabus_lookup,
    "past_paper_lookup": past_paper_lookup,
    "marking_scheme_lookup": marking_scheme_lookup,
    "formative_item_generate": formative_item_generate,
    "response_score": response_score,
}

__all__ = [
    "TOOLS",
    "bind_subject_tools",
    "formative_item_generate",
    "marking_scheme_lookup",
    "past_paper_lookup",
    "response_score",
    "syllabus_lookup",
]
