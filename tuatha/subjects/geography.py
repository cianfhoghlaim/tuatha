"""tuatha.subjects.geography — the Geography ADK agent.

One of 8 NCCA subject agents. BAML prefix: Geog.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.corpus_tools import bind_subject_tools

_wire = build_wire(
    ncca_subject="geography",
    module_slug="geog",
    display_name="Geography",
    baml_prefix="Geog",
    langfuse_trace_name="agent.geography.<verb>",
    cognee_dataset="oideachais_lc_geography",
    letta_agent_id="kcg-geography-agent",
)

config = TuathaConfig.from_env()

# The five corpus tools, bound to this subject so the model
# cannot query another subject's corpus.
_tools = [FunctionTool(func=f) for f in bind_subject_tools("geography")]


geog_agent = LlmAgent(
    name="geog_agent",
    model=config.litellm.resolve_model("subject_agent"),
    description=(
        "Geography specialist agent for the NCCA Leaving "
        "Certificate and Junior Cycle curriculum. Physical "
        "geography, regional geography, human-environment "
        "interaction, geographic investigation."
    ),
    instruction=(
        "You are the Geography specialist agent for the new "
        "tuatha/ project. Route keyword-level traffic to your 5 "
        "per-subject tools and emit typed BAML responses per the "
        "`qpack_geography.baml` contract."
    ),
    tools=_tools,
    output_key="geography_response",
)


__all__ = ["_wire", "config", "geog_agent"]
