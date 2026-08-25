"""Tests for the ADK routing keyword dispatch + subject wiring lookup.

Covers the contract:
1. `ROUTING_KEYWORDS` has 8 buckets (math / appm / chem / geog
   / hist / engl / gael / comp).
2. `route_message(text)` returns the matching module_slug.
3. `route_message(text)` returns `unknown` when no keyword
   matches.
4. `route_message(text)` is case-insensitive.
5. `route_message_to_wire(text)` returns the matching
   `SubjectAgentWiring` from `SUBJECT_WIRING_REGISTRY`.
6. `route_message_to_wire(text)` returns None for unknown
   messages.
7. Empty / None / non-string messages return `unknown`.
"""
from __future__ import annotations

import pytest

from tuatha import routing


# ── ROUTING_KEYWORDS map tests ───────────────────────────────────────


def test_routing_keywords_has_eight_buckets() -> None:
    """The keyword map has exactly 8 buckets (the 8 NCCA subjects)."""
    expected = {
        "math",
        "appm",
        "chem",
        "geog",
        "hist",
        "engl",
        "gael",
        "comp",
    }
    assert set(routing.ROUTING_KEYWORDS.keys()) == expected
    assert len(routing.ROUTING_KEYWORDS) == 8


def test_routing_keywords_each_bucket_has_keywords() -> None:
    """Each bucket has at least one keyword."""
    for slug, keywords in routing.ROUTING_KEYWORDS.items():
        assert isinstance(keywords, list), (
            f"bucket {slug!r} should be a list, got {type(keywords).__name__}"
        )
        assert len(keywords) >= 1, f"bucket {slug!r} is empty"
        for kw in keywords:
            assert isinstance(kw, str)
            assert kw.strip(), f"bucket {slug!r} has empty keyword"


def test_routing_keywords_no_empty_bucket() -> None:
    """No bucket has only whitespace keywords."""
    for slug, keywords in routing.ROUTING_KEYWORDS.items():
        for kw in keywords:
            assert kw.strip(), f"bucket {slug!r} has whitespace-only keyword {kw!r}"


# ── route_message() tests ────────────────────────────────────────────


@pytest.mark.parametrize(
    "message, expected_slug",
    [
        # Mathematics
        ("Can you help with complex numbers in HL Maths?", "math"),
        ("Algebra basics", "math"),
        ("Trigonometry problems", "math"),
        ("LC Maths 2024", "math"),
        # Applied Mathematics
        ("Mechanics in Applied Mathematics", "appm"),
        ("differential equations", "appm"),
        # Chemistry
        ("Atomic structure", "chem"),
        ("Organic chemistry", "chem"),
        # Geography
        ("Physical geography of Ireland", "geog"),
        ("European geography", "geog"),
        # History
        ("Early modern Irish history", "hist"),
        ("Modern Irish history", "hist"),
        # English
        ("Composition techniques", "engl"),
        ("Studied poets", "engl"),
        # Gaeilge
        ("An bhfuil gramadach ag teastáil uait?", "gael"),
        ("Litriú na Gaeilge", "gael"),
        ("Claddagh district", "gael"),
        ("Ogham script", "gael"),
        # Computer Science
        ("Algorithms and data structures", "comp"),
        ("Programming in Python", "comp"),
        ("Networks", "comp"),
    ],
)
def test_route_message_dispatches_correctly(
    message: str, expected_slug: str
) -> None:
    """`route_message(text)` returns the correct module_slug for each
    canonical message.
    """
    assert routing.route_message(message) == expected_slug


def test_route_message_is_case_insensitive() -> None:
    """The dispatch is case-insensitive."""
    assert routing.route_message("LC MATHS") == "math"
    assert routing.route_message("CEIMIC") == "chem"
    assert routing.route_message("ALGORITHMS") == "comp"


def test_route_message_gaelic_irish_keywords() -> None:
    """Gaeilge keywords include both English and Irish anchors."""
    # English anchor
    assert routing.route_message("Can you help with Irish?") == "gael"
    # Irish anchor (with fada)
    assert routing.route_message("Cabhair le Gaeilge") == "gael"


