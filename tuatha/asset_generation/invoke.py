"""FIBO + TRELLIS.2 + SAM-3D-Objects asset invocation client.

Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md
T7.3 (3D meshes) + T7.15 (FIBO PNGs) + T7.17 (SVG icons).

Invokes the canonical VLM backbone (Bolmo / Molmo2 / Qwen3-VL) + the
FIBO API + TRELLIS.2-4B + SAM-3D-Objects for the 8 NCCA subject
asset generation. The output lands at s3://cianfhoghlaim-asset-v2/{3d,2d}/{subject}/.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

try:
    from cianfhoghlaim.tuatha.asset_generation.fibo import education_fibo
    FIBO_AVAILABLE = True
except ImportError:
    FIBO_AVAILABLE = False
    education_fibo = None


# The 24-entry OCR/VLM registry (cianfhoghlaim.meaisinfhoghlaim.models.registry)
try:
    from cianfhoghlaim.meaisinfhoghlaim.models.registry import VISION_MODELS, get_optimal_for_m4
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    VISION_MODELS = None
    get_optimal_for_m4 = None


# ── Phase 1 P1+P7: the 3-layer asset-generation facade ──────────
# Re-export the new image_gen + vlm surfaces (the FIBO surface is
# the existing `education_fibo` above). These imports are
# deliberately wrapped in try/except so this module keeps working
# in envs that haven't installed the new subpackages yet
# (graceful-degradation per the centralized-model-registry
# contract).
try:
    from tuatha.asset_generation.image_gen import (  # type: ignore[import-not-found]
        DEFAULT_IMAGE_GEN_ROLE,
        ImageGenRouter,
        STUB_MODEL_KEY,
        StubImageGenBackend,
        UnslothClient,
        UnslothClientError,
        UnslothImageGenBackend,
    )
    IMAGE_GEN_AVAILABLE = True
except ImportError:
    IMAGE_GEN_AVAILABLE = False
    ImageGenRouter = None  # type: ignore[assignment, misc]
    StubImageGenBackend = None  # type: ignore[assignment, misc]
    UnslothImageGenBackend = None  # type: ignore[assignment, misc]
    UnslothClient = None  # type: ignore[assignment, misc]
    UnslothClientError = None  # type: ignore[assignment, misc]
    DEFAULT_IMAGE_GEN_ROLE = "fibo"  # type: ignore[assignment, misc]
    STUB_MODEL_KEY = "stub/image/unknown"  # type: ignore[assignment, misc]


try:
    from tuatha.asset_generation.vlm import (  # type: ignore[import-not-found]
        DEFAULT_VLM_ROLE,
        DIAGRAM_POINTING_ROLE,
        PAGE_IMAGE_ROLE,
        SPECIALIST_VLM_ROLE,
        STUB_VLM_MODEL_KEY,
        StubVlmBackend,
        UnslothVlmBackend,
        VlmRouter,
    )
    VLM_AVAILABLE = True
except ImportError:
    VLM_AVAILABLE = False
    VlmRouter = None  # type: ignore[assignment, misc]
    StubVlmBackend = None  # type: ignore[assignment, misc]
    UnslothVlmBackend = None  # type: ignore[assignment, misc]
    DEFAULT_VLM_ROLE = "default"  # type: ignore[assignment, misc]
    DIAGRAM_POINTING_ROLE = "diagram_pointing"  # type: ignore[assignment, misc]
    PAGE_IMAGE_ROLE = "page_image"  # type: ignore[assignment, misc]
    SPECIALIST_VLM_ROLE = "specialist"  # type: ignore[assignment, misc]
    STUB_VLM_MODEL_KEY = "stub/vlm/unknown"  # type: ignore[assignment, misc]


# The 8 NCCA subjects
NCCA_SUBJECTS = (
    "mathematics",
    "applied_mathematics",
    "chemistry",
    "geography",
    "history",
    "english",
    "gaeilge",
    "computer_science",
)


async def generate_2d_sprite_atlas(subject: str, language: str = "en") -> dict[str, Any]:
    """Generate the 2D sprite atlas for the subject via FIBO.

    The sprite atlas is the headless render of the 3D scene at multiple
    angles, per the Hades dual-mode pipeline (per docs/BROWN_AJAH_THEMING.md).
    """
    if not FIBO_AVAILABLE:
        return {"error": "FIBO not available", "subject": subject}

    template = education_fibo.get_fibo_prompt(subject, language=language)

    # TODO: call the FIBO API via InvokeAI or BFL FIBO directly
    # The prompt is `template["prompt"]` — we use the LiteLLM gateway
    # to invoke the FIBO model (per the LiteLLM config at
    # cianfhoghlaim.meaisinfhoghlaim.litellm_config)

    return {
        "status": "queued",
        "subject": subject,
        "language": language,
        "tuatha_de_deity": template["tuatha_de_deity"],
        "tuatha_de_treasure": template["tuatha_de_treasure"],
        "game_ui_inspiration": template["game_ui_inspiration"],
        "estimated_minutes": 5,
        "output": f"s3://cianfhoghlaim-asset-v2/2d/{subject}/{language}.png",
    }


async def generate_3d_mesh(subject: str, prompt: str = "") -> dict[str, Any]:
    """Generate the 3D mesh via TRELLIS.2 + SAM-3D-Objects.

    The output is a GLB file uploaded to s3://cianfhoghlaim-asset-v2/3d/{subject}/.
    Per the 5-stage DAG flow: VLM prompt generation → SAM3 sprite
    segmentation → TRELLIS.2 mesh generation → R2 upload.
    """
    if not FIBO_AVAILABLE:
        return {"error": "FIBO not available", "subject": subject}

    template = education_fibo.get_fibo_prompt(subject, language="en")

    # TODO: chain:
    # 1. VLM prompt refinement via Qwen3-VL (Bolmo / Molmo2 fallback)
    # 2. SAM3 sprite segmentation via the sam3-server stack
    # 3. TRELLIS.2-4B mesh generation via the trellis-server stack
    # 4. R2 upload via the Garage S3 stack
    # 5. Convex skill_assets record

    return {
        "status": "queued",
        "subject": subject,
        "prompt": prompt or template["prompt"],
        "tuatha_de_deity": template["tuatha_de_deity"],
        "estimated_minutes": 12,
        "output_glb": f"s3://cianfhoghlaim-asset-v2/3d/{subject}/{prompt[:32].replace(' ', '_') or 'default'}.glb",
    }


async def generate_subkey_competency_emblem(key_competency: str) -> dict[str, Any]:
    """Generate the 5 NCCA Key Competencies emblems via FIBO.

    Per docs/BROWN_AJAH_THEMING.md, the 5 NCCA Key Competencies are the
    5 surviving gifts of the Tuatha Dé Danann. The emblems are the
    visual representation of each gift.
    """
    # TODO: call FIBO with the 5 Trí Dé Dána + Lugh motifs
    return {
        "status": "queued",
        "key_competency": key_competency,
        "estimated_minutes": 2,
        "output": f"s3://cianfhoghlaim-asset-v2/2d/insights/{key_competency}.svg",
    }


def select_optimal_vlm_model(task: str) -> dict[str, Any]:
    """Select the optimal VLM model from the 24-entry OCR/VLM registry.

    Per the model selection logic in
    `cianfhoghlaim.meaisinfhoghlaim.models.registry.get_optimal_for_m4`.
    """
    if not REGISTRY_AVAILABLE or get_optimal_for_m4 is None:
        return {"error": "Registry not available"}

    # TODO: select the optimal model based on the task type
    return {
        "task": task,
        "registry_entries": len(VISION_MODELS) if VISION_MODELS else 0,
    }


# ── Phase 1 P1+P7: the 3-layer facade re-exports ────────────────
# The 3 layers are: image_gen / fibo / vlm. Callers can use them
# directly OR via the helper functions below. The existing 5 FIBO
# functions (`generate_2d_sprite_atlas`, `generate_3d_mesh`, etc.)
# are preserved verbatim above.

__all__ = [
    # Layer 1: image_gen (new)
    "DEFAULT_IMAGE_GEN_ROLE",
    "ImageGenRouter",
    "IMAGE_GEN_AVAILABLE",
    "STUB_MODEL_KEY",
    "StubImageGenBackend",
    "UnslothClient",
    "UnslothClientError",
    "UnslothImageGenBackend",
    # Layer 2: fibo (existing)
    "FIBO_AVAILABLE",
    # Layer 3: vlm (new)
    "DEFAULT_VLM_ROLE",
    "DIAGRAM_POINTING_ROLE",
    "PAGE_IMAGE_ROLE",
    "SPECIALIST_VLM_ROLE",
    "STUB_VLM_MODEL_KEY",
    "StubVlmBackend",
    "UnslothVlmBackend",
    "VLM_AVAILABLE",
    "VlmRouter",
    # Existing public symbols
    "NCCA_SUBJECTS",
    "REGISTRY_AVAILABLE",
    "generate_2d_sprite_atlas",
    "generate_3d_mesh",
    "generate_subkey_competency_emblem",
    "select_optimal_vlm_model",
]