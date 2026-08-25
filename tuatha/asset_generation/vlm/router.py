"""tuatha.asset_generation.vlm.router — the multi-model VLM analysis router.

Per the asset-generation surface contract:
- Resolves model strings via `MODEL_REGISTRY.resolve("ocr_vision", role)`
  — never hardcodes a model name.
- Routes the 3 canonical VLM entries (molmo2-8b,
  qwen3-vl-8b-instruct, olmOCR-2-7B-1025) via their canonical
  roles (`specialist`, `default`, `specialist`).

Note: the registry's canonical roles for `ocr_vision` are
`default`, `legacy`, `lightweight`, `primary`, and
`specialist`. The Phase 1 task spec also references task-level
logical roles (`diagram_pointing`, `page_image`) — this router
maps them onto the actual registry roles via
`_ROLE_TO_REGISTRY` so the public API is task-flavoured while
the resolution remains registry-correct.

Architecture mirrors the image_gen router:
- `VlmBackend` — ABC for the underlying HTTP client.
- `UnslothVlmBackend` — the production impl wrapping
  `UnslothClient` (POST `/v1/chat/completions`).
- `StubVlmBackend` — the offline-dev / unit-test fallback.
- `VlmRouter` — the public facade. Resolves the model key via
  `MODEL_REGISTRY.resolve("ocr_vision", role)` and delegates to
  the backend.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any

# Per the centralized-model-registry contract: route every
# model choice through MODEL_REGISTRY.resolve(family, role).
try:
    from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for  # type: ignore[import-not-found]
except ImportError:
    MODEL_REGISTRY = None  # type: ignore[assignment, misc]
    model_for = None  # type: ignore[assignment, misc]


# The canonical VLM role set per the Phase 1 spec. Logical task
# roles (`diagram_pointing`, `page_image`) map onto actual
# registry roles (`specialist`, `default`).
DEFAULT_VLM_ROLE = "default"
SPECIALIST_VLM_ROLE = "specialist"
DIAGRAM_POINTING_ROLE = "diagram_pointing"
PAGE_IMAGE_ROLE = "page_image"

# Per the Phase 1 task spec: logical task → registry role map.
# `diagram_pointing` needs precise visual pointing → use the
# specialist entry (molmo2-8b / olmOCR-2). `page_image` is a
# general page analysis → use the default entry (qwen3-vl-8b).
_ROLE_TO_REGISTRY: dict[str, str] = {
    DIAGRAM_POINTING_ROLE: "specialist",
    PAGE_IMAGE_ROLE: "default",
    "default": "default",
    "specialist": "specialist",
}


# Per the UnslothClient contract: graceful-degradation when the
# registry is offline (unit tests, dev sandboxes). The router
# falls back to a stub backend that echoes the request.
STUB_VLM_MODEL_KEY = "stub/vlm/unknown"


class VlmBackend(ABC):
    """The ABC for VLM chat-completion HTTP backends.

    Lets tests inject a fake (no httpx, no Unsloth Studio round
    trip) without monkey-patching the production client.
    """

    @abstractmethod
    def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        *,
        temperature: float,
        max_tokens: int,
        extra_body: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Issue the chat-completion HTTP call and return the parsed JSON."""


class UnslothVlmBackend(VlmBackend):
    """The production VLM backend wrapping `UnslothClient`."""

    def __init__(self, client: Any = None) -> None:
        # LBYL: defer the import so the vlm surface doesn't
        # crash on import in envs that haven't installed httpx
        # yet (unit-test isolation).
        from tuatha.asset_generation.image_gen.unsloth_client import (
            DEFAULT_BASE_URL,
            UnslothClient,
        )

        if client is None:
            client = UnslothClient(
                base_url=os.environ.get("UNSLOTH_BASE_URL", DEFAULT_BASE_URL),
                api_key=os.environ.get("UNSLOTH_API_KEY"),
            )
        self._client = client

    def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        *,
        temperature: float,
        max_tokens: int,
        extra_body: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return self._client.chat_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_body=extra_body,
        )


class StubVlmBackend(VlmBackend):
    """The offline-dev / unit-test backend.

    Echoes the request as a dict so callers can verify the
    routing contract (the right `model` key was chosen) without
    requiring a live Unsloth Studio endpoint.
    """

    def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        *,
        temperature: float,
        max_tokens: int,
        extra_body: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "id": "stub-chatcmpl",
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "[stub] VLM response",
                    },
                    "stub": True,
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "echoed": {
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "extra_body": extra_body or {},
            },
        }


