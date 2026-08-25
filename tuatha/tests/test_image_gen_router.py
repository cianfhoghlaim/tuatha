"""Tests for the multi-model image-gen router.

Covers the contract:
1. The router resolves model strings via
   `MODEL_REGISTRY.resolve("image_gen", role)` — never hardcoded.
2. The router delegates to the backend with the resolved key.
3. The router rejects empty prompts (LBYL).
4. The StubImageGenBackend is the canonical offline fallback.
5. The UnslothImageGenBackend wraps `UnslothClient`.
6. The UnslothClient retries on 5xx with exponential backoff.
7. The UnslothClient does NOT retry on 4xx (caller mistake).
8. The 7 canonical image_gen roles all resolve to distinct
   registry keys.
"""
from __future__ import annotations

import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


# All tests in this module use the offline stub backend so we
# never require httpx to be importable. The UnslothImageGenBackend
# is exercised separately via a mocked UnslothClient.
os.environ.setdefault("TUATHA_OFFLINE", "1")


# ── ImageGenRouter tests ──────────────────────────────────────────────


def test_router_with_stub_backend_default_role() -> None:
    """The default role is `fibo` and resolves to a non-empty string."""
    from tuatha.asset_generation.image_gen import (
        DEFAULT_IMAGE_GEN_ROLE,
        ImageGenRouter,
        StubImageGenBackend,
    )

    assert DEFAULT_IMAGE_GEN_ROLE == "fibo"
    router = ImageGenRouter(backend=StubImageGenBackend())
    model_key = router.resolve_model()
    assert isinstance(model_key, str)
    assert model_key, "model key must be non-empty"


def test_router_resolves_all_seven_roles() -> None:
    """All 7 canonical image_gen roles resolve to distinct keys."""
    from tuatha.asset_generation.image_gen import (
        ImageGenRouter,
        StubImageGenBackend,
    )

    router = ImageGenRouter(backend=StubImageGenBackend())
    roles = [
        "flux",
        "z_image",
        "qwen",
        "fibo",
        "sdxl",
        "unsloth_diffusion",
        "unsloth_qwen_image",
    ]
    keys = {router.resolve_model(role) for role in roles}
    # All 7 roles should resolve to a string — and (when the
    # registry is available) to 7 distinct keys.
    assert len(keys) == len(roles), (
        f"Expected 7 distinct image_gen keys, got {len(keys)}: {keys}"
    )


def test_router_generate_passes_resolved_model_to_backend() -> None:
    """`generate()` resolves the model key then passes it to the backend."""
    from tuatha.asset_generation.image_gen import (
        ImageGenRouter,
        StubImageGenBackend,
    )

    fake_backend = MagicMock(spec=StubImageGenBackend)
    fake_backend.generate_image.return_value = {"created": 1, "data": []}

    router = ImageGenRouter(backend=fake_backend)
    router.generate(prompt="celtic-art window chrome", role="fibo")

    fake_backend.generate_image.assert_called_once()
    call_kwargs = fake_backend.generate_image.call_args.kwargs
    assert call_kwargs["prompt"] == "celtic-art window chrome"
    assert call_kwargs["size"] == "1024x1024"
    assert call_kwargs["n"] == 1
    # The router passes `model` as a kwarg.
    model_key = call_kwargs["model"]
    assert isinstance(model_key, str)
    assert model_key, "model key must be non-empty"


def test_router_generate_rejects_empty_prompt() -> None:
    """LBYL: empty / whitespace-only prompts raise ValueError."""
    from tuatha.asset_generation.image_gen import ImageGenRouter, StubImageGenBackend

    router = ImageGenRouter(backend=StubImageGenBackend())

    with pytest.raises(ValueError):
        router.generate(prompt="")

    with pytest.raises(ValueError):
        router.generate(prompt="   ")


def test_router_generate_uses_size_and_n_kwargs() -> None:
    """`size` and `n` are passed through to the backend."""
    from tuatha.asset_generation.image_gen import (
        ImageGenRouter,
        StubImageGenBackend,
    )

    fake_backend = MagicMock(spec=StubImageGenBackend)
    fake_backend.generate_image.return_value = {"created": 1, "data": []}

    router = ImageGenRouter(backend=fake_backend)
    router.generate(prompt="x", role="flux", size="512x512", n=4)

    call_kwargs = fake_backend.generate_image.call_args.kwargs
    assert call_kwargs["size"] == "512x512"
    assert call_kwargs["n"] == 4


