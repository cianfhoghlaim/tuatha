"""tuatha.education.agents.agent — the Phase 5 agent surface.

A 5-agent dispatcher that routes learner questions to the
Phase 1 + Phase 2 + Phase 3 sources:

  - Q on a single LO  -> the subject_agent (per-subject ADK)
  - Q on cross-subject -> the cross_subject_agent
  - Q on lore        -> the mythology_narrator_agent
  - Q on history     -> the academic_history_agent
  - Q on Celtic grammar -> the celtic_grammar_agent

The 5-agent fan-out is per the build plan's "9-agent ADK fleet"
extended with the Phase 1-3 surfaces.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class AgentKind(str, Enum):
    SUBJECT = "subject_agent"           # 8 NCCA subjects
    CROSS_SUBJECT = "cross_subject_agent"
    MYTHOLOGY = "mythology_narrator_agent"
    ACADEMIC_HISTORY = "academic_history_agent"
    CELTIC_GRAMMAR = "celtic_grammar_agent"


@dataclass
class Phase5AgentQuery:
    """The canonical learner query."""
    student_id: str
    prompt: str
    subject_hint: Optional[str] = None
    language: str = "en"
    cite_required: bool = True


@dataclass
class Phase5AgentResponse:
    """The canonical agent response (carries Phase 3 rung-5 root)."""
    agent: AgentKind
    subject: str
    reply_en: str
    reply_ga: str
    rung1_sha256: str = ""
    rung5_root: str = ""
    confidence: float = 1.0


def dispatch_agent(query: Phase5AgentQuery) -> AgentKind:
    """Pick which of the 5 agents handles the query.

    Routing rules (per the build plan):
    - the prompt mentions a Learning Outcome code (LC-MATHS-LO-2.4) -> subject_agent
    - the prompt mentions multiple subjects / cross-jurisdiction -> cross_subject_agent
    - the prompt asks about Tuatha Dé Danann / Déisigh / Uí Liatháin / Celtic lore -> mythology_narrator_agent
    - the prompt asks about historical events / NCCA / 1916 / 1922 -> academic_history_agent
    - the prompt asks about grammar / verb conjugation / noun declension -> celtic_grammar_agent
    - default: subject_agent (with subject_hint if provided)
    """
    p = query.prompt.lower()
    if any(k in p for k in ("lc-", "sc-", "junior-cycle", "syllabus", "marking scheme",
                           "exam", "question", "lo-")):
        return AgentKind.SUBJECT
    if any(k in p for k in ("compar", "cross-subject", "across", "between",
                           "equivalen")):
        return AgentKind.CROSS_SUBJECT
    if any(k in p for k in ("tuatha dé danann", "dé danann", "uí liatháin",
                           "déisigh", "celtic lore", "mabinogi", "gwydion",
                           "fomorian", "fomorians", "danu", "lugh")):
        return AgentKind.MYTHOLOGY
    if any(k in p for k in ("1916", "1922", "rising", "war of independence",
                           "ncca", "history of", "act of union")):
        return AgentKind.ACADEMIC_HISTORY
    if any(k in p for k in ("grammar", "conjugat", "declen", "verbal noun",
                           "eclips", "lenition", "mutation")):
        return AgentKind.CELTIC_GRAMMAR
    return AgentKind.SUBJECT


async def query_agent(query: Phase5AgentQuery) -> Phase5AgentResponse:
    """Dispatch + execute (stub: returns a placeholder response)."""
    agent = dispatch_agent(query)
    return Phase5AgentResponse(
        agent=agent,
        subject=query.subject_hint or "unknown",
        reply_en=f"(stub: {agent.value} response)",
        reply_ga=f"(stub: freagra {agent.value})",
        rung5_root="0".repeat(64),
        confidence=0.5,
    )
