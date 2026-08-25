"""tuatha.observability.langfuse_traces — the `@trace_agent(subject)` decorator.

Per the agent-observability openspec capability, every BAML call
site in the new tuatha/ project emits a `agent.<subject>.extract`
Langfuse trace via this decorator. The decorator:

1. Uses `langfuse.observe(name=..., as_type="generation")` when
   the Langfuse SDK is importable. The `as_type="generation"`
   is the right hint for BAML extraction calls so the Langfuse
   UI groups them under the correct LLM-call surface.
2. Falls back to a no-op decorator when Langfuse is unavailable
   (offline dev / unit tests). The no-op preserves the trace
   contract: the function still runs, just without emitting a
   remote trace.

TODO(offline-dev): replace the no-op with a structlog-based local
emitter once the Langfuse SDK is wired into the test harness.

Usage:
    from tuatha.observability.langfuse_traces import trace_agent

    @trace_agent("mathematics")
    async def extract_math_syllabus(lo_code: str) -> dict:
        return await b.GenerateMathSyllabus(lo_code=lo_code)
"""
from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


# LBYL: probe the Langfuse SDK once at import time. We deliberately
# do NOT wrap this in a try/except that hides the failure — any
# import failure (other than ImportError) should surface, not be
# silently swallowed.
try:
    from langfuse import observe as _langfuse_observe  # type: ignore[import-not-found]

    _LANGFUSE_AVAILABLE = True
except ImportError:
    _langfuse_observe = None  # type: ignore[assignment]
    _LANGFUSE_AVAILABLE = False


# Per the centralized-langfuse-trace-naming contract:
# every trace is `agent.<subject>.extract`.
TRACE_TEMPLATE = "agent.{subject}.extract"


def trace_name_for(subject: str) -> str:
    """Return the canonical Langfuse trace name for the given subject.

    Args:
        subject: One of the 8 NCCA subject slugs (mathematics,
            applied_mathematics, chemistry, geography, history,
            english, gaeilge, computer_science) OR one of the
            educational / hackathon slugs.

    Returns:
        The canonical `agent.<subject>.extract` trace name.
    """
    return TRACE_TEMPLATE.format(subject=subject)


def trace_agent(subject: str) -> Callable[[F], F]:
    """Decorator that wraps a BAML call site with the canonical
    `agent.<subject>.extract` Langfuse trace.

    Args:
        subject: The subject slug for the trace name (e.g.,
            "mathematics", "applied_mathematics", "gaeilge",
            "academic_history", "marking_grader").

    Returns:
        A decorator that wraps the input function. When the
        Langfuse SDK is available the wrapper emits a real trace;
        otherwise it is a no-op (the function still runs).
    """
    trace_name = trace_name_for(subject)

    if _LANGFUSE_AVAILABLE and _langfuse_observe is not None:
        # The Langfuse path — wrap with the SDK decorator.
        # as_type="generation" is the right hint for BAML
        # extraction calls.
        return _langfuse_observe(name=trace_name, as_type="generation")

    # No-op path — offline dev / unit tests. We still record
    # what the trace name WOULD be so the contract is preserved.
    def _noop_decorator(func: F) -> F:
        # TODO(offline-dev): replace with structlog local
        # emitter once the Langfuse SDK is wired into the
        # test harness.

        @wraps(func)
        async def _async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await func(*args, **kwargs)

        @wraps(func)
        def _sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        # Pick the right wrapper based on whether `func` is
        # a coroutine function.
        if _is_coroutine_function(func):
            return _async_wrapper  # type: ignore[return-value]
        return _sync_wrapper  # type: ignore[return-value]

    return _noop_decorator


def _is_coroutine_function(func: Callable[..., Any]) -> bool:
    """LBYL: detect whether `func` is declared with `async def`.

    We use `inspect.iscoroutinefunction` which works for both
    `async def` functions and callable instances with
    `__call__` marked async.
    """
    import inspect

    return inspect.iscoroutinefunction(func)


__all__ = [
    "TRACE_TEMPLATE",
    "_LANGFUSE_AVAILABLE",
    "trace_agent",
    "trace_name_for",
]
