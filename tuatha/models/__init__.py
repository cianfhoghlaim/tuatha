"""tuatha.models — the per-project model role resolver.

Re-exports the 7-role ModelRole dataclass + ROLES dict from
`tuatha.models.registry` for callers who use the
`from tuatha.models import ROLES` pattern.

Per the centralized-registry contract: the canonical resolver
is `MODEL_REGISTRY.resolve(family, role)` in
`meaisinfhoghlaim/models/model_registry.py`. This per-project
registry is the offline dev fallback when the parent package
is not importable.
"""

from __future__ import annotations

try:
    from .registry import ROLES, ModelRole, resolve, vision_env  # type: ignore

    __all__ = ["ROLES", "ModelRole", "resolve", "vision_env"]
except ImportError:
    # Graceful degradation for unit tests in isolation.
    ROLES = {}
    ModelRole = None  # type: ignore
    resolve = None  # type: ignore
    vision_env = None  # type: ignore

    __all__ = ["ROLES", "ModelRole", "resolve", "vision_env"]
