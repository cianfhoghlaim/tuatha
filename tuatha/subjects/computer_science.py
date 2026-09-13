"""tuatha.subjects.computer_science — the Computer Science ADK agent.

One of 8 NCCA subject agents. BAML prefix: Comp.
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
    ncca_subject="computer_science",
    module_slug="comp",
    display_name="Computer Science",
    baml_prefix="Comp",
    langfuse_trace_name="agent.computer_science.<verb>",
    cognee_dataset="oideachais_lc_computer_science",
    letta_agent_id="cianfhoghlaim-computer-science-agent",
)

config = TuathaConfig.from_env()

# The 5 per-subject tools, bound via bind_subject_tools. The
# underlying functions are wrapped below with ``@trace_agent``
# so every BAML call site emits the canonical
# ``agent.computer_science.extract`` Langfuse trace.
_bound_tools = bind_subject_tools("computer_science")


# Per-tool extraction wrappers emit the canonical
# `agent.computer_science.extract` Langfuse trace. The wrappers
# delegate to the underlying tool function unchanged via
# *args/**kwargs so they never break the existing function
# signatures. The decorator is the only addition.


@trace_agent("computer_science")
async def _comp_syllabus_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for computer_science syllabus lookup."""
    return await _bound_tools[0](*args, **kwargs)


@trace_agent("computer_science")
async def _comp_past_paper_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for computer_science past-paper lookup."""
    return await _bound_tools[1](*args, **kwargs)


@trace_agent("computer_science")
async def _comp_marking_scheme_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for computer_science marking-scheme lookup."""
    return await _bound_tools[2](*args, **kwargs)


@trace_agent("computer_science")
async def _comp_formative_item_generate(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for computer_science formative item generation."""
    return await _bound_tools[3](*args, **kwargs)


@trace_agent("computer_science")
async def _comp_response_score(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for computer_science response scoring."""
    return await _bound_tools[4](*args, **kwargs)


comp_syllabus_lookup_tool = FunctionTool(func=_comp_syllabus_lookup)
comp_past_paper_lookup_tool = FunctionTool(func=_comp_past_paper_lookup)
comp_marking_scheme_lookup_tool = FunctionTool(func=_comp_marking_scheme_lookup)
comp_formative_item_generate_tool = FunctionTool(func=_comp_formative_item_generate)
comp_response_score_tool = FunctionTool(func=_comp_response_score)





comp_agent = LlmAgent(
    name="comp_agent",
    model=config.litellm.resolve_model("text_llm", "subject_agent"),
    description=(
        "Computer Science specialist agent for the NCCA Leaving "
        "Certificate curriculum. Algorithms, data structures, "
        "computational thinking, programming, databases."
    ),
    instruction=(
        "You are the Computer Science specialist agent for the "
        "new tuatha/ project. Route keyword-level traffic to your "
        "5 per-subject tools and emit typed BAML responses per the "
        "`qpack_computer_science.baml` contract.\n\n"
        "THE 5 TOOLS — WHEN TO USE EACH:\n"
        "- syllabus_lookup: typed SyllabusChunk rows with provenance\n"
        "- past_paper_lookup: typed ExamPaperChunk rows\n"
        "- marking_scheme_lookup: typed MarkingCriterion rows\n"
        "- formative_item_generate: grounding evidence\n"
        "- response_score: marking-scheme evidence\n\n"
        "EVIDENCE LADDER (G7): no response without provenance "
        "(source_pdf + source_page + verbatim_text). If a tool "
        "returns zero rows, say 'No coverage for computer science on "
        "that query' — never invent content.\n\n"
        "NCCA LO NUMBERING: LC-COMP-LO-<strand>.<index>.\n\n"
        "DIFFICULTY CALIBRATION: 1 = recall (e.g., Big-O definitions); "
        "2 = 1-step trace; 3 = 2-3 step algorithm application; "
        "4 = multi-step synthesis (e.g., design + implement); "
        "5 = evaluation/proof (e.g., complexity proof).\n\n"
        "LANGUAGE: English only."
    ),
    tools=[
        comp_syllabus_lookup_tool,
        comp_past_paper_lookup_tool,
        comp_marking_scheme_lookup_tool,
        comp_formative_item_generate_tool,
        comp_response_score_tool,
    ],
    output_key="computer_science_response",
)


__all__ = ["_wire", "comp_agent", "config"]
