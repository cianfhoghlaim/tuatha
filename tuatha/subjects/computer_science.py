"""tuatha.subjects.computer_science — the Computer Science ADK agent.

One of 8 NCCA subject agents. BAML prefix: Comp.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.corpus_tools import bind_subject_tools

_wire = build_wire(
    ncca_subject="computer_science",
    module_slug="comp",
    display_name="Computer Science",
    baml_prefix="Comp",
    langfuse_trace_name="agent.computer_science.<verb>",
    cognee_dataset="oideachais_lc_computer_science",
    letta_agent_id="kcg-computer-science-agent",
)

config = TuathaConfig.from_env()

# The five corpus tools, bound to this subject so the model
# cannot query another subject's corpus.
_tools = [FunctionTool(func=f) for f in bind_subject_tools("computer_science")]


comp_agent = LlmAgent(
    name="comp_agent",
    model=config.litellm.resolve_model("subject_agent"),
    description=(
        "Computer Science specialist agent for the NCCA Leaving "
        "Certificate curriculum. Algorithms, data structures, "
        "computational thinking, programming, databases."
    ),
    instruction=(
        "You are the Computer Science specialist agent for the "
        "new tuatha/ project. Route keyword-level traffic to your "
        "5 per-subject tools and emit typed BAML responses per the "
        "`qpack_computer_science.baml` contract."
    ),
    tools=_tools,
    output_key="computer_science_response",
)


__all__ = ["_wire", "comp_agent", "config"]
