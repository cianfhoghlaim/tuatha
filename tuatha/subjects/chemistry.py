"""tuatha.subjects.chemistry — the Chemistry ADK agent.

One of 8 NCCA subject agents. BAML prefix: Chem.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.corpus_tools import bind_subject_tools

_wire = build_wire(
    ncca_subject="chemistry",
    module_slug="chem",
    display_name="Chemistry",
    baml_prefix="Chem",
    langfuse_trace_name="agent.chemistry.<verb>",
    cognee_dataset="oideachais_lc_chemistry",
    letta_agent_id="kcg-chemistry-agent",
)

config = TuathaConfig.from_env()

# The five corpus tools, bound to this subject so the model
# cannot query another subject's corpus.
_tools = [FunctionTool(func=f) for f in bind_subject_tools("chemistry")]


chem_agent = LlmAgent(
    name="chem_agent",
    model=config.litellm.resolve_model("subject_agent"),
    description=(
        "Chemistry specialist agent for the NCCA Leaving Certificate "
        "and Junior Cycle curriculum. Atomic structure, bonding, "
        "stoichiometry, organic chemistry, equilibrium."
    ),
    instruction=(
        "You are the Chemistry specialist agent for the new "
        "tuatha/ project. Route keyword-level traffic to your 5 "
        "per-subject tools and emit typed BAML responses per the "
        "`qpack_chemistry.baml` contract."
    ),
    tools=_tools,
    output_key="chemistry_response",
)


__all__ = ["_wire", "chem_agent", "config"]
