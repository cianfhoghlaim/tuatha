"""tuatha.subjects.english — the English ADK agent.

One of 8 NCCA subject agents. BAML prefix: Engl.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.corpus_tools import bind_subject_tools

_wire = build_wire(
    ncca_subject="english",
    module_slug="engl",
    display_name="English",
    baml_prefix="Engl",
    langfuse_trace_name="agent.english.<verb>",
    cognee_dataset="oideachais_lc_english",
    letta_agent_id="kcg-english-agent",
)

config = TuathaConfig.from_env()

# The five corpus tools, bound to this subject so the model
# cannot query another subject's corpus.
_tools = [FunctionTool(func=f) for f in bind_subject_tools("english")]


engl_agent = LlmAgent(
    name="engl_agent",
    model=config.litellm.resolve_model("subject_agent"),
    description=(
        "English specialist agent for the NCCA Leaving "
        "Certificate and Junior Cycle curriculum. Comprehension, "
        "composition, language awareness, literary analysis."
    ),
    instruction=(
        "You are the English specialist agent for the new "
        "tuatha/ project. Route keyword-level traffic to your 5 "
        "per-subject tools and emit typed BAML responses per the "
        "`qpack_english.baml` contract."
    ),
    tools=_tools,
    output_key="english_response",
)


__all__ = ["_wire", "config", "engl_agent"]
