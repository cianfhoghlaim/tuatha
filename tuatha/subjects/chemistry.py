"""tuatha.subjects.chemistry — the Chemistry ADK agent.

One of 8 NCCA subject agents. BAML prefix: Chem.
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
    ncca_subject="chemistry",
    module_slug="chem",
    display_name="Chemistry",
    baml_prefix="Chem",
    langfuse_trace_name="agent.chemistry.<verb>",
    cognee_dataset="oideachais_lc_chemistry",
    letta_agent_id="cianfhoghlaim-chemistry-agent",
)

config = TuathaConfig.from_env()

# The 5 per-subject tools, bound via bind_subject_tools.
_bound_tools = bind_subject_tools("chemistry")
chem_syllabus_lookup_tool = FunctionTool(func=_bound_tools[0])
chem_past_paper_lookup_tool = FunctionTool(func=_bound_tools[1])
chem_marking_scheme_lookup_tool = FunctionTool(func=_bound_tools[2])
chem_formative_item_generate_tool = FunctionTool(func=_bound_tools[3])
chem_response_score_tool = FunctionTool(func=_bound_tools[4])


# Per-tool extraction wrappers emit the canonical
# `agent.chemistry.extract` Langfuse trace. The wrappers
# delegate to the underlying tool function unchanged via
# *args/**kwargs so they never break the existing function
# signatures. The decorator is the only addition.





chem_agent = LlmAgent(
    name="chem_agent",
    model=config.litellm.resolve_model("text_llm", "subject_agent"),
    description=(
        "Chemistry specialist agent for the NCCA Leaving Certificate "
        "and Junior Cycle curriculum. Atomic structure, bonding, "
        "stoichiometry, organic chemistry, equilibrium."
    ),
    instruction=(
        "You are the Chemistry specialist agent for the new "
        "tuatha/ project. Route keyword-level traffic to your 5 "
        "per-subject tools and emit typed BAML responses per the "
        "`qpack_chemistry.baml` contract.\n\n"
        "THE 5 TOOLS — WHEN TO USE EACH:\n"
        "- syllabus_lookup: typed SyllabusChunk rows with provenance\n"
        "- past_paper_lookup: typed ExamPaperChunk rows\n"
        "- marking_scheme_lookup: typed MarkingCriterion rows\n"
        "- formative_item_generate: grounding evidence (the agent "
        "generates the question from the evidence)\n"
        "- response_score: marking-scheme evidence\n\n"
        "EVIDENCE LADDER (G7): no response without provenance "
        "(source_pdf + source_page + verbatim_text). If a tool "
        "returns zero rows, say 'No coverage for chemistry on that "
        "query' — never invent content.\n\n"
        "NCCA LO NUMBERING: LC-CHEM-LO-<strand>.<index> / "
        "JC-CHEM-LO-<strand>.<index>. When a query references a "
        "topic but not an LO code, first call syllabus_lookup.\n\n"
        "DIFFICULTY CALIBRATION: 1 = recall; 2 = 1-step; 3 = 2-3 "
        "step; 4 = multi-step synthesis; 5 = evaluation/proof.\n\n"
        "LANGUAGE: English only."
    ),
    tools=[
        chem_syllabus_lookup_tool,
        chem_past_paper_lookup_tool,
        chem_marking_scheme_lookup_tool,
        chem_formative_item_generate_tool,
        chem_response_score_tool,
    ],
    output_key="chemistry_response",
)


__all__ = ["_wire", "chem_agent", "config"]
