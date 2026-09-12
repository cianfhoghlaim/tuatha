"""tuatha.subjects.english — the English ADK agent.

One of 8 NCCA subject agents. BAML prefix: Engl.
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
    ncca_subject="english",
    module_slug="engl",
    display_name="English",
    baml_prefix="Engl",
    langfuse_trace_name="agent.english.<verb>",
    cognee_dataset="oideachais_lc_english",
    letta_agent_id="cianfhoghlaim-english-agent",
)

config = TuathaConfig.from_env()

# The 5 per-subject tools, bound via bind_subject_tools.
_bound_tools = bind_subject_tools("english")
engl_syllabus_lookup_tool = FunctionTool(func=_bound_tools[0])
engl_past_paper_lookup_tool = FunctionTool(func=_bound_tools[1])
engl_marking_scheme_lookup_tool = FunctionTool(func=_bound_tools[2])
engl_formative_item_generate_tool = FunctionTool(func=_bound_tools[3])
engl_response_score_tool = FunctionTool(func=_bound_tools[4])


# Per-tool extraction wrappers emit the canonical
# `agent.english.extract` Langfuse trace. The wrappers
# delegate to the underlying tool function unchanged via
# *args/**kwargs so they never break the existing function
# signatures. The decorator is the only addition.





engl_agent = LlmAgent(
    name="engl_agent",
    model=config.litellm.resolve_model("text_llm", "subject_agent"),
    description=(
        "English specialist agent for the NCCA Leaving "
        "Certificate and Junior Cycle curriculum. Comprehension, "
        "composition, language awareness, literary analysis."
    ),
    instruction=(
        "You are the English specialist agent for the new "
        "tuatha/ project. Route keyword-level traffic to your 5 "
        "per-subject tools and emit typed BAML responses per the "
        "`qpack_english.baml` contract.\n\n"
        "THE 5 TOOLS — WHEN TO USE EACH:\n"
        "- syllabus_lookup: typed SyllabusChunk rows with provenance\n"
        "- past_paper_lookup: typed ExamPaperChunk rows\n"
        "- marking_scheme_lookup: typed MarkingCriterion rows\n"
        "- formative_item_generate: grounding evidence\n"
        "- response_score: marking-scheme evidence\n\n"
        "EVIDENCE LADDER (G7): no response without provenance "
        "(source_pdf + source_page + verbatim_text). If a tool "
        "returns zero rows, say 'No coverage for english on that "
        "query' — never invent content.\n\n"
        "NCCA LO NUMBERING: LC-ENGL-LO-<strand>.<index> / "
        "JC-ENGL-LO-<strand>.<index>.\n\n"
        "DIFFICULTY CALIBRATION: 1 = recall; 2 = 1-step; 3 = 2-3 "
        "step; 4 = multi-step synthesis; 5 = evaluation/proof.\n\n"
        "LANGUAGE: English only."
    ),
    tools=[
        engl_syllabus_lookup_tool,
        engl_past_paper_lookup_tool,
        engl_marking_scheme_lookup_tool,
        engl_formative_item_generate_tool,
        engl_response_score_tool,
    ],
    output_key="english_response",
)


__all__ = ["_wire", "config", "engl_agent"]
