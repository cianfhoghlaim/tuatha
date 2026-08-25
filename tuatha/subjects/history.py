"""tuatha.subjects.history — the History ADK agent.

One of 8 NCCA subject agents. BAML prefix: Hist.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.corpus_tools import bind_subject_tools

_wire = build_wire(
    ncca_subject="history",
    module_slug="hist",
    display_name="History",
    baml_prefix="Hist",
    langfuse_trace_name="agent.history.<verb>",
    cognee_dataset="oideachais_lc_history",
    letta_agent_id="kcg-history-agent",
)

config = TuathaConfig.from_env()

# The five corpus tools, bound to this subject so the model
# cannot query another subject's corpus.
_tools = [FunctionTool(func=f) for f in bind_subject_tools("history")]


hist_agent = LlmAgent(
    name="hist_agent",
    model=config.litellm.resolve_model("subject_agent"),
    description=(
        "History specialist agent for the NCCA Leaving "
        "Certificate and Junior Cycle curriculum. Early modern, "
        "modern Irish, European, world history."
    ),
    instruction=(
        "You are the History specialist agent for the new "
        "tuatha/ project. Route keyword-level traffic to your 5 "
        "per-subject tools and emit typed BAML responses per the "
        "`qpack_history.baml` contract."
    ),
    tools=_tools,
    output_key="history_response",
)


__all__ = ["_wire", "config", "hist_agent"]
