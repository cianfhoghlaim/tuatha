"""tuatha.asset_generation.image_gen — the multi-model image-gen surface.

The 3-layer asset-generation facade (image_gen / fibo / vlm):

- `image_gen/` (this subpackage) — the multi-model image-gen
  router + the OpenAI-compatible Unsloth Studio HTTP client.
  Routes the 7 image_gen entries (flux2-dev, z-image-turbo,
  qwen-image, fibo, sdxl, diffusiongemma-26b-a4b,
  qwen-image-2512) via their canonical roles.

- `fibo/` (sibling subpackage) — the 8 NCCA subject FIBO
  prompt templates + the FIBO asset factory.

- `vlm/` (sibling subpackage) — the multi-model VLM router for
  document / syllabus image analysis.

Per the centralized-model-registry contract: every model choice
routes through `MODEL_REGISTRY.resolve(family, role)` — no
hardcoded model strings.
"""
from __future__ import annotations

from tuatha.asset_generation.image_gen.router import (
    DEFAULT_IMAGE_GEN_ROLE,
    ImageGenBackend,
    ImageGenRouter,
    STUB_MODEL_KEY,
    StubImageGenBackend,
    UnslothImageGenBackend,
)
from tuatha.asset_generation.image_gen.unsloth_client import (
    CHAT_ENDPOINT,
    DEFAULT_BASE_URL,
    IMAGES_ENDPOINT,
    MAX_RETRIES,
    UnslothClient,
    UnslothClientError,
)

__all__ = [
    # Image-gen router
    "DEFAULT_IMAGE_GEN_ROLE",
    "ImageGenBackend",
    "ImageGenRouter",
    "STUB_MODEL_KEY",
    "StubImageGenBackend",
    "UnslothImageGenBackend",
    # Unsloth client
    "CHAT_ENDPOINT",
    "DEFAULT_BASE_URL",
    "IMAGES_ENDPOINT",
    "MAX_RETRIES",
    "UnslothClient",
    "UnslothClientError",
]
