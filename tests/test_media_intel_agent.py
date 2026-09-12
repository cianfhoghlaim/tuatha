"""The 10-tool media_descriptor_agent tests."""
import pytest

from tuatha.agents.media_intel import (
    TOOLS, TOOL_NAMES, media_descriptor_agent,
    classify_medium, per_medium_coverage, cross_medium_consistency, summarise_corpus,
)


def test_10_tools_present():
    # Per the 2026-08-27 change: 11 tools now (10 original +
    # extract_xmen_descriptor Class F). The test name stays "10"
    # for backwards-compat — the canonical count is 11.
    assert len(TOOLS) == 11


def test_5_extractor_tools():
    # Per the 2026-08-27 change: 6 extractors now (5 original +
    # extract_xmen_descriptor Class F). The test name stays "5"
    # for backwards-compat — the canonical count is 6.
    extractors = [n for n in TOOL_NAMES if n.startswith("extract_")]
    assert len(extractors) == 6


def test_5_corpus_tools():
    corpus = [n for n in TOOL_NAMES if not n.startswith("extract_")]
    assert len(corpus) == 5
