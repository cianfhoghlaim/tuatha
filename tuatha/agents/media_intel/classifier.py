"""tuatha.agents.media_intel.classifier — the per-medium classifier (NEW).

Routes a `MediaDescriptor` record to the correct BAML extractor
function (comic / prose / animation / gameplay / official_document)
based on the `medium` field + the BAML-extracted features.

Per the BUILD_PLAN.md this is one of the 2 new media_intel
files added by the consolidation change.
"""
from __future__ import annotations

from typing import Any


def classify_medium(media_descriptor: dict[str, Any]) -> str:
    """Classify a `MediaDescriptor` record to its BAML extractor
    function name.

    This is pure dispatch with no I/O. It was declared ``async`` and
    never awaited, so callers received a coroutine object rather than a
    string — the reason ``test_classify_medium`` was failing.

    Returns one of:

    - 'comic_descriptor' (for comic / graphic novel)
    - 'prose_descriptor' (for novel / story / essay)
    - 'animation_descriptor' (for animation / cartoon)
    - 'gameplay_descriptor' (for game screenshot + session log)
    - 'official_document_descriptor' (for government / syllabus)
    """
    medium = media_descriptor.get("medium", "").lower()
    if medium in ("comic", "graphic_novel"):
        return "comic_descriptor"
    if medium in ("prose", "novel", "story", "essay"):
        return "prose_descriptor"
    if medium in ("animation", "cartoon", "film"):
        return "animation_descriptor"
    if medium in ("game", "gameplay", "screenshot"):
        return "gameplay_descriptor"
    if medium in ("official", "document", "syllabus"):
        return "official_document_descriptor"
    # Default fallback
    return "official_document_descriptor"


__all__ = ["classify_medium"]
