"""tuatha.routing — the canonical SubjectAgentWiring factory.

Per the academic_history_agent.py pattern (the canonical 8-field
SubjectAgentWiring dataclass), the new tuatha/ project
adopts the same shape. The factory is the canonical mount
point for every per-subject agent + per-educational agent +
per-hackathon feature.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SubjectAgentWiring:
    """The per-subject / per-educational / per-hackathon wiring.

    Pattern (verbatim from the parent's
    `agents/agent_registry.py:AGENT_REGISTRY`):
    - 5 positional fields: ncca_subject / module_slug / display_name /
      baml_prefix / langfuse_trace_name / cognee_dataset
    - Plus: letta_agent_id (the Letta memory ID)
    - Plus: litellm_routing_key (the LiteLLM routing key)

    Every agent in the new tuatha/ project carries one of these.
    The factory `build_wire()` produces the canonical instances.
    """

    ncca_subject: str
    module_slug: str
    display_name: str
    baml_prefix: str
    langfuse_trace_name: str
    cognee_dataset: str
    letta_agent_id: str
    litellm_routing_key: str = "minimax"  # the canonical 7-tier fallback


def build_wire(
    ncca_subject: str,
    module_slug: str,
    display_name: str,
    baml_prefix: str,
    langfuse_trace_name: str,
    cognee_dataset: str,
    letta_agent_id: str,
    litellm_routing_key: str = "minimax",
) -> SubjectAgentWiring:
    """Build the canonical SubjectAgentWiring for a subject / educational / hackathon.

    Per the parent's `agents/agent_registry.py:register_ncca_subjects_in_agent_registry()`
    pattern: the factory produces the canonical SubjectAgentWiring
    that the parent repo registers in the AGENT_REGISTRY.
    """
    return SubjectAgentWiring(
        ncca_subject=ncca_subject,
        module_slug=module_slug,
        display_name=display_name,
        baml_prefix=baml_prefix,
        langfuse_trace_name=langfuse_trace_name,
        cognee_dataset=cognee_dataset,
        letta_agent_id=letta_agent_id,
        litellm_routing_key=litellm_routing_key,
    )


# ── The canonical 8-subject wire registry ──────────────────────


SUBJECT_WIRING_REGISTRY: dict[str, SubjectAgentWiring] = {
    "mathematics": build_wire(
        ncca_subject="mathematics",
        module_slug="math",
        display_name="Mathematics",
        baml_prefix="Math",
        langfuse_trace_name="agent.mathematics.<verb>",
        cognee_dataset="oideachais_lc_mathematics",
        letta_agent_id="kcg-mathematics-agent",
    ),
    "applied_mathematics": build_wire(
        ncca_subject="applied_mathematics",
        module_slug="appm",
        display_name="Applied Mathematics",
        baml_prefix="AppM",
        langfuse_trace_name="agent.applied_mathematics.<verb>",
        cognee_dataset="oideachais_lc_applied_mathematics",
        letta_agent_id="kcg-applied-mathematics-agent",
    ),
    "chemistry": build_wire(
        ncca_subject="chemistry",
        module_slug="chem",
        display_name="Chemistry",
        baml_prefix="Chem",
        langfuse_trace_name="agent.chemistry.<verb>",
        cognee_dataset="oideachais_lc_chemistry",
        letta_agent_id="kcg-chemistry-agent",
    ),
    "geography": build_wire(
        ncca_subject="geography",
        module_slug="geog",
        display_name="Geography",
        baml_prefix="Geog",
        langfuse_trace_name="agent.geography.<verb>",
        cognee_dataset="oideachais_lc_geography",
        letta_agent_id="kcg-geography-agent",
    ),
    "history": build_wire(
        ncca_subject="history",
        module_slug="hist",
        display_name="History",
        baml_prefix="Hist",
        langfuse_trace_name="agent.history.<verb>",
        cognee_dataset="oideachais_lc_history",
        letta_agent_id="kcg-history-agent",
    ),
    "english": build_wire(
        ncca_subject="english",
        module_slug="engl",
        display_name="English",
        baml_prefix="Engl",
        langfuse_trace_name="agent.english.<verb>",
        cognee_dataset="oideachais_lc_english",
        letta_agent_id="kcg-english-agent",
    ),
    "gaeilge": build_wire(
        ncca_subject="gaeilge",
        module_slug="gael",
        display_name="Gaeilge",
        baml_prefix="Gael",
        langfuse_trace_name="agent.gaeilge.<verb>",
        cognee_dataset="oideachais_lc_gaeilge",
        letta_agent_id="kcg-gaeilge-agent",
    ),
    "computer_science": build_wire(
        ncca_subject="computer_science",
        module_slug="comp",
        display_name="Computer Science",
        baml_prefix="Comp",
        langfuse_trace_name="agent.computer_science.<verb>",
        cognee_dataset="oideachais_lc_computer_science",
        letta_agent_id="kcg-computer-science-agent",
    ),
}


# ── The canonical 3-educational wire registry ────────────────


EDUCATIONAL_WIRING_REGISTRY: dict[str, SubjectAgentWiring] = {
    "academic_history": build_wire(
        ncca_subject="academic_history",
        module_slug="academic_history",
        display_name="Academic History",
        baml_prefix="AcadHist",
        langfuse_trace_name="agent.academic_history.<verb>",
        cognee_dataset="oideachais_academic_history",
        letta_agent_id="kcg-academic-history-agent",
    ),
    "celtic_grammar": build_wire(
        ncca_subject="celtic_grammar",
        module_slug="celtic_grammar",
        display_name="Celtic Grammar",
        baml_prefix="CeltGram",
        langfuse_trace_name="agent.celtic_grammar.<verb>",
        cognee_dataset="oideachais_celtic_grammar",
        letta_agent_id="kcg-celtic-grammar-agent",
    ),
    "celtic_morphology": build_wire(
        ncca_subject="celtic_morphology",
        module_slug="celtic_morphology",
        display_name="Celtic Morphology",
        baml_prefix="CeltMorph",
        langfuse_trace_name="agent.celtic_morphology.<verb>",
        cognee_dataset="oideachais_celtic_morphology",
        letta_agent_id="kcg-celtic-morphology-agent",
    ),
}


# ── The canonical 4-hackathon wire registry ─────────────────


HACKATHON_WIRING_REGISTRY: dict[str, SubjectAgentWiring] = {
    "marking_grader": build_wire(
        ncca_subject="marking_grader",
        module_slug="marking_grader",
        display_name="Marking Grader",
        baml_prefix="MarkGrade",
        langfuse_trace_name="agent.marking_grader.<verb>",
        cognee_dataset="oideachais_marking_grader",
        letta_agent_id="kcg-marking-grader-agent",
    ),
    "adaptive_tutor": build_wire(
        ncca_subject="adaptive_tutor",
        module_slug="adaptive_tutor",
        display_name="Adaptive Tutor",
        baml_prefix="AdaptTutor",
        langfuse_trace_name="agent.adaptive_tutor.<verb>",
        cognee_dataset="oideachais_adaptive_tutor",
        letta_agent_id="kcg-adaptive-tutor-agent",
    ),
    "equivalency_generator": build_wire(
        ncca_subject="equivalency_generator",
        module_slug="equivalency_generator",
        display_name="Equivalency Generator",
        baml_prefix="EquivGen",
        langfuse_trace_name="agent.equivalency_generator.<verb>",
        cognee_dataset="oideachais_equivalency_generator",
        letta_agent_id="kcg-equivalency-generator-agent",
    ),
    "curriculum_change_sensor": build_wire(
        ncca_subject="curriculum_change_sensor",
        module_slug="curriculum_change_sensor",
        display_name="Curriculum Change Sensor",
        baml_prefix="CurrChgSens",
        langfuse_trace_name="agent.curriculum_change_sensor.<verb>",
        cognee_dataset="oideachais_curriculum_change_sensor",
        letta_agent_id="kcg-curriculum-change-sensor-agent",
    ),
}


__all__ = [
    "EDUCATIONAL_WIRING_REGISTRY",
    "HACKATHON_WIRING_REGISTRY",
    "ROUTING_KEYWORDS",
    "SUBJECT_WIRING_REGISTRY",
    "SubjectAgentWiring",
    "UNKNOWN_SUBJECT",
    "build_wire",
    "route_message",
]


# ── The canonical 8-subject keyword dispatch map ──────────────
# Per the Phase 1 P7 (ADK routing) addition: the root_agent uses
# this map to dispatch a free-form user message to the right
# NCCA subject agent. The keyword set is the canonical 8 buckets:
# math / appm / chem / geog / hist / engl / gael / comp.
#
# Each bucket maps the module_slug (the short slug used in the
# NCCA subject wiring) to a list of keywords that should route to
# it. The keyword list is intentionally a small set of unambiguous
# anchors (subject-specific NCCA codes + Irish/Gaeilge counterparts
# for the gaeilge bucket) so `route_message()` can classify
# cleanly without false positives.
#
# Order matters: `route_message()` checks buckets in the order
# below. Place higher-precision buckets first if you ever add a
# more-specific keyword set.
#
# CRITICAL: the `appm` bucket MUST come before the `math` bucket
# because the keyword "applied mathematics" contains the substring
# "mathematics" — the longer match would otherwise be masked.
ROUTING_KEYWORDS: dict[str, list[str]] = {
    "appm": [
        "applied mathematics",
        "applied maths",
        "matamaitic fheidhmeach",
        "differential equations",
        "coordinate geometry",
        "sequences and series",
    ],
    "math": [
        "mathematics",
        "maths",
        "matamaitic",
        "lc maths",
        "hl maths",
        "ol maths",
        "complex numbers",
        "calculus",
        "algebra",
        "trigonometry",
    ],
    "chem": [
        "chemistry",
        "ceimic",
        "atomic structure",
        "bonding",
        "stoichiometry",
        "organic chemistry",
        "rates of reaction",
    ],
    "geog": [
        "geography",
        "tíreolaíocht",
        "physical geography",
        "regional geography",
        "geographic investigation",
        "european geography",
    ],
    "hist": [
        "history",
        "stair",
        "early modern",
        "modern irish",
        "european history",
        "world history",
        "chronology",
    ],
    "engl": [
        "english",
        "béarla",
        "comprehension",
        "composition",
        "language awareness",
        "literary analysis",
        "studied poets",
    ],
    "gael": [
        "gaeilge",
        "irish",
        "gramadach",
        "litriú",
        "filíocht",
        "prós",
        "agallamh",
        "aistí",
        "samplaí",
        "claddagh",
        "gaeltacht",
        "ogham",
    ],
    "comp": [
        "computer science",
        "computing",
        "ríomhaireacht",
        "algorithms",
        "data structures",
        "computational thinking",
        "programming",
        "databases",
        "networks",
    ],
}


# The fallback slug when no keyword matches. The root_agent
# should route to the cross_subject agent in this case (per the
# cross_subject.py pattern).
UNKNOWN_SUBJECT = "unknown"


def route_message(message: str) -> str:
    """Classify a free-form user message to an NCCA subject module slug.

    The dispatch checks each bucket in `ROUTING_KEYWORDS` and
    returns the first matching module_slug. Returns
    `UNKNOWN_SUBJECT` when no keyword matches.

    Args:
        message: The raw user message (case-insensitive substring
            match against each bucket's keyword list).

    Returns:
        The matching module slug
        (`math` / `appm` / `chem` / `geog` / `hist` / `engl` /
        `gael` / `comp`) or `UNKNOWN_SUBJECT` if no bucket matches.
    """
    # LBYL: guard against non-string or empty inputs without
    # raising — the root_agent can receive empty / None messages
    # during smoke tests.
    if not isinstance(message, str) or not message.strip():
        return UNKNOWN_SUBJECT

    normalised = message.casefold()

    for slug, keywords in ROUTING_KEYWORDS.items():
        for keyword in keywords:
            if keyword.casefold() in normalised:
                return slug

    return UNKNOWN_SUBJECT


def route_message_to_wire(message: str) -> SubjectAgentWiring | None:
    """Classify + look up the canonical SubjectAgentWiring for a message.

    Convenience wrapper around `route_message()` that returns the
    full `SubjectAgentWiring` (so callers can use the
    langfuse_trace_name, cognee_dataset, letta_agent_id fields
    directly). Returns `None` when no keyword matches — callers
    should fall back to the cross_subject agent.

    The `SubjectAgentWiring` instances in `SUBJECT_WIRING_REGISTRY`
    are keyed by their full `ncca_subject` slug (e.g.,
    `"mathematics"`), not by the short `module_slug` returned by
    `route_message()` (e.g., `"math"`). We therefore look up by
    `module_slug` rather than dict key.

    Args:
        message: The raw user message.

    Returns:
        The matching `SubjectAgentWiring`, or `None` if no bucket
        matches.
    """
    slug = route_message(message)
    if slug == UNKNOWN_SUBJECT:
        return None
    for wire in SUBJECT_WIRING_REGISTRY.values():
        if wire.module_slug == slug:
            return wire
    return None
