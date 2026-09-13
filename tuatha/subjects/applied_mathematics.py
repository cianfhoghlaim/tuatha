"""tuatha.subjects.applied_mathematics — the Applied Mathematics ADK agent.

One of 8 NCCA subject agents. Mirrors the Mathematics agent
pattern. BAML prefix: AppM.
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
    ncca_subject="applied_mathematics",
    module_slug="appm",
    display_name="Applied Mathematics",
    baml_prefix="AppM",
    langfuse_trace_name="agent.applied_mathematics.<verb>",
    cognee_dataset="oideachais_lc_applied_mathematics",
    letta_agent_id="cianfhoghlaim-applied-mathematics-agent",
)

config = TuathaConfig.from_env()

# The 5 per-subject tools, bound via bind_subject_tools. The
# underlying functions are wrapped below with ``@trace_agent``
# so every BAML call site emits the canonical
# ``agent.applied_mathematics.extract`` Langfuse trace.
_bound_tools = bind_subject_tools("applied_mathematics")


# Per-tool extraction wrappers emit the canonical
# `agent.applied_mathematics.extract` Langfuse trace. The wrappers
# delegate to the underlying tool function unchanged via
# *args/**kwargs so they never break the existing function
# signatures. The decorator is the only addition.


@trace_agent("applied_mathematics")
async def _appm_syllabus_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for applied_mathematics syllabus lookup."""
    return await _bound_tools[0](*args, **kwargs)


@trace_agent("applied_mathematics")
async def _appm_past_paper_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for applied_mathematics past-paper lookup."""
    return await _bound_tools[1](*args, **kwargs)


@trace_agent("applied_mathematics")
async def _appm_marking_scheme_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for applied_mathematics marking-scheme lookup."""
    return await _bound_tools[2](*args, **kwargs)


@trace_agent("applied_mathematics")
async def _appm_formative_item_generate(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for applied_mathematics formative item generation."""
    return await _bound_tools[3](*args, **kwargs)


@trace_agent("applied_mathematics")
async def _appm_response_score(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for applied_mathematics response scoring."""
    return await _bound_tools[4](*args, **kwargs)


appm_syllabus_lookup_tool = FunctionTool(func=_appm_syllabus_lookup)
appm_past_paper_lookup_tool = FunctionTool(func=_appm_past_paper_lookup)
appm_marking_scheme_lookup_tool = FunctionTool(func=_appm_marking_scheme_lookup)
appm_formative_item_generate_tool = FunctionTool(func=_appm_formative_item_generate)
appm_response_score_tool = FunctionTool(func=_appm_response_score)





appm_agent = LlmAgent(
    name="appm_agent",
    model=config.litellm.resolve_model("text_llm", "subject_agent"),
    description=(
        "Applied Mathematics specialist agent for the NCCA "
        "Leaving Certificate and Junior Cycle curriculum. "
        "Mechanics, sequences + series, coordinate geometry, "
        "differential equations."
    ),
    instruction=(
        "You are the Applied Mathematics specialist agent for the "
        "new tuatha/ project. You handle queries about the NCCA "
        "Leaving Certificate + Junior Cycle Applied Mathematics "
        "syllabus. Route keyword-level traffic to your 5 "
        "per-subject tools and emit typed BAML responses per the "
        "`qpack_applied_mathematics.baml` contract.\n\n"
        "THE 5 TOOLS — WHEN TO USE EACH:\n"
        "- syllabus_lookup: 'what does the syllabus say about X' → "
        "typed SyllabusChunk rows with provenance (source_pdf + "
        "source_page + verbatim_text)\n"
        "- past_paper_lookup: 'show me past paper questions on X' → "
        "typed ExamPaperChunk rows\n"
        "- marking_scheme_lookup: 'how is X graded' → typed "
        "MarkingCriterion rows\n"
        "- formative_item_generate: 'give me a practice question on "
        "X' → grounding evidence\n"
        "- response_score: 'grade my answer' → marking-scheme evidence\n\n"
        "EVIDENCE LADDER (G7 CONTRACT): no response without "
        "provenance (source_pdf + source_page + verbatim_text). "
        "If a tool returns zero rows, say 'No coverage for applied "
        "mathematics on that query' — never invent content.\n\n"
        "NCCA LO NUMBERING: LC-APPM-LO-<strand>.<index> / "
        "JC-APPM-LO-<strand>.<index>. When a query references a "
        "topic but not an LO code, first call syllabus_lookup to "
        "identify the relevant LO code.\n\n"
        "DIFFICULTY CALIBRATION: 1 = recall; 2 = 1-step; 3 = 2-3 "
        "step; 4 = multi-step synthesis; 5 = evaluation/proof.\n\n"
        "LANGUAGE: English only."
    ),
    tools=[
        appm_syllabus_lookup_tool,
        appm_past_paper_lookup_tool,
        appm_marking_scheme_lookup_tool,
        appm_formative_item_generate_tool,
        appm_response_score_tool,
    ],
    output_key="applied_mathematics_response",
)


__all__ = ["_wire", "appm_agent", "config"]
