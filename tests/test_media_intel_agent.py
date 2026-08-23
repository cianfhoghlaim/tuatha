"""The 10-tool media_descriptor_agent tests."""
import pytest

from tuatha.agents.media_intel import (
    TOOLS, TOOL_NAMES, media_descriptor_agent,
    classify_medium, per_medium_coverage, cross_medium_consistency, summarise_corpus,
)


def test_10_tools_present():
    assert len(TOOLS) == 10


def test_5_extractor_tools():
    extractors = [n for n in TOOL_NAMES if n.startswith("extract_")]
    assert len(extractors) == 5


def test_5_corpus_tools():
    corpus = [n for n in TOOL_NAMES if not n.startswith("extract_")]
    assert len(corpus) == 5
