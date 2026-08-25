"""tuatha.badges.mint — the BadgeMintService (queries baml_extractions + emits rung-5-complete badges)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class MintStub:
    name: str = "mint"
    def __init__(self, *args: Any, **kwargs: Any) -> None: pass


__all__ = ["MintStub"]
