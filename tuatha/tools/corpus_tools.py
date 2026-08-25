"""tuatha.tools.corpus_tools — the subject-agnostic corpus tools.

These five tools replace the 40 per-subject tool modules
(``<subject>_syllabus_lookup.py`` and friends). Those were eight
near-identical copies of five functions, each returning a hardcoded
dict — they never touched a corpus. Since the subject is already a
parameter, one implementation covers all eight.

Every tool returns rows carrying their provenance. The G7 gate says
nothing renders unless it can name its source, so a caller that drops
``provenance`` from a result breaks traceability without breaking
anything visible until someone clicks through.
"""

from __future__ import annotations

from typing import Any

from ..corpus import DocKind, SubjectChunk, corpus
from ..corpus.client import CorpusUnavailableError

__all__ = [
    "bind_subject_tools",
    "formative_item_generate",
    "marking_scheme_lookup",
    "past_paper_lookup",
    "response_score",
    "syllabus_lookup",
]


def _render(chunks: list[SubjectChunk]) -> list[dict[str, Any]]:
    """Render chunks for an agent, provenance attached."""
    return [
        {"text": c.text, "doc_kind": c.doc_kind, "provenance": c.provenance()}
        for c in chunks
    ]


def _lookup(
    subject: str,
    query: str,
    doc_kind: str | None,
    level: str,
    language: str,
    limit: int,
) -> dict[str, Any]:
    """Shared body for the three lookup tools."""
    try:
        client = corpus()
        chunks = (
            client.search_text(
                subject,
                query,
                level=level,
                language=language,
                doc_kind=doc_kind,
                limit=limit,
            )
            if query
            else client.chunks(
                subject,
                level=level,
                language=language,
                doc_kind=doc_kind,
                limit=limit,
            )
        )
    except (CorpusUnavailableError, ValueError) as exc:
        # Surfaced rather than swallowed: an agent that receives an
        # empty result set cannot tell "no coverage" from "no match".
        return {
            "subject": subject,
            "doc_kind": doc_kind,
            "error": str(exc),
            "results": [],
        }

    return {
        "subject": subject,
        "doc_kind": doc_kind,
        "level": level,
        "language": language,
        "query": query,
        "count": len(chunks),
        "results": _render(chunks),
    }


async def syllabus_lookup(
    subject: str,
    query: str = "",
    level: str = "hl",
    language: str = "en",
    limit: int = 10,
) -> dict[str, Any]:
    """Look up syllabus content for a subject.

    Args:
        subject: an NCCA subject slug with corpus coverage.
        query: free text; empty returns the head of the syllabus.
        level: ``hl`` / ``ol`` / ``fl``.
        language: ``en`` or ``ga``. The corpus embedder is multilingual,
            so a Gaeilge query can retrieve English content.
        limit: maximum rows.
    """
    return _lookup(subject, query, DocKind.SYLLABUS, level, language, limit)


async def past_paper_lookup(
    subject: str,
    query: str = "",
    level: str = "hl",
    language: str = "en",
    limit: int = 10,
) -> dict[str, Any]:
    """Look up past exam paper content for a subject."""
    return _lookup(subject, query, DocKind.PAST_PAPER, level, language, limit)


async def marking_scheme_lookup(
    subject: str,
    query: str = "",
    level: str = "hl",
    language: str = "en",
    limit: int = 10,
) -> dict[str, Any]:
    """Look up marking scheme content for a subject."""
    return _lookup(subject, query, DocKind.MARKING_SCHEME, level, language, limit)


