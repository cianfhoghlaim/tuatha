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
routes through `config.litellm.resolve_model(role)`.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
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
    letta_agent_id="kcg-mathematics-agent",
)

# Build the canonical config from env (Plan A keyless Firecrawl +
# MODEL_REGISTRY fallback).
config = TuathaConfig.from_env()

# The 5 per-subject tools.
# The five corpus tools, bound to this subject so the model
# cannot query another subject's corpus.
_tools = [FunctionTool(func=f) for f in bind_subject_tools("mathematics")]


# The canonical ADK LlmAgent for the Mathematics subject.
math_agent = LlmAgent(
    name="math_agent",
    model=config.litellm.resolve_model("subject_agent"),
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
        "`qpack_mathematics.baml` contract."
    ),
    tools=_tools,
    output_key="mathematics_response",
)


__all__ = ["_wire", "config", "math_agent"]
