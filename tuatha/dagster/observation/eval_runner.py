"""tuatha.dagster.observation.eval_runner — wraps AgentEvaluator.run_eval(...).

Per the
`openspec/changes/2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1/`
T3.2: wraps `google.adk.evaluation.AgentEvaluator.run_eval(...)`
with a graceful-degradation fallback (no-op decorator when
google-adk is not installed).

Per the centralized-registry contract: LLM-as-judge calls
route through `MODEL_REGISTRY.resolve("text_llm", "judge")`.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# Module-level LBYL probe.
try:
    from google.adk.evaluation import AgentEvaluator  # type: ignore

    _ADK_AGENT_EVALUATOR_AVAILABLE = True
except ImportError:
    AgentEvaluator = None  # type: ignore
    _ADK_AGENT_EVALUATOR_AVAILABLE = False


def run_eval(
    eval_set_path: str,
    *,
    agent_module: str = "tuatha.agents.media_intel.media_descriptor_agent",
    raise_on_unavailable: bool = False,
) -> dict[str, Any]:
    """Run an eval set via AgentEvaluator.run_eval(...).

    Args:
        eval_set_path: path to the YAML eval set (relative to the
            `tuatha/dagster/observation/eval_sets/` directory).
        agent_module: the module path of the ADK agent under test.
        raise_on_unavailable: when True, raise ImportError if
            google-adk is not installed. Default: log a warning +
            return a no-op result.

    Returns:
        A dict with the run summary + per-case scores.
    """
    if not _ADK_AGENT_EVALUATOR_AVAILABLE:
        msg = (
            f"google-adk not installed; cannot run eval_set={eval_set_path}. "
            "Install with `uv pip install google-adk`."
        )
        if raise_on_unavailable:
            raise ImportError(msg)
        logger.warning(msg)
        return {
            "noop": True,
            "eval_set": eval_set_path,
            "agent_module": agent_module,
            "cases": [],
        }

    # The real AgentEvaluator.run_eval(...) call.
    return AgentEvaluator.run_eval(  # type: ignore[union-attr]
        eval_set_path=eval_set_path,
        agent_module=agent_module,
    )


__all__ = ["run_eval"]