async def formative_item_generate(
    subject: str,
    topic: str,
    level: str = "hl",
    language: str = "en",
    difficulty: int = 3,
) -> dict[str, Any]:
    """Gather the grounding a formative item must be generated from.

    This deliberately does not generate the item. It returns the
    syllabus and past-paper evidence a generator needs, so that whatever
    produces the question can cite it. Generating an item from a model's
    own recall would produce a chamber that cannot name its source,
    which the G7 gate exists to reject.
    """
    syllabus = _lookup(subject, topic, DocKind.SYLLABUS, level, language, 5)
    papers = _lookup(subject, topic, DocKind.PAST_PAPER, level, language, 5)

    grounding = syllabus["results"] + papers["results"]
    return {
        "subject": subject,
        "topic": topic,
        "level": level,
        "language": language,
        "difficulty": difficulty,
        "grounding": grounding,
        "groundable": bool(grounding),
        "errors": [e for e in (syllabus.get("error"), papers.get("error")) if e],
    }


async def response_score(
    subject: str,
    question: str,
    student_response: str,
    level: str = "hl",
    language: str = "en",
) -> dict[str, Any]:
    """Gather the marking-scheme evidence needed to score a response.

    As with :func:`formative_item_generate`, this returns grounding
    rather than a grade. A score that cannot point at the marking-scheme
    band it came from is not a score the Evidence Ladder will publish.
    """
    scheme = _lookup(subject, question, DocKind.MARKING_SCHEME, level, language, 5)
    return {
        "subject": subject,
        "question": question,
        "student_response": student_response,
        "level": level,
        "language": language,
        "marking_scheme": scheme["results"],
        "scorable": bool(scheme["results"]),
        "errors": [e for e in (scheme.get("error"),) if e],
    }


def bind_subject_tools(subject: str) -> list[Any]:
    """Return the five corpus tools bound to one subject.

    A subject agent must not be able to query a different subject's
    corpus, so ``subject`` is closed over rather than left as a
    parameter the model fills in. The returned callables carry their own
    ``__name__`` and ``__doc__`` because ADK derives each tool's schema
    and description from them.

    Args:
        subject: the NCCA subject slug this agent speaks for.

    Returns:
        Five async callables, in the order syllabus / past_paper /
        marking_scheme / formative_item / response_score.
    """

    async def syllabus(query: str = "", level: str = "hl", language: str = "en") -> dict[str, Any]:
        return await syllabus_lookup(subject, query, level, language)

    async def past_paper(
        query: str = "", level: str = "hl", language: str = "en"
    ) -> dict[str, Any]:
        return await past_paper_lookup(subject, query, level, language)

    async def marking_scheme(
        query: str = "", level: str = "hl", language: str = "en"
    ) -> dict[str, Any]:
        return await marking_scheme_lookup(subject, query, level, language)

    async def formative_item(
        topic: str, level: str = "hl", language: str = "en", difficulty: int = 3
    ) -> dict[str, Any]:
        return await formative_item_generate(subject, topic, level, language, difficulty)

    async def score(
        question: str, student_response: str, level: str = "hl", language: str = "en"
    ) -> dict[str, Any]:
        return await response_score(subject, question, student_response, level, language)

    bound = [syllabus, past_paper, marking_scheme, formative_item, score]
    docs = [
        f"Look up {subject} syllabus content. Returns chunks with provenance.",
        f"Look up {subject} past exam paper content. Returns chunks with provenance.",
        f"Look up {subject} marking scheme content. Returns chunks with provenance.",
        (
            f"Gather syllabus and past-paper grounding for a {subject} formative "
            "item on a topic. Returns evidence to generate from, not the item."
        ),
        (
            f"Gather the {subject} marking-scheme evidence needed to score a "
            "student response. Returns evidence to score against, not a grade."
        ),
    ]
    for fn, name, doc in zip(
        bound,
        (
            f"{subject}_syllabus_lookup",
            f"{subject}_past_paper_lookup",
            f"{subject}_marking_scheme_lookup",
            f"{subject}_formative_item_generate",
            f"{subject}_response_score",
        ),
        docs,
        strict=True,
    ):
        fn.__name__ = name
        fn.__qualname__ = name
        fn.__doc__ = doc
    return bound
