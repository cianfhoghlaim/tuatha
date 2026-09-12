"""tuatha.agents.educational.academic_history_agent — the cross-archive academic history agent.

Per the parent's `agents/meaisinfhoghlaim/educational/academic_history_agent.py`
pattern: the cross-subject + cross-jurisdiction history research
agent. Routes queries to the Wikipedia + CELT + Dúchas / Gaois
corpora via the BAML `qpack_academic_history.baml` contract.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent

from ...config import TuathaConfig
from ...routing import build_wire

_wire = build_wire(
    ncca_subject="academic_history",
    module_slug="academic_history",
    display_name="Academic History",
    baml_prefix="AcadHist",
    langfuse_trace_name="agent.academic_history.<verb>",
    cognee_dataset="oideachais_academic_history",
    letta_agent_id="cianfhoghlaim-academic-history-agent",
)

config = TuathaConfig.from_env()


academic_history_agent = LlmAgent(
    name="academic_history_agent",
    model=config.litellm.resolve_model("text_llm", "educational_agent"),
    description=(
        "Cross-archive academic history research agent for the "
        "British Isles MMO. Routes queries to the Wikipedia + CELT + "
        "Dúchas / Gaois corpora via the BAML "
        "`qpack_academic_history.baml` contract."
    ),
    instruction=(
        "You are the academic history specialist agent. You "
        "handle cross-archive academic history research queries "
        "for the British Isles MMO. Route keyword-level traffic "
        "to the Wikipedia + CELT + Dúchas / Gaois corpora and "
        "emit typed BAML responses per the `qpack_academic_history.baml` "
        "contract.\n\n"
        "THE 5 TOOLS — WHEN TO USE EACH:\n"
        "- list_my_modules: enumerate student's enrolled modules\n"
        "- list_my_artifacts: privacy-gated artefact enumeration\n"
        "- get_my_notes / get_my_assignments: per-student retrieval\n"
        "- get_my_exam_history / get_my_answer_scripts: exam records\n"
        "- summarise_my_progress / recommend_next_revision: heuristics\n"
        "- compare_my_answer_to_solution / search_my_formulas: cross-reference\n\n"
        "EVIDENCE LADDER (G7): no response without provenance "
        "(source_pdf + source_page + verbatim_text).\n\n"
        "LANGUAGE: English only."
    ),
    output_key="academic_history_response",
)


__all__ = ["_wire", "academic_history_agent", "config"]
