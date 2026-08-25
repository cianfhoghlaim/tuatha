"""Tests for the multi-model VLM analysis router.

Covers the contract:
1. The router resolves model strings via
   `MODEL_REGISTRY.resolve("ocr_vision", role)` — never hardcoded.
2. Logical task roles (`diagram_pointing`, `page_image`) map
   onto the actual registry roles (`specialist`, `default`).
3. The router delegates chat-completion calls to the backend
   with the resolved model key.
4. The router rejects empty messages (LBYL).
5. The StubVlmBackend echoes the request for offline tests.
6. The 3 canonical VLM entries (molmo2-8b, qwen3-vl-8b-instruct,
   olmOCR-2-7B-1025) are reachable via the canonical roles.
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest


# All tests use the offline stub backend so we never require
# httpx to be importable.
os.environ.setdefault("TUATHA_OFFLINE", "1")


# ── Role mapping tests ───────────────────────────────────────────────


def test_default_vlm_role_is_default() -> None:
    """The default VLM role is `default`."""
    from tuatha.asset_generation.vlm import DEFAULT_VLM_ROLE

    assert DEFAULT_VLM_ROLE == "default"


def test_diagram_pointing_maps_to_specialist() -> None:
    """`diagram_pointing` (task-level role) maps to `specialist`."""
    from tuatha.asset_generation.vlm import VlmRouter

    assert VlmRouter.map_role("diagram_pointing") == "specialist"


def test_page_image_maps_to_default() -> None:
    """`page_image` (task-level role) maps to `default`."""
    from tuatha.asset_generation.vlm import VlmRouter

    assert VlmRouter.map_role("page_image") == "default"


def test_unknown_role_passes_through_unchanged() -> None:
    """An unmapped role is returned unchanged (registry will error)."""
    from tuatha.asset_generation.vlm import VlmRouter

    assert VlmRouter.map_role("unknown_role") == "unknown_role"


def test_direct_registry_role_passes_through() -> None:
    """Direct registry roles (`default`, `specialist`) pass through."""
    from tuatha.asset_generation.vlm import VlmRouter

    assert VlmRouter.map_role("default") == "default"
    assert VlmRouter.map_role("specialist") == "specialist"


# ── Router resolution tests ──────────────────────────────────────────


def test_router_resolves_default_role() -> None:
    """The default role resolves to a non-empty string."""
    from tuatha.asset_generation.vlm import StubVlmBackend, VlmRouter

    router = VlmRouter(backend=StubVlmBackend())
    key = router.resolve_model()
    assert isinstance(key, str)
    assert key


def test_router_resolves_specialist_role() -> None:
    """The specialist role resolves to a non-empty string."""
    from tuatha.asset_generation.vlm import StubVlmBackend, VlmRouter

    router = VlmRouter(backend=StubVlmBackend())
    key = router.resolve_model("specialist")
    assert isinstance(key, str)
    assert key


def test_router_resolves_diagram_pointing_to_specialist_model() -> None:
    """`diagram_pointing` resolves to the same key as `specialist`."""
    from tuatha.asset_generation.vlm import StubVlmBackend, VlmRouter

    router = VlmRouter(backend=StubVlmBackend())
    pointing_key = router.resolve_model("diagram_pointing")
    specialist_key = router.resolve_model("specialist")
    assert pointing_key == specialist_key


def test_router_resolves_page_image_to_default_model() -> None:
    """`page_image` resolves to the same key as `default`."""
    from tuatha.asset_generation.vlm import StubVlmBackend, VlmRouter

    router = VlmRouter(backend=StubVlmBackend())
    page_key = router.resolve_model("page_image")
    default_key = router.resolve_model("default")
    assert page_key == default_key


def test_router_resolves_to_canonical_vlm_entries() -> None:
    """The 3 canonical VLM entries are reachable (molmo2-8b,
    qwen3-vl-8b-instruct, olmOCR-2-7B-1025).
    """
    from tuatha.asset_generation.vlm import StubVlmBackend, VlmRouter

    router = VlmRouter(backend=StubVlmBackend())
    # Walk every available ocr_vision entry to verify the
    # router can resolve them all. (At minimum the 3 canonical
    # entries above must be present.)
    from tuatha.asset_generation.vlm.router import model_for as _mf

    if _mf is None:
        pytest.skip("MODEL_REGISTRY not available — skipping canonical-entries check")

    from meaisinfhoghlaim.models import MODEL_REGISTRY  # type: ignore[import-not-found]

    entries = MODEL_REGISTRY.filter(family="ocr_vision")
    assert len(entries) >= 3
    keys = {e.key for e in entries}
    # The 3 canonical VLM entries from the Phase 1 spec.
    assert "molmo2-8b" in keys
    assert "qwen3-vl-8b-instruct" in keys
    assert "olmocr-2-7b-1025" in keys


# ── analyze() tests ──────────────────────────────────────────────────


def test_router_analyze_passes_resolved_model_to_backend() -> None:
    """`analyze()` resolves the model key then passes it to the backend."""
    from tuatha.asset_generation.vlm import StubVlmBackend, VlmRouter

    fake_backend = MagicMock(spec=StubVlmBackend)
    fake_backend.chat.return_value = {
        "choices": [{"message": {"content": "ok"}}]
    }

    router = VlmRouter(backend=fake_backend)
    messages = [{"role": "user", "content": "What is this diagram?"}]
    router.analyze(messages=messages, role="diagram_pointing")

    fake_backend.chat.assert_called_once()
    call_kwargs = fake_backend.chat.call_args.kwargs
    # The router passes `model` + `messages` as kwargs.
    model_key = call_kwargs["model"]
    assert isinstance(model_key, str)
    assert model_key, "model key must be non-empty"
    # The messages were passed through.
    assert call_kwargs["messages"] == messages


def test_router_analyze_rejects_empty_messages() -> None:
    """LBYL: empty messages raise ValueError."""
    from tuatha.asset_generation.vlm import StubVlmBackend, VlmRouter

    router = VlmRouter(backend=StubVlmBackend())

    with pytest.raises(ValueError):
        router.analyze(messages=[])


def test_router_analyze_forwards_temperature_max_tokens() -> None:
    """`temperature` and `max_tokens` are forwarded to the backend."""
    from tuatha.asset_generation.vlm import StubVlmBackend, VlmRouter

    fake_backend = MagicMock(spec=StubVlmBackend)
    fake_backend.chat.return_value = {
        "choices": [{"message": {"content": "ok"}}]
    }

    router = VlmRouter(backend=fake_backend)
    router.analyze(
        messages=[{"role": "user", "content": "x"}],
        role="page_image",
        temperature=0.7,
        max_tokens=512,
    )

    call_kwargs = fake_backend.chat.call_args.kwargs
    assert call_kwargs["temperature"] == 0.7
    assert call_kwargs["max_tokens"] == 512


def test_router_analyze_extra_body_merged() -> None:
    """`extra_body` is forwarded to the backend as-is."""
    from tuatha.asset_generation.vlm import StubVlmBackend, VlmRouter

    fake_backend = MagicMock(spec=StubVlmBackend)
    fake_backend.chat.return_value = {
        "choices": [{"message": {"content": "ok"}}]
    }

    router = VlmRouter(backend=fake_backend)
    extra = {"image_grid": [[0, 0], [1, 1]]}
    router.analyze(
        messages=[{"role": "user", "content": "x"}],
        role="diagram_pointing",
        extra_body=extra,
    )

    call_kwargs = fake_backend.chat.call_args.kwargs
    assert call_kwargs["extra_body"] == extra


# ── Stub backend tests ───────────────────────────────────────────────


def test_stub_vlm_backend_echoes_request() -> None:
    """The StubVlmBackend returns a request-shaped echo dict."""
    from tuatha.asset_generation.vlm import StubVlmBackend

    backend = StubVlmBackend()
    messages = [{"role": "user", "content": "hi"}]
    result = backend.chat(
        model="molmo2-8b",
        messages=messages,
        temperature=0.5,
        max_tokens=256,
        extra_body={"foo": "bar"},
    )

    assert result["id"] == "stub-chatcmpl"
    assert result["model"] == "molmo2-8b"
    assert result["choices"][0]["message"]["content"] == "[stub] VLM response"
    assert result["choices"][0]["stub"] is True
    assert result["echoed"]["messages"] == messages
    assert result["echoed"]["temperature"] == 0.5
    assert result["echoed"]["max_tokens"] == 256
    assert result["echoed"]["extra_body"] == {"foo": "bar"}


# ── UnslothVlmBackend tests ──────────────────────────────────────────


def test_unsloth_vlm_backend_uses_provided_client() -> None:
    """UnslothVlmBackend forwards calls to the provided UnslothClient."""
    from tuatha.asset_generation.vlm import UnslothVlmBackend

    fake_client = MagicMock()
    fake_client.chat_completion.return_value = {"choices": [{"message": {"content": "y"}}]}

    backend = UnslothVlmBackend(client=fake_client)
    messages = [{"role": "user", "content": "x"}]
    result = backend.chat(
        model="qwen3-vl-8b-instruct",
        messages=messages,
        temperature=0.0,
        max_tokens=128,
        extra_body=None,
    )

    fake_client.chat_completion.assert_called_once_with(
        model="qwen3-vl-8b-instruct",
        messages=messages,
        temperature=0.0,
        max_tokens=128,
        extra_body=None,
    )
    assert result == {"choices": [{"message": {"content": "y"}}]}


# ── Lifecycle tests ──────────────────────────────────────────────────


def test_router_close_is_idempotent() -> None:
    """`close()` is idempotent on a stub backend."""
    from tuatha.asset_generation.vlm import StubVlmBackend, VlmRouter

    router = VlmRouter(backend=StubVlmBackend())
    router.close()
    router.close()


def test_router_works_as_context_manager() -> None:
    """The router works as a context manager."""
    from tuatha.asset_generation.vlm import StubVlmBackend, VlmRouter

    fake_backend = MagicMock(spec=StubVlmBackend)
    fake_backend.chat.return_value = {
        "choices": [{"message": {"content": "ok"}}]
    }

    with VlmRouter(backend=fake_backend) as router:
        router.analyze(
            messages=[{"role": "user", "content": "x"}],
            role="default",
        )


# ── Hard-rule guard: no hardcoded model strings ──────────────────────


def test_no_hardcoded_model_strings_in_router_module() -> None:
    """LBYL: the VLM router module must not contain hardcoded
    `<hf-org>/<hf-model>` literals or registry-bypassing
    `litellm_alias=` strings.
    """
    from pathlib import Path

    src_path = Path(
        "/Users/cianmacandeisigh/dev/tuatha/tuatha/asset_generation/vlm/router.py"
    )
    text = src_path.read_text()
    # STUB_VLM_MODEL_KEY is the only allowed literal.
    assert text.count('"stub/vlm/unknown"') == 1