def test_router_generate_extra_body_merged() -> None:
    """`extra_body` is forwarded to the backend as-is."""
    from tuatha.asset_generation.image_gen import (
        ImageGenRouter,
        StubImageGenBackend,
    )

    fake_backend = MagicMock(spec=StubImageGenBackend)
    fake_backend.generate_image.return_value = {"created": 1, "data": []}

    router = ImageGenRouter(backend=fake_backend)
    extra = {"seed": 42, "cfg_scale": 7.5}
    router.generate(prompt="x", role="qwen", extra_body=extra)

    call_kwargs = fake_backend.generate_image.call_args.kwargs
    assert call_kwargs["extra_body"] == extra


def test_stub_backend_echoes_request() -> None:
    """The StubImageGenBackend returns a request-shaped echo dict."""
    from tuatha.asset_generation.image_gen import StubImageGenBackend

    backend = StubImageGenBackend()
    result = backend.generate_image(
        model="local/image/test",
        prompt="hello",
        size="256x256",
        n=2,
        extra_body={"seed": 1},
    )
    assert result["created"] == 0
    assert len(result["data"]) == 1
    item = result["data"][0]
    assert item["stub"] is True
    assert item["model"] == "local/image/test"
    assert item["prompt"] == "hello"
    assert item["size"] == "256x256"
    assert item["n"] == 2
    assert item["extra_body"] == {"seed": 1}


def test_router_close_does_not_crash_on_stub_backend() -> None:
    """`close()` is idempotent and safe for the stub backend."""
    from tuatha.asset_generation.image_gen import ImageGenRouter, StubImageGenBackend

    router = ImageGenRouter(backend=StubImageGenBackend())
    router.close()
    router.close()  # idempotent


def test_router_context_manager() -> None:
    """The router works as a context manager."""
    from tuatha.asset_generation.image_gen import (
        ImageGenRouter,
        StubImageGenBackend,
    )

    fake_backend = MagicMock(spec=StubImageGenBackend)
    fake_backend.generate_image.return_value = {"created": 1, "data": []}

    with ImageGenRouter(backend=fake_backend) as router:
        router.generate(prompt="hi", role="sdxl")


# ── UnslothClient tests (with mocked httpx) ──────────────────────────


