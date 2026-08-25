"""The conftest for the Phase 1 P1+P7 test suite.

Provides the shared fixtures needed to test the multi-model
image-gen + VLM routers + the Langfuse decorator in the
tuatha/ venv without requiring `httpx` + `langfuse` to be
installed.

We use `sys.modules` injection (the canonical pattern for
mocking optional dependencies in tests) to make the test
surface import-clean in the offline / CI env. The mocks are
minimal: they only expose the attributes the production
modules reach for at runtime.
"""
from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock


# ── httpx mock ────────────────────────────────────────────────────────
# UnslothClient uses `httpx.Client`, `httpx.HTTPError`,
# `httpx.ConnectError`, and `httpx.Response`. We stub a minimal
# module that satisfies the duck-typed interface.

_HTTPX_RESPONSE_BASE = {
    "status_code": 200,
    "text": "",
}


def _make_fake_httpx() -> SimpleNamespace:
    """Build a minimal `httpx` mock module."""
    fake_client = MagicMock(name="httpx.Client")
    fake_http_error = type("HTTPError", (Exception,), {})
    # ConnectError must inherit from HTTPError so that the
    # `except httpx.HTTPError` clause in UnslothClient catches it.
    fake_connect_error = type("ConnectError", (fake_http_error,), {})

    fake_module = SimpleNamespace(
        Client=fake_client,
        HTTPError=fake_http_error,
        ConnectError=fake_connect_error,
        Response=MagicMock(name="httpx.Response"),
        _HTTPX_AVAILABLE=True,
    )
    return fake_module


# Inject the fake httpx module BEFORE any test imports
# unsloth_client. This makes `import httpx` succeed with our
# mock.
_fake_httpx = _make_fake_httpx()
sys.modules.setdefault("httpx", _fake_httpx)


# Also force the unsloth_client module's httpx reference to be
# the mock (so its internal checks pass).
def _patch_unsloth_client_httpx() -> None:
    try:
        from tuatha.asset_generation.image_gen import unsloth_client

        unsloth_client.httpx = _fake_httpx  # type: ignore[attr-defined]
        unsloth_client._HTTPX_AVAILABLE = True  # type: ignore[attr-defined]
    except ImportError:
        # The unsloth_client isn't installed in this env; nothing
        # to patch.
        pass


_patch_unsloth_client_httpx()
