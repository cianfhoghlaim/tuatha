"""tuatha.subjects.mathematics — the Mathematics ADK agent.

One of 8 NCCA subject agents (math / appm / chem / geog / hist
/ engl / gael / comp). The agent routes keyword-level traffic
to its 5 per-subject tools (syllabus / past_paper /
marking_scheme / formative_item / response_score) and emits
typed BAML responses per the `qpack_mathematics.baml` contract.

Per the academic_history_agent.py pattern (the canonical
reference): the agent is constructed with `_BAML_AVAILABLE`
+ `_LANGFUSE_AVAILABLE` graceful degradation so the import
never crashes.

Per the centralized-registry contract: every model string
routes through `config.litellm.resolve_model(family, role)`.
"""
from __future__ import annotations

from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..observability import trace_agent
from ..routing import build_wire
from ..tools.corpus_tools import bind_subject_tools

# Build the canonical SubjectAgentWiring for mathematics.
_wire = build_wire(
    ncca_subject="mathematics",
    module_slug="math",
    display_name="Mathematics",
    baml_prefix="Math",
    langfuse_trace_name="agent.mathematics.<verb>",
    cognee_dataset="oideachais_lc_mathematics",
    letta_agent_id="cianfhoghlaim-mathematics-agent",
)

# Build the canonical config from env (Plan A keyless Firecrawl +
# MODEL_REGISTRY fallback).
config = TuathaConfig.from_env()

# The 5 per-subject tools, bound via bind_subject_tools. The
# underlying functions are wrapped below with ``@trace_agent``
# so every BAML call site emits the canonical
# ``agent.mathematics.extract`` Langfuse trace.
_bound_tools = bind_subject_tools("mathematics")


# Per-tool extraction wrappers emit the canonical
# `agent.mathematics.extract` Langfuse trace. The wrappers
# delegate to the underlying tool function unchanged via
# *args/**kwargs so they never break the existing function
# signatures. The decorator is the only addition.


@trace_agent("mathematics")
async def _math_syllabus_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for mathematics syllabus lookup."""
    return await _bound_tools[0](*args, **kwargs)


@trace_agent("mathematics")
async def _math_past_paper_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for mathematics past-paper lookup."""
    return await _bound_tools[1](*args, **kwargs)


@trace_agent("mathematics")
async def _math_marking_scheme_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for mathematics marking-scheme lookup."""
    return await _bound_tools[2](*args, **kwargs)


@trace_agent("mathematics")
async def _math_formative_item_generate(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for mathematics formative item generation."""
    return await _bound_tools[3](*args, **kwargs)


@trace_agent("mathematics")
async def _math_response_score(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for mathematics response scoring."""
    return await _bound_tools[4](*args, **kwargs)


math_syllabus_lookup_tool = FunctionTool(func=_math_syllabus_lookup)
math_past_paper_lookup_tool = FunctionTool(func=_math_past_paper_lookup)
math_marking_scheme_lookup_tool = FunctionTool(func=_math_marking_scheme_lookup)
math_formative_item_generate_tool = FunctionTool(func=_math_formative_item_generate)
math_response_score_tool = FunctionTool(func=_math_response_score)





# The canonical ADK LlmAgent for the Mathematics subject.
math_agent = LlmAgent(
    name="math_agent",
    model=config.litellm.resolve_model("text_llm", "subject_agent"),
    description=(
        "Mathematics specialist agent for the NCCA Leaving "
        "Certificate and Junior Cycle curriculum. Formative "
        "assessment, quest-pack generation, response scoring, "
        "and bilingual EN + GA feedback."
    ),
    instruction=(
        "You are the Mathematics specialist agent for the new "
        "tuatha/ project. You handle queries about the NCCA "
        "Leaving Certificate + Junior Cycle Mathematics syllabus. "
        "You route keyword-level traffic to your 5 per-subject "
        "tools (syllabus_lookup / past_paper_lookup / "
        "marking_scheme_lookup / formative_item_generate / "
        "response_score) and emit typed BAML responses per the "
        "`qpack_mathematics.baml` contract.\n\n"
        "THE 5 TOOLS — WHEN TO USE EACH:\n"
        "- syllabus_lookup: 'what does the syllabus say about X' → "
        "typed SyllabusChunk rows with provenance (source_pdf + "
        "source_page + verbatim_text)\n"
        "- past_paper_lookup: 'show me past paper questions on X' → "
        "typed ExamPaperChunk rows\n"
        "- marking_scheme_lookup: 'how is X graded' → typed "
        "MarkingCriterion rows\n"
        "- formative_item_generate: 'give me a practice question on "
        "X' → grounding evidence (NOT the question — the agent "
        "generates the question from the evidence)\n"
        "- response_score: 'grade my answer' → marking-scheme "
        "evidence (NOT a grade — the agent scores against the "
        "evidence)\n\n"
        "THE EVIDENCE LADDER (G7 CONTRACT): every tool response "
        "carries `provenance` (source_pdf + source_page + "
        "verbatim_text). If a tool returns zero rows, the response "
        "MUST say 'No coverage for mathematics on that query' — "
        "never invent content.\n\n"
        "NCCA LO NUMBERING: Learning Outcomes follow "
        "LC-MATHS-LO-<strand>.<index> (e.g., LC-MATHS-LO-2.4 = "
        "complex numbers); Junior Cycle JC-MATHS-LO-<strand>.<index>. "
        "When a query references a topic but not an LO code, first "
        "call syllabus_lookup to identify the relevant LO code, "
        "then route subsequent calls with that LO code.\n\n"
        "DIFFICULTY CALIBRATION: 1 = recall (definitions, formulas); "
        "2 = 1-step application; 3 = 2-3 step analysis; "
        "4 = multi-step synthesis; 5 = evaluation/proof.\n\n"
        "LANGUAGE: English only."
    ),
    tools=[
        math_syllabus_lookup_tool,
        math_past_paper_lookup_tool,
        math_marking_scheme_lookup_tool,
        math_formative_item_generate_tool,
        math_response_score_tool,
    ],
    output_key="mathematics_response",
)


__all__ = ["_wire", "config", "math_agent"]
