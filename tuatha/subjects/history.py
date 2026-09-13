"""tuatha.subjects.history — the History ADK agent.

One of 8 NCCA subject agents. BAML prefix: Hist.
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
    ncca_subject="history",
    module_slug="hist",
    display_name="History",
    baml_prefix="Hist",
    langfuse_trace_name="agent.history.<verb>",
    cognee_dataset="oideachais_lc_history",
    letta_agent_id="cianfhoghlaim-history-agent",
)

config = TuathaConfig.from_env()

# The 5 per-subject tools, bound via bind_subject_tools. The
# underlying functions are wrapped below with ``@trace_agent``
# so every BAML call site emits the canonical
# ``agent.history.extract`` Langfuse trace.
_bound_tools = bind_subject_tools("history")


# Per-tool extraction wrappers emit the canonical
# `agent.history.extract` Langfuse trace. The wrappers
# delegate to the underlying tool function unchanged via
# *args/**kwargs so they never break the existing function
# signatures. The decorator is the only addition.


@trace_agent("history")
async def _hist_syllabus_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for history syllabus lookup."""
    return await _bound_tools[0](*args, **kwargs)


@trace_agent("history")
async def _hist_past_paper_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for history past-paper lookup."""
    return await _bound_tools[1](*args, **kwargs)


@trace_agent("history")
async def _hist_marking_scheme_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for history marking-scheme lookup."""
    return await _bound_tools[2](*args, **kwargs)


@trace_agent("history")
async def _hist_formative_item_generate(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for history formative item generation."""
    return await _bound_tools[3](*args, **kwargs)


@trace_agent("history")
async def _hist_response_score(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for history response scoring."""
    return await _bound_tools[4](*args, **kwargs)


hist_syllabus_lookup_tool = FunctionTool(func=_hist_syllabus_lookup)
hist_past_paper_lookup_tool = FunctionTool(func=_hist_past_paper_lookup)
hist_marking_scheme_lookup_tool = FunctionTool(func=_hist_marking_scheme_lookup)
hist_formative_item_generate_tool = FunctionTool(func=_hist_formative_item_generate)
hist_response_score_tool = FunctionTool(func=_hist_response_score)





hist_agent = LlmAgent(
    name="hist_agent",
    model=config.litellm.resolve_model("text_llm", "subject_agent"),
    description=(
        "History specialist agent for the NCCA Leaving "
        "Certificate and Junior Cycle curriculum. Early modern, "
        "modern Irish, European, world history."
    ),
    instruction=(
        "You are the History specialist agent for the new "
        "tuatha/ project. Route keyword-level traffic to your 5 "
        "per-subject tools and emit typed BAML responses per the "
        "`qpack_history.baml` contract.\n\n"
        "THE 5 TOOLS — WHEN TO USE EACH:\n"
        "- syllabus_lookup: typed SyllabusChunk rows with provenance\n"
        "- past_paper_lookup: typed ExamPaperChunk rows\n"
        "- marking_scheme_lookup: typed MarkingCriterion rows\n"
        "- formative_item_generate: grounding evidence\n"
        "- response_score: marking-scheme evidence\n\n"
        "EVIDENCE LADDER (G7): no response without provenance "
        "(source_pdf + source_page + verbatim_text). If a tool "
        "returns zero rows, say 'No coverage for history on that "
        "query' — never invent content.\n\n"
        "NCCA LO NUMBERING: LC-HIST-LO-<strand>.<index> / "
        "JC-HIST-LO-<strand>.<index>.\n\n"
        "DIFFICULTY CALIBRATION: 1 = recall; 2 = 1-step; 3 = 2-3 "
        "step; 4 = multi-step synthesis; 5 = evaluation/proof.\n\n"
        "LANGUAGE: English only."
    ),
    tools=[
        hist_syllabus_lookup_tool,
        hist_past_paper_lookup_tool,
        hist_marking_scheme_lookup_tool,
        hist_formative_item_generate_tool,
        hist_response_score_tool,
    ],
    output_key="history_response",
)


__all__ = ["_wire", "config", "hist_agent"]
