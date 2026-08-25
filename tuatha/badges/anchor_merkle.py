"""tuatha.badges.anchor_merkle — the MerkleAnchorService (computes the rung-5 root across all (subject, language, sha256) tuples)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class AnchorMerkleStub:
    name: str = "anchor_merkle"
    def __init__(self, *args: Any, **kwargs: Any) -> None: pass


__all__ = ["AnchorMerkleStub"]
