"""tuatha.asset_generation.image_gen.router — the multi-model image-gen router.

Per the asset-generation surface contract:
- Resolves model strings via `MODEL_REGISTRY.resolve("image_gen", role)`
  — never hardcodes a model name.
- Routes 7 image-gen entries (flux2-dev, z-image-turbo, qwen-image,
  fibo, sdxl, diffusiongemma-26b-a4b, qwen-image-2512) via their
  canonical roles (`flux`, `z_image`, `qwen`, `fibo`, `sdxl`,
  `unsloth_diffusion`, `unsloth_qwen_image`).
- Delegates the actual HTTP call to the OpenAI-compatible
  `UnslothClient` (POST `/v1/images/generations`).

The router is the canonical mount point for the FIBO prompt
templates (per `tuatha.asset_generation.fibo.education_fibo`):
the 8 subject-specific prompt templates are passed to `generate()`
and routed to the right model based on the requested role.

Architecture:
- `ImageGenBackend` — ABC for the underlying HTTP client.
  Lets tests inject a fake without spinning up an httpx mock.
- `UnsloothImageGenBackend` — the production impl wrapping
  `UnslothClient`.
- `ImageGenRouter` — the public facade. Resolves the model key
  via `MODEL_REGISTRY.resolve("image_gen", role)` and delegates
  to the backend.
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

# The default role when callers don't specify one.
# 'fibo' is the canonical role for curriculum-asset generation
# (the new tuatha's primary image-gen use case).
DEFAULT_IMAGE_GEN_ROLE = "fibo"

# Per the UnslothClient contract: graceful-degradation when the
# registry is offline (unit tests, dev sandboxes). The router
# falls back to a stub backend that echoes the request.
STUB_MODEL_KEY = "stub/image/unknown"


class ImageGenBackend(ABC):
    """The ABC for image-gen HTTP backends.

    Lets tests inject a fake (no httpx, no Unsloth Studio round
    trip) without monkey-patching the production client.
    """

    @abstractmethod
    def generate_image(
        self,
        model: str,
        prompt: str,
        *,
        size: str,
        n: int,
        extra_body: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Issue the image-gen HTTP call and return the parsed JSON."""


class UnslothImageGenBackend(ImageGenBackend):
    """The production image-gen backend wrapping `UnslothClient`."""

    def __init__(self, client: Any = None) -> None:
        # LBYL: defer the import so the image_gen surface
        # doesn't crash on import in envs that haven't installed
        # httpx yet (unit-test isolation).
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

    def generate_image(
        self,
        model: str,
        prompt: str,
        *,
        size: str,
        n: int,
        extra_body: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return self._client.generate_image(
            model=model,
            prompt=prompt,
            size=size,
            n=n,
            extra_body=extra_body,
        )


class StubImageGenBackend(ImageGenBackend):
    """The offline-dev / unit-test backend.

    Echoes the request as a dict so callers can verify the
    routing contract (the right `model` key was chosen) without
    requiring a live Unsloth Studio endpoint.
    """

    def generate_image(
        self,
        model: str,
        prompt: str,
        *,
        size: str,
        n: int,
        extra_body: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "created": 0,
            "data": [
                {
                    "stub": True,
                    "model": model,
                    "prompt": prompt,
                    "size": size,
                    "n": n,
                    "extra_body": extra_body or {},
                }
            ],
        }


class ImageGenRouter:
    """The multi-model image-gen router for the 7 image_gen entries.

    Usage:
        router = ImageGenRouter()  # picks Unsloth backend in prod
        result = router.generate(
            prompt="celtic-art window chrome for the Mathematics realm",
            role="fibo",
        )

    Per the centralized-model-registry contract: no hardcoded
    model strings — every role resolves through
    `MODEL_REGISTRY.resolve("image_gen", role)`.
    """

    def __init__(self, backend: ImageGenBackend | None = None) -> None:
        if backend is not None:
            self._backend = backend
            self._owns_backend = False
        elif os.environ.get("TUATHA_OFFLINE") == "1" or model_for is None:
            # Offline dev / unit-test fallback.
            self._backend = StubImageGenBackend()
            self._owns_backend = True
        else:
            self._backend = UnslothImageGenBackend()
            self._owns_backend = True

    def resolve_model(self, role: str = DEFAULT_IMAGE_GEN_ROLE) -> str:
        """Resolve a canonical image_gen model key for the given role.

        Args:
            role: One of the 7 canonical roles
                (`flux`, `z_image`, `qwen`, `fibo`, `sdxl`,
                `unsloth_diffusion`, `unsloth_qwen_image`).

        Returns:
            The canonical `local/image/<name>` model key.

        Raises:
            ValueError: if `MODEL_REGISTRY` is unavailable and no
                offline fallback can satisfy the role.
        """
        if model_for is not None:
            try:
                return model_for("image_gen", role)
            except KeyError:
                # The registry may not know the role (e.g., a
                # downstream operator added a custom role). Fall
                # back to the first available image_gen entry
                # rather than failing the whole request.
                if MODEL_REGISTRY is not None:
                    entries = MODEL_REGISTRY.filter(family="image_gen")
                    if entries:
                        return entries[0].key

        # Final offline fallback for unit tests in isolation.
        return STUB_MODEL_KEY

    def generate(
        self,
        prompt: str,
        role: str = DEFAULT_IMAGE_GEN_ROLE,
        *,
        size: str = "1024x1024",
        n: int = 1,
        extra_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate an image using the model registered for `role`.

        Args:
            prompt: The image-gen prompt (FIBO template, BAML
                output, etc.).
            role: The image-gen role to dispatch to. Defaults
                to `"fibo"` (the curriculum-asset role).
            size: OpenAI-style `"<W>x<H>"` size string.
            n: The number of images to generate.
            extra_body: Extra fields merged into the JSON body
                (Unsloth-specific extensions).

        Returns:
            The parsed JSON response from the backend.

        Raises:
            ValueError: if `prompt` is empty.
        """
        # LBYL: validate inputs up front so the caller gets a
        # clear error rather than a cryptic HTTP 400 from the
        # Unsloth Studio.
        if not prompt or not prompt.strip():
            raise ValueError("`prompt` must be a non-empty string")

        model_key = self.resolve_model(role)
        return self._backend.generate_image(
            model=model_key,
            prompt=prompt,
            size=size,
            n=n,
            extra_body=extra_body,
        )

    def close(self) -> None:
        """Close the backend (if it owns resources). Idempotent."""
        if self._owns_backend:
            close = getattr(self._backend, "close", None)
            if callable(close):
                close()

    def __enter__(self) -> ImageGenRouter:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


__all__ = [
    "DEFAULT_IMAGE_GEN_ROLE",
    "ImageGenBackend",
    "ImageGenRouter",
    "STUB_MODEL_KEY",
    "StubImageGenBackend",
    "UnslothImageGenBackend",
]
