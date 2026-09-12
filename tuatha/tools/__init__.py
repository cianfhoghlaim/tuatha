"""tuatha.tools — the canonical per-subject tool surface.

After the 2026-08-27 ANAM capture pipeline port + 3-corpus
expansion change (T1.7), the 40 per-subject tool stub files
were collapsed into a single `bind_subject_tools(<subject>)`
helper from `corpus_tools.py`. This module re-exports that
helper + the special `gaeilge_gramadach_review` tool
(gaeilge subject's 6th tool — the grammardóir reviewer).

Per the centralized-registry contract: no hardcoded model
strings anywhere; per-resolution via MODEL_REGISTRY.
"""
from __future__ import annotations

# The single canonical helper — `bind_subject_tools(<subject>)`
# returns the 5 async callables (syllabus / past_paper /
# marking_scheme / formative_item / response_score).
from .corpus_tools import bind_subject_tools  # type: ignore

# The gaeilge grammardóir reviewer — the 6th tool for the
# gaeilge subject. Lifted to module level so the gaeilge
# subject agent can register it as an additional tool.
try:
    from .gaeilge_gramadach_review import review_gael_gramadach  # type: ignore

    _GRAMADACH_AVAILABLE = True
except ImportError:
    review_gael_gramadach = None  # type: ignore
    _GRAMADACH_AVAILABLE = False


__all__ = [
    "bind_subject_tools",
    "review_gael_gramadach",
]
