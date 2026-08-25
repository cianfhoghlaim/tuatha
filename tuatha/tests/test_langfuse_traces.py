"""Tests for the `@trace_agent(subject)` Langfuse decorator.

Covers the contract:
1. `trace_name_for(subject)` returns `agent.<subject>.extract`.
2. `trace_agent(subject)` decorates a sync function and the
   wrapper still returns the function's result (no-op fallback).
3. `trace_agent(subject)` decorates an async function and the
   wrapper still returns the function's result (no-op fallback).
4. The no-op fallback preserves `functools.wraps` semantics
   (`__name__`, `__doc__`).
5. When the Langfuse SDK is available, the decorator wires
   through the SDK's `observe(name=..., as_type="generation")`.
"""
from __future__ import annotations

import asyncio
import inspect
from unittest.mock import patch

import pytest


# ── trace_name_for tests ─────────────────────────────────────────────


def test_trace_name_for_mathematics() -> None:
    """The canonical trace name for mathematics is
    `agent.mathematics.extract`.
    """
    from tuatha.observability.langfuse_traces import trace_name_for

    assert trace_name_for("mathematics") == "agent.mathematics.extract"


@pytest.mark.parametrize(
    "subject",
    [
        "mathematics",
        "applied_mathematics",
        "chemistry",
        "geography",
        "history",
        "english",
        "gaeilge",
        "computer_science",
        "academic_history",
        "marking_grader",
    ],
)
def test_trace_name_for_all_subjects(subject: str) -> None:
    """Every NCCA + educational + hackathon subject gets the
    `agent.<subject>.extract` trace name.
    """
    from tuatha.observability.langfuse_traces import trace_name_for

    assert trace_name_for(subject) == f"agent.{subject}.extract"


def test_trace_template_constant() -> None:
    """`TRACE_TEMPLATE` is `agent.{subject}.extract`."""
    from tuatha.observability.langfuse_traces import TRACE_TEMPLATE

    assert TRACE_TEMPLATE == "agent.{subject}.extract"


# ── @trace_agent sync wrapper tests ──────────────────────────────────


def test_trace_agent_sync_wrapper_returns_function_value() -> None:
    """Sync function wrapped with @trace_agent still returns its value."""
    from tuatha.observability.langfuse_traces import trace_agent

    @trace_agent("mathematics")
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    assert add(2, 3) == 5


def test_trace_agent_preserves_function_metadata() -> None:
    """`@trace_agent` preserves `__name__` + `__doc__` via functools.wraps."""
    from tuatha.observability.langfuse_traces import trace_agent

    @trace_agent("chemistry")
    def my_helper() -> str:
        """A helpful function."""
        return "ok"

    assert my_helper.__name__ == "my_helper"
    assert my_helper.__doc__ == "A helpful function."


def test_trace_agent_sync_wrapper_with_args_and_kwargs() -> None:
    """Sync wrapper forwards args + kwargs to the underlying function."""
    from tuatha.observability.langfuse_traces import trace_agent

    @trace_agent("geography")
    def greet(name: str, *, greeting: str = "Hello") -> str:
        return f"{greeting}, {name}"

    assert greet("Cian", greeting="Dia duit") == "Dia duit, Cian"


# ── @trace_agent async wrapper tests ────────────────────────────────


def test_trace_agent_async_wrapper_returns_function_value() -> None:
    """Async function wrapped with @trace_agent still returns its value."""
    from tuatha.observability.langfuse_traces import trace_agent

    @trace_agent("gaeilge")
    async def fetch_async(lo_code: str) -> str:
        """Fetch an LO asynchronously."""
        return f"lo={lo_code}"

    result = asyncio.run(fetch_async("LC-GA-LO-1.1"))
    assert result == "lo=LC-GA-LO-1.1"


def test_trace_agent_async_wrapper_preserves_coroutine() -> None:
    """The async wrapper returns a coroutine (not awaited inside)."""
    from tuatha.observability.langfuse_traces import trace_agent

    @trace_agent("english")
    async def f() -> str:
        return "x"

    coro = f()
    assert inspect.iscoroutine(coro)
    # Close the coroutine to avoid warnings.
    coro.close()


def test_trace_agent_async_wrapper_with_args_and_kwargs() -> None:
    """Async wrapper forwards args + kwargs."""
    from tuatha.observability.langfuse_traces import trace_agent

    @trace_agent("history")
    async def query(year: int, *, level: str = "hl") -> str:
        return f"{year}/{level}"

    result = asyncio.run(query(2024, level="ol"))
    assert result == "2024/ol"


# ── Langfuse SDK wiring test ─────────────────────────────────────────


def test_trace_agent_calls_langfuse_observe_when_available() -> None:
    """When `langfuse.observe` is importable, `@trace_agent` wires through it
    with `name=trace_name` and `as_type="generation"`.
    """
    # We patch the module-level `_langfuse_observe` so the
    # production path is exercised without requiring the SDK
    # to be importable.
    with patch(
        "tuatha.observability.langfuse_traces._langfuse_observe",
        create=True,
    ) as mock_observe:
        # _langfuse_observe is set on the module by the import
        # try/except; we replace it via patch and reload.
        from tuatha.observability import langfuse_traces

        # Force the LBYL branch: set _LANGFUSE_AVAILABLE = True.
        langfuse_traces._LANGFUSE_AVAILABLE = True  # type: ignore[attr-defined]
        langfuse_traces._langfuse_observe = mock_observe  # type: ignore[attr-defined]
        # Make `observe(name=..., as_type=...)` return a passthrough
        # decorator (a decorator that returns the function unchanged).
        mock_observe.return_value = lambda f: f

        # Force the decorator to re-evaluate the LBYL branch.
        langfuse_traces.trace_agent("computer_science")

        mock_observe.assert_called_once_with(
            name="agent.computer_science.extract",
            as_type="generation",
        )


# ── Offline / no-op path tests ───────────────────────────────────────


def test_no_op_path_does_not_import_langfuse() -> None:
    """When the Langfuse SDK is missing, the no-op path works without it."""
    from tuatha.observability.langfuse_traces import (
        _LANGFUSE_AVAILABLE,
        trace_agent,
    )

    # In the test env the SDK is unlikely to be installed; the
    # module should still import cleanly.
    if _LANGFUSE_AVAILABLE:
        pytest.skip("Langfuse SDK is installed in this env")

    @trace_agent("mathematics")
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3


# ── Observability surface tests ──────────────────────────────────────


def test_observability_init_exports() -> None:
    """The `tuatha.observability` package exports the canonical surface."""
    from tuatha import observability

    assert hasattr(observability, "trace_agent")
    assert hasattr(observability, "trace_name_for")
    assert hasattr(observability, "_LANGFUSE_AVAILABLE")
