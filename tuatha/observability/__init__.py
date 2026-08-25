"""tuatha.observability — the agent-tracing surface for the new tuatha/ project.

Per the agent-observability + centralized-model-registry contracts,
the observability layer exposes the `@trace_agent(subject)` decorator
that wraps every BAML call site with a `agent.<subject>.extract`
Langfuse trace.

The decorator is the canonical mount point for:
- The 8 NCCA subject agents (math / appm / chem / geog / hist /
  engl / gael / comp)
- The 3 educational agents (academic_history + celtic_grammar +
  celtic_morphology)
- The 4 BIEP hackathon features (marking_grader + adaptive_tutor +
  equivalency_generator + curriculum_change_sensor)

When the Langfuse SDK is unavailable (offline dev / unit tests),
the decorator falls back to a no-op + emits a TODO note so the
trace contract is preserved without crashing the import.
"""
from __future__ import annotations

from tuatha.observability.langfuse_traces import (
    _LANGFUSE_AVAILABLE,
    trace_agent,
    trace_name_for,
)

__all__ = [
    "_LANGFUSE_AVAILABLE",
    "trace_agent",
    "trace_name_for",
]
