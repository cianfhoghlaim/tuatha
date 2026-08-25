"""tuatha.asset_generation.vlm — the multi-model VLM analysis surface.

The third layer of the 3-layer asset-generation facade
(image_gen / fibo / vlm):

- `vlm/` (this subpackage) — the multi-model VLM router for
  document / syllabus image analysis. Routes the 3 canonical
  VLM entries (molmo2-8b, qwen3-vl-8b-instruct,
  olmOCR-2-7B-1025) via their canonical roles
  (`specialist`, `default`, `specialist`). Task-level logical
  roles (`diagram_pointing`, `page_image`) are mapped onto
  the registry roles.

Per the centralized-model-registry contract: every model choice
routes through `MODEL_REGISTRY.resolve(family, role)` — no
hardcoded model strings.
"""
from __future__ import annotations

from tuatha.asset_generation.vlm.router import (
    DEFAULT_VLM_ROLE,
    DIAGRAM_POINTING_ROLE,
    PAGE_IMAGE_ROLE,
    SPECIALIST_VLM_ROLE,
    STUB_VLM_MODEL_KEY,
    StubVlmBackend,
    UnslothVlmBackend,
    VlmBackend,
    VlmRouter,
)

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
