"""tuatha.models — the model resolution surface for the tuatha project.

tuatha does not carry a copy of the cianfhoghlaim 20-entry
`VISION_MODELS` catalogue. It declares only the roles it actually
consumes and resolves them to concrete model ids. See
`tuatha/corpus/CONTRACT.md` for the repo boundary this enforces.
"""

from .registry import (
    ROLES,
    ModelRole,
    resolve,
    vision_env,
)

__all__ = ["ROLES", "ModelRole", "resolve", "vision_env"]