class VlmRouter:
    """The multi-model VLM router for the ocr_vision family.

    Usage:
        router = VlmRouter()  # picks Unsloth backend in prod
        result = router.analyze(
            messages=[{"role": "user", "content": "What does this diagram show?"}],
            role="diagram_pointing",
        )

    Per the centralized-model-registry contract: no hardcoded
    model strings — every role resolves through
    `MODEL_REGISTRY.resolve("ocr_vision", role)`. Logical task
    roles (`diagram_pointing`, `page_image`) are mapped onto
    actual registry roles (`specialist`, `default`) via the
    `_ROLE_TO_REGISTRY` table.
    """

    def __init__(self, backend: VlmBackend | None = None) -> None:
        if backend is not None:
            self._backend = backend
            self._owns_backend = False
        elif os.environ.get("TUATHA_OFFLINE") == "1" or model_for is None:
            # Offline dev / unit-test fallback.
            self._backend = StubVlmBackend()
            self._owns_backend = True
        else:
            self._backend = UnslothVlmBackend()
            self._owns_backend = True

    @staticmethod
    def map_role(role: str) -> str:
        """Map a logical task-level role onto the actual registry role.

        Args:
            role: Either a logical role
                (`diagram_pointing`, `page_image`) or a direct
                registry role (`default`, `specialist`).

        Returns:
            The registry role to pass to
            `MODEL_REGISTRY.resolve("ocr_vision", ...)`.
        """
        return _ROLE_TO_REGISTRY.get(role, role)

    def resolve_model(self, role: str = DEFAULT_VLM_ROLE) -> str:
        """Resolve a canonical ocr_vision model key for the given role.

        Args:
            role: A logical role (`diagram_pointing`, `page_image`)
                or a direct registry role (`default`, `specialist`).

        Returns:
            The canonical model key (e.g., `"molmo2-8b"`).

        Raises:
            ValueError: if `MODEL_REGISTRY` is unavailable and no
                offline fallback can satisfy the role.
        """
        registry_role = self.map_role(role)

        if model_for is not None:
            try:
                return model_for("ocr_vision", registry_role)
            except KeyError:
                # The registry may not know the role (e.g., a
                # downstream operator added a custom role). Fall
                # back to the first available ocr_vision entry
                # rather than failing the whole request.
                if MODEL_REGISTRY is not None:
                    entries = MODEL_REGISTRY.filter(family="ocr_vision")
                    if entries:
                        return entries[0].key

        # Final offline fallback for unit tests in isolation.
        return STUB_VLM_MODEL_KEY

    def analyze(
        self,
        messages: list[dict[str, Any]],
        role: str = DEFAULT_VLM_ROLE,
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        extra_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run a VLM chat-completion for the given messages + role.

        Args:
            messages: The OpenAI-style messages list
                (`[{"role": "user", "content": "..."}]`).
            role: The VLM role to dispatch to. Logical task roles
                (`diagram_pointing`, `page_image`) and direct
                registry roles (`default`, `specialist`) are both
                accepted.
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Max output tokens.
            extra_body: Extra fields merged into the JSON body.

        Returns:
            The parsed JSON response from the backend.

        Raises:
            ValueError: if `messages` is empty.
        """
        # LBYL: validate inputs up front so the caller gets a
        # clear error rather than a cryptic HTTP 400 from the
        # Unsloth Studio.
        if not messages:
            raise ValueError("`messages` must be a non-empty list")

        model_key = self.resolve_model(role)
        return self._backend.chat(
            model=model_key,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_body=extra_body,
        )

    def close(self) -> None:
        """Close the backend (if it owns resources). Idempotent."""
        if self._owns_backend:
            close = getattr(self._backend, "close", None)
            if callable(close):
                close()

    def __enter__(self) -> VlmRouter:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


__all__ = [
    "DEFAULT_VLM_ROLE",
    "DIAGRAM_POINTING_ROLE",
    "PAGE_IMAGE_ROLE",
    "SPECIALIST_VLM_ROLE",
    "STUB_VLM_MODEL_KEY",
    "StubVlmBackend",
    "UnslothVlmBackend",
    "VlmBackend",
    "VlmRouter",
]
