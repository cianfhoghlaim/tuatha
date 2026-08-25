"""tuatha.subjects.applied_mathematics — the Applied Mathematics ADK agent.

One of 8 NCCA subject agents. Mirrors the Mathematics agent
pattern. BAML prefix: AppM.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.corpus_tools import bind_subject_tools

_wire = build_wire(
    ncca_subject="applied_mathematics",
    module_slug="appm",
    display_name="Applied Mathematics",
    baml_prefix="AppM",
    langfuse_trace_name="agent.applied_mathematics.<verb>",
    cognee_dataset="oideachais_lc_applied_mathematics",
    letta_agent_id="kcg-applied-mathematics-agent",
)

config = TuathaConfig.from_env()

# The five corpus tools, bound to this subject so the model
# cannot query another subject's corpus.
_tools = [FunctionTool(func=f) for f in bind_subject_tools("applied_mathematics")]


appm_agent = LlmAgent(
    name="appm_agent",
    model=config.litellm.resolve_model("subject_agent"),
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
        "`qpack_applied_mathematics.baml` contract."
    ),
    tools=_tools,
    output_key="applied_mathematics_response",
)


__all__ = ["_wire", "appm_agent", "config"]