def test_route_message_returns_unknown_for_no_match() -> None:
    """An unrelated message returns `unknown`."""
    assert routing.route_message("Just chatting about life") == "unknown"
    assert routing.route_message("Tell me a story") == "unknown"


def test_route_message_returns_unknown_for_empty_input() -> None:
    """Empty / whitespace / None / non-string inputs return `unknown`."""
    assert routing.route_message("") == "unknown"
    assert routing.route_message("   ") == "unknown"
    assert routing.route_message(None) == "unknown"
    assert routing.route_message(42) == "unknown"  # type: ignore[arg-type]


def test_unknown_subject_constant() -> None:
    """`UNKNOWN_SUBJECT` is the string `'unknown'`."""
    assert routing.UNKNOWN_SUBJECT == "unknown"


# ── route_message_to_wire() tests ────────────────────────────────────


def test_route_message_to_wire_mathematics() -> None:
    """`route_message_to_wire('LC Maths')` returns the Mathematics wire."""
    wire = routing.route_message_to_wire("LC Maths")
    assert wire is not None
    assert wire.ncca_subject == "mathematics"
    assert wire.module_slug == "math"


def test_route_message_to_wire_gaeilge() -> None:
    """Gaeilge keywords resolve to the Gaeilge wire."""
    wire = routing.route_message_to_wire("An bhfuil Gaeilge agat?")
    assert wire is not None
    assert wire.ncca_subject == "gaeilge"
    assert wire.module_slug == "gael"


def test_route_message_to_wire_all_eight_subjects() -> None:
    """Every bucket resolves to the matching `SubjectAgentWiring`."""
    messages = {
        "math": "complex numbers",
        "appm": "applied mathematics mechanics",
        "chem": "atomic structure",
        "geog": "physical geography",
        "hist": "early modern history",
        "engl": "composition basics",
        "gael": "gaeilge grammar",
        "comp": "algorithms",
    }
    for expected_slug, message in messages.items():
        wire = routing.route_message_to_wire(message)
        assert wire is not None, f"no wire for {message!r}"
        assert wire.module_slug == expected_slug, (
            f"expected module_slug={expected_slug!r}, got {wire.module_slug!r}"
        )


def test_route_message_to_wire_unknown_returns_none() -> None:
    """An unknown message returns None."""
    assert routing.route_message_to_wire("just chatting") is None
    assert routing.route_message_to_wire("") is None
    assert routing.route_message_to_wire(None) is None  # type: ignore[arg-type]


# ── Wire dataclass invariants ────────────────────────────────────────


def test_subject_wiring_registry_has_eight_entries() -> None:
    """The subject wiring registry has 8 entries (the 8 NCCA subjects)."""
    assert len(routing.SUBJECT_WIRING_REGISTRY) == 8


def test_subject_wiring_all_module_slugs_match_routing_keywords() -> None:
    """The 8 module_slugs in the wiring registry match the
    8 routing buckets.
    """
    wiring_slugs = {
        wire.module_slug for wire in routing.SUBJECT_WIRING_REGISTRY.values()
    }
    routing_slugs = set(routing.ROUTING_KEYWORDS.keys())
    assert wiring_slugs == routing_slugs


def test_each_wire_has_langfuse_trace_name() -> None:
    """Every wire carries the canonical `agent.<subject>.<verb>` trace name."""
    for wire in routing.SUBJECT_WIRING_REGISTRY.values():
        assert wire.langfuse_trace_name.startswith("agent.")
        assert wire.langfuse_trace_name.endswith(".<verb>")
        assert wire.ncca_subject in wire.langfuse_trace_name


def test_each_wire_has_cognee_dataset() -> None:
    """Every wire carries an `oideachais_lc_<subject>` Cognee dataset name."""
    for wire in routing.SUBJECT_WIRING_REGISTRY.values():
        assert wire.cognee_dataset.startswith("oideachais_")
        assert wire.cognee_dataset.endswith(wire.ncca_subject)


def test_each_wire_has_letta_agent_id() -> None:
    """Every wire carries a `kcg-<subject>-agent` Letta agent ID."""
    for wire in routing.SUBJECT_WIRING_REGISTRY.values():
        assert wire.letta_agent_id.startswith("kcg-")
        assert wire.letta_agent_id.endswith("-agent")
