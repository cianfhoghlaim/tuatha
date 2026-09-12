"""tuatha.models.registry — role-based model resolution.

Why this exists
---------------
The canonical 20-entry `VISION_MODELS` catalogue lives in
cianfhoghlaim (`meaisinfhoghlaim/models/registry.py`). tuatha is a
separate checkout and must not import across the repo boundary, but
it also must not fork a 1000-line catalogue it does not own.

So tuatha declares the *roles* it consumes and the default model id
for each. Every role is overridable by environment variable, which
is how a cianfhoghlaim-hosted deployment injects the authoritative
registry resolution without tuatha ever importing it.

Resolution order for a role:

1. the role's explicit env var (e.g. ``VISION_MODEL_HADES``)
2. the family-wide env var (e.g. ``TUATHA_VISION_MODEL``)
3. the declared default below

The declared defaults follow the same
``unsloth_id > mlx_id > upstream_id`` preference the cianfhoghlaim
registry uses for the M4 Max target.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

__all__ = ["ROLES", "ModelRole", "resolve", "vision_env"]


@dataclass(frozen=True)
class ModelRole:
    """One model role that tuatha consumes.

    Attributes:
        key: the role name, e.g. ``"hades_boon"``.
        family: ``"ocr_vision"`` or ``"text_llm"``.
        tier: the cianfhoghlaim registry tier this role maps to.
        default: the model id used when no env override is present.
        env_var: the role-specific override variable.
        why: what the role is for, so the choice is auditable.
    """

    key: str
    family: str
    tier: str
    default: str
    env_var: str
    why: str


#: Family-wide override variables, consulted after the role-specific one.
_FAMILY_ENV: dict[str, str] = {
    "ocr_vision": "TUATHA_VISION_MODEL",
    "text_llm": "TUATHA_TEXT_MODEL",
}


ROLES: dict[str, ModelRole] = {
    "hades_boon": ModelRole(
        key="hades_boon",
        family="ocr_vision",
        tier="tier2_medium",
        default="unsloth/Qwen3-VL-8B-Instruct-GGUF",
        env_var="VISION_MODEL_HADES",
        why=(
            "Boon icons occupy <5% of a 1080p frame and carry dense "
            "overlaid text; needs the medium tier, not the light one."
        ),
    ),
    "comic_particle": ModelRole(
        key="comic_particle",
        family="ocr_vision",
        tier="tier2_medium",
        default="unsloth/Qwen3-VL-8B-Instruct-GGUF",
        env_var="VISION_MODEL_COMIC",
        why=(
            "Panel-level particle description needs colour fidelity and "
            "motion vocabulary across a full comic page."
        ),
    ),
    "gba_magic": ModelRole(
        key="gba_magic",
        family="ocr_vision",
        tier="tier3_light",
        default="unsloth/gemma-4-E2B-it-GGUF",
        env_var="VISION_MODEL_GBA",
        why=(
            "GBA framebuffers are 240x160. The light tier is sufficient "
            "and keeps headless emulator sweeps cheap."
        ),
    ),
    "subject_agent": ModelRole(
        key="subject_agent",
        family="text_llm",
        tier="default",
        default="minimax",
        env_var="TEXT_MODEL_SUBJECT_AGENT",
        why=(
            "The NCCA subject agents reason over corpus text that has "
            "already been extracted. They previously resolved an "
            "ocr_vision model, which is the wrong family for a "
            "text-in / text-out router."
        ),
    ),
    "educational_agent": ModelRole(
        key="educational_agent",
        family="text_llm",
        tier="default",
        default="minimax",
        env_var="TEXT_MODEL_EDUCATIONAL_AGENT",
        why=(
            "The academic-history and Celtic grammar/morphology agents. "
            "Separate from subject_agent so the Celtic-language work can "
            "be pointed at an Irish-tuned model without moving the rest."
        ),
    ),
    "hackathon_agent": ModelRole(
        key="hackathon_agent",
        family="text_llm",
        tier="default",
        default="minimax",
        env_var="TEXT_MODEL_HACKATHON_AGENT",
        why=(
            "The four BIEP features (marking grader, adaptive tutor, "
            "equivalency generator, curriculum change sensor)."
        ),
    ),
    "anam_map": ModelRole(
        key="anam_map",
        family="text_llm",
        tier="default",
        default="minimax",
        env_var="TEXT_MODEL_DEFAULT",
        why=(
            "Source-to-ANAM mapping is text-to-text over already "
            "extracted descriptors; routed through the LiteLLM alias."
        ),
    ),
}


def resolve(role: str) -> str:
    """Resolve a role name to a concrete model id.

    Args:
        role: a key of :data:`ROLES`.

    Returns:
        The model id to pass to the inference gateway.

    Raises:
        KeyError: if ``role`` is not a declared role. The message
            lists the valid roles, because a silent fallback to some
            default model is worse than a loud failure.
    """
    try:
        spec = ROLES[role]
    except KeyError:
        raise KeyError(
            f"Unknown model role {role!r}. Declared roles: {sorted(ROLES)}. "
            "Add it to tuatha.models.registry.ROLES rather than hardcoding "
            "a model string at the call site."
        ) from None

    override = os.environ.get(spec.env_var)
    if override:
        return override

    family_override = os.environ.get(_FAMILY_ENV.get(spec.family, ""))
    if family_override:
        return family_override

    return spec.default


def vision_env() -> dict[str, str]:
    """Return the env mapping the BAML clients read.

    The ANAM BAML clients (``HadesBoonClient``, ``ComicParticleClient``,
    ``GbaMagicClient``, ``AnamMapClient``) take their ``model_name``
    from environment variables rather than literals. This builds that
    mapping so a caller can export it before invoking BAML.
    """
    return {spec.env_var: resolve(name) for name, spec in ROLES.items()}