def test_unsloth_client_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Constructing UnslothClient without UNSLOTH_API_KEY raises."""
    from tuatha.asset_generation.image_gen.unsloth_client import (
        UnslothClient,
        UnslothClientError,
    )

    monkeypatch.delenv("UNSLOTH_API_KEY", raising=False)
    with pytest.raises(UnslothClientError, match="UNSLOTH_API_KEY"):
        UnslothClient()


def test_unsloth_client_passes_authorization_header() -> None:
    """UnslothClient sends Bearer auth in the Authorization header."""
    from tuatha.asset_generation.image_gen.unsloth_client import UnslothClient

    with patch("httpx.Client") as mock_client_cls:
        mock_client_cls.return_value = MagicMock()
        client = UnslothClient(api_key="test-key-123")

    headers = mock_client_cls.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer test-key-123"


def test_unsloth_client_retries_on_5xx_then_succeeds() -> None:
    """5xx → retry; succeed within MAX_RETRIES."""
    from tuatha.asset_generation.image_gen.unsloth_client import (
        IMAGES_ENDPOINT,
        MAX_RETRIES,
        UnslothClient,
    )

    fake_response_500 = MagicMock()
    fake_response_500.status_code = 500
    fake_response_500.text = "boom"
    fake_response_200 = MagicMock()
    fake_response_200.status_code = 200
    fake_response_200.json.return_value = {"created": 1, "data": []}

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        # 2 x 5xx then 1 x 2xx
        mock_client.request.side_effect = [
            fake_response_500,
            fake_response_500,
            fake_response_200,
        ]

        # Stub the sleep helper so the test is instant.
        with patch.object(UnslothClient, "_sleep") as mock_sleep:
            client = UnslothClient(api_key="k")
            result = client.generate_image(
                model="local/image/test",
                prompt="x",
            )

    assert result == {"created": 1, "data": []}
    # 2 retries → 2 sleeps
    assert mock_sleep.call_count == 2
    # 3 HTTP requests total (initial + 2 retries)
    assert mock_client.request.call_count == 3
    # All requests POST to the images endpoint.
    for call in mock_client.request.call_args_list:
        assert call.args[0] == "POST"
        assert call.args[1] == IMAGES_ENDPOINT


def test_unsloth_client_does_not_retry_on_4xx() -> None:
    """4xx → raise immediately, no retry."""
    from tuatha.asset_generation.image_gen.unsloth_client import (
        UnslothClient,
        UnslothClientError,
    )

    fake_response_400 = MagicMock()
    fake_response_400.status_code = 400
    fake_response_400.text = "bad request"

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.request.return_value = fake_response_400

        client = UnslothClient(api_key="k")
        with pytest.raises(UnslothClientError, match="400"):
            client.generate_image(model="local/image/test", prompt="x")

    assert mock_client.request.call_count == 1


def test_unsloth_client_gives_up_after_max_retries_on_5xx() -> None:
    """After MAX_RETRIES retries the client raises UnslothClientError."""
    from tuatha.asset_generation.image_gen.unsloth_client import (
        UnslothClient,
        UnslothClientError,
    )

    fake_response_500 = MagicMock()
    fake_response_500.status_code = 500
    fake_response_500.text = "still broken"

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.request.return_value = fake_response_500

        with patch.object(UnslothClient, "_sleep"):
            client = UnslothClient(api_key="k")
            with pytest.raises(UnslothClientError, match="500"):
                client.generate_image(model="local/image/test", prompt="x")

    # MAX_RETRIES + 1 attempts (initial + retries)
    assert mock_client.request.call_count == UnslothClient(api_key="k", max_retries=3)._max_retries + 1


def test_unsloth_client_retries_on_connection_error_then_succeeds() -> None:
    """ConnectionError → retry; succeed on subsequent attempt."""
    from tuatha.asset_generation.image_gen.unsloth_client import UnslothClient

    fake_response_200 = MagicMock()
    fake_response_200.status_code = 200
    fake_response_200.json.return_value = {"choices": [{"message": {"content": "ok"}}]}

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        # import the httpx symbol used by UnslothClient
        import httpx

        mock_client.request.side_effect = [
            httpx.ConnectError("nope"),
            fake_response_200,
        ]

        with patch.object(UnslothClient, "_sleep"):
            client = UnslothClient(api_key="k")
            result = client.chat_completion(
                model="molmo2-8b",
                messages=[{"role": "user", "content": "hi"}],
            )

    assert result == {"choices": [{"message": {"content": "ok"}}]}


def test_unsloth_client_parse_json_raises_on_non_dict() -> None:
    """A 2xx with a non-dict JSON payload raises UnslothClientError."""
    from tuatha.asset_generation.image_gen.unsloth_client import (
        UnslothClient,
        UnslothClientError,
    )

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = [1, 2, 3]  # list, not dict

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.request.return_value = fake_response

        client = UnslothClient(api_key="k")
        with pytest.raises(UnslothClientError, match="non-dict"):
            client.generate_image(model="local/image/test", prompt="x")


# ── Backend ABC tests ───────────────────────────────────────────────


def test_unsloth_image_gen_backend_uses_provided_client() -> None:
    """UnslothImageGenBackend forwards to the provided UnslothClient."""
    from tuatha.asset_generation.image_gen import UnslothImageGenBackend

    fake_client = MagicMock()
    fake_client.generate_image.return_value = {"ok": True}

    backend = UnslothImageGenBackend(client=fake_client)
    result = backend.generate_image(
        model="x",
        prompt="y",
        size="1024x1024",
        n=1,
        extra_body=None,
    )

    fake_client.generate_image.assert_called_once_with(
        model="x",
        prompt="y",
        size="1024x1024",
        n=1,
        extra_body=None,
    )
    assert result == {"ok": True}


# ── Hard-rule guard: no hardcoded model strings ─────────────────────


def test_no_hardcoded_model_strings_in_router_module() -> None:
    """LBYL: the router module must not contain hardcoded
    `local/image/<name>` literals that bypass the registry.
    """
    from pathlib import Path

    src_path = Path(
        "/Users/cianmacandeisigh/dev/tuatha/tuatha/asset_generation/image_gen/router.py"
    )
    text = src_path.read_text()

    # The STUB_MODEL_KEY is allowed (it's the offline fallback).
    # Any other `local/image/<literal>` would indicate a
    # hardcoded model string.
    assert text.count('"local/image/') <= 1, (
        f"router.py should only define STUB_MODEL_KEY, not hardcoded "
        f"local/image/<name> strings. Found {text.count(chr(34) + 'local/image/')} occurrences."
    )


def test_resolve_model_returns_string_for_every_role() -> None:
    """Even when the registry is missing, every role returns a string."""
    from tuatha.asset_generation.image_gen import (
        ImageGenRouter,
        StubImageGenBackend,
    )

    router = ImageGenRouter(backend=StubImageGenBackend())
    # Patch model_for to None to simulate offline mode
    with patch(
        "tuatha.asset_generation.image_gen.router.model_for", None
    ):
        for role in ("flux", "z_image", "qwen", "fibo", "sdxl",
                     "unsloth_diffusion", "unsloth_qwen_image"):
            key = router.resolve_model(role)
            assert isinstance(key, str)
            assert key
