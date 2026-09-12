"""tuatha.subjects.geography — the Geography ADK agent.

One of 8 NCCA subject agents. BAML prefix: Geog.
"""
from __future__ import annotations

from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..observability import trace_agent
from ..routing import build_wire
from ..tools.corpus_tools import bind_subject_tools

_wire = build_wire(
    ncca_subject="geography",
    module_slug="geog",
    display_name="Geography",
    baml_prefix="Geog",
    langfuse_trace_name="agent.geography.<verb>",
    cognee_dataset="oideachais_lc_geography",
    letta_agent_id="cianfhoghlaim-geography-agent",
)

config = TuathaConfig.from_env()

# The 5 per-subject tools, bound via bind_subject_tools.
_bound_tools = bind_subject_tools("geography")
geog_syllabus_lookup_tool = FunctionTool(func=_bound_tools[0])
geog_past_paper_lookup_tool = FunctionTool(func=_bound_tools[1])
geog_marking_scheme_lookup_tool = FunctionTool(func=_bound_tools[2])
geog_formative_item_generate_tool = FunctionTool(func=_bound_tools[3])
geog_response_score_tool = FunctionTool(func=_bound_tools[4])


# Per-tool extraction wrappers emit the canonical
# `agent.geography.extract` Langfuse trace. The wrappers
# delegate to the underlying tool function unchanged via
# *args/**kwargs so they never break the existing function
# signatures. The decorator is the only addition.





geog_agent = LlmAgent(
    name="geog_agent",
    model=config.litellm.resolve_model("text_llm", "subject_agent"),
    description=(
        "Geography specialist agent for the NCCA Leaving "
        "Certificate and Junior Cycle curriculum. Physical "
        "geography, regional geography, human-environment "
        "interaction, geographic investigation."
    ),
    instruction=(
        "You are the Geography specialist agent for the new "
        "tuatha/ project. Route keyword-level traffic to your 5 "
        "per-subject tools and emit typed BAML responses per the "
        "`qpack_geography.baml` contract.\n\n"
        "THE 5 TOOLS — WHEN TO USE EACH:\n"
        "- syllabus_lookup: typed SyllabusChunk rows with provenance\n"
        "- past_paper_lookup: typed ExamPaperChunk rows\n"
        "- marking_scheme_lookup: typed MarkingCriterion rows\n"
        "- formative_item_generate: grounding evidence\n"
        "- response_score: marking-scheme evidence\n\n"
        "EVIDENCE LADDER (G7): no response without provenance. If "
        "a tool returns zero rows, say 'No coverage for geography on "
        "that query' — never invent content.\n\n"
        "NCCA LO NUMBERING: LC-GEOG-LO-<strand>.<index> / "
        "JC-GEOG-LO-<strand>.<index>.\n\n"
        "DIFFICULTY CALIBRATION: 1 = recall; 2 = 1-step; 3 = 2-3 "
        "step; 4 = multi-step synthesis; 5 = evaluation/proof.\n\n"
        "LANGUAGE: English only."
    ),
    tools=[
        geog_syllabus_lookup_tool,
        geog_past_paper_lookup_tool,
        geog_marking_scheme_lookup_tool,
        geog_formative_item_generate_tool,
        geog_response_score_tool,
    ],
    output_key="geography_response",
)


__all__ = ["_wire", "config", "geog_agent"]
