"""Tuatha ADK configuration.

Per the openspec change `2026-09-06-adk-gemini-deep-research-control-plane-v1`,
the Tuatha ADK agents (`tuatha_root_agent`, `celtic_tutor_agent`,
`mythology_narrator_agent`) read their model assignments from this single
config object. The orchestrator uses a higher-capability model than the
worker agents.

When the change ships the real config (LiteLLM-resolved model names from
the `tuatha/config.py:orchestrator_model` + `tuatha/config.py:worker_model`
fields), replace the stub strings below with the resolved model IDs.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TuathaAdkConfig:
    """Resolved ADK config for the Tuatha Celtic Educational MMO."""

    orchestrator_model: str = "gemini/gemini-2.5-pro"
    worker_model: str = "gemini/gemini-2.5-flash"


config = TuathaAdkConfig()
