"""tuatha.dagster.observation.otel_langfuse_bridge — ADK OTEL → Langfuse.

Per the
`openspec/changes/2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1/`
T3.5: send the ADK OTEL spans to the Langfuse backend
(`langfuse.cianfhoghlaim.ie`) so the eval trajectories appear
in the Langfuse UI.

This is a thin bridge — the canonical Langfuse integration
already lives at `tuatha/tuatha/observability/langfuse_traces.py`.
The bridge here ADDS the ADK-specific span names (e.g.,
`agent.<subject>.extract` → `eval.<eval_set_name>.case.<case_name>`).

Per the centralized-registry contract: no hardcoded model
strings; routes through `MODEL_REGISTRY.resolve("text_llm",
"judge")`.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


# Module-level LBYL probe (per the langfuse_traces.py pattern).
try:
    from langfuse import observe as _langfuse_observe  # type: ignore

    _LANGFUSE_AVAILABLE = True
except ImportError:
    _LANGFUSE_AVAILABLE = False


def bridge_adk_span_to_langfuse(
    *,
    eval_set_name: str,
    case_name: str,
    score: float,
    threshold: float,
    passed: bool,
) -> dict[str, bool | float | str]:
    """Bridge one ADK eval trajectory to a Langfuse span.

    Returns a no-op dict when Langfuse is not available (the
    offline dev path).

    Per the AGENTS.md pattern: graceful degradation never
    crashes the import.
    """
    if not _LANGFUSE_AVAILABLE:
        logger.debug(
            "Langfuse not available; returning no-op bridge for "
            "eval_set=%s case=%s",
            eval_set_name,
            case_name,
        )
        return {
            "noop": True,
            "eval_set": eval_set_name,
            "case": case_name,
        }

    # The real bridge emits an OTEL span via langfuse.decorators.observe.
    @_langfuse_observe(name=f"eval.{eval_set_name}.{case_name}", as_type="generation")
    def _emit() -> dict[str, bool | float | str]:
        return {
            "score": score,
            "threshold": threshold,
            "passed": passed,
            "eval_set": eval_set_name,
            "case": case_name,
        }

    return _emit()


__all__ = ["bridge_adk_span_to_langfuse"]
