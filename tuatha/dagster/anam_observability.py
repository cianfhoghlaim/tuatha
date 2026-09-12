"""Observability wrappers for the ANAM capture pipeline.

Three layers (per the agent-observability skill):
  1. Langfuse @observe decorators (cost + prompt management)
  2. MLflow experiment tracking (model registry + metrics)
  3. structlog structured logging (JSON for prod, console for dev)

All 3 are wired here so every CocoIndex + Dagster + Hermes call lands
in the central observability platform.
"""
from __future__ import annotations

import functools
import inspect
import os
from collections.abc import Callable
from typing import Any

import structlog

# -- structlog (always-on, zero deps outside the stdlib + structlog) ----------


def configure_logging(*, service: str = "tuatha-anam", env: str | None = None) -> None:
    """Wire structlog to JSONRenderer (prod) or ConsoleRenderer (dev)."""
    env = env or os.environ.get("TUATHA_ENV", "development")
    processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if env == "production":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(20 if env == "production" else 10),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    structlog.contextvars.bind_contextvars(service=service, env=env)


# -- Langfuse @observe ---------------------------------------------------------


def langfuse_observe(*, name: str, as_type: str = "span") -> Callable:
    """Decorator: wrap a function in Langfuse tracing.

    Falls back to a logging no-op when langfuse is absent, so the
    CocoIndex flows and Dagster assets still run in CI without secrets.

    Langfuse v3 moved ``observe`` from ``langfuse.decorators`` to the
    package root. Only the old path was tried here, so against the
    declared ``langfuse>=3.0`` the import always failed and the
    pipeline ran permanently untraced without saying so.
    """
    try:
        try:
            from langfuse import observe  # type: ignore[import-not-found]
        except ImportError:
            from langfuse.decorators import observe  # type: ignore[import-not-found,no-redef]

        return observe(name=name, as_type=as_type)
    except ImportError:

        def _decorator(fn: Callable) -> Callable:
            @functools.wraps(fn)
            async def _async(*args: Any, **kwargs: Any) -> Any:
                log = structlog.get_logger("tuatha.anam.langfuse")
                log.info("langfuse_fallback_async", fn=name, as_type=as_type)
                return await fn(*args, **kwargs)

            @functools.wraps(fn)
            def _sync(*args: Any, **kwargs: Any) -> Any:
                log = structlog.get_logger("tuatha.anam.langfuse")
                log.info("langfuse_fallback_sync", fn=name, as_type=as_type)
                return fn(*args, **kwargs)

            return _async if inspect.iscoroutinefunction(fn) else _sync

        return _decorator


# -- MLflow experiment tracking ------------------------------------------------


def mlflow_log_metric(name: str, value: float, *, step: int | None = None) -> None:
    """Log a metric to the canonical tuatha-anam experiment.

    Falls back to a log message if mlflow is not installed.
    """
    try:
        import mlflow  # type: ignore[import-not-found]

        mlflow.set_tracking_uri(
            os.environ.get(
                "MLFLOW_TRACKING_URI",
                "https://mlflow.cianfhoghlaim.ie",
            )
        )
        mlflow.set_experiment("tuatha-anam")
        with mlflow.start_run(run_name=os.environ.get("TUATHA_RUN_ID", "local")):
            mlflow.log_metric(name, value, step=step)
    except ImportError:
        log = structlog.get_logger("tuatha.anam.mlflow")
        log.info("mlflow_fallback", metric=name, value=value)


# -- The 3 RAGAS-friendly metrics we register --------------------------------


def ragas_color_anchor_metric(score: float) -> dict[str, Any]:
    """Custom RAGAS metric: color_anchor — see tuatha/dagster/anam.py.

    Returns the metric envelope for the Langfuse trace.
    """
    return {
        "metric": "anam_color_anchor",
        "score": score,
        "threshold": 0.85,
        "direction": "maximize",
    }
