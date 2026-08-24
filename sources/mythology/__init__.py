"""tuatha/sources/mythology — Celtic mythology query surface (Ireland + Wales + Scotland).

Re-derives the real lancedb + pydantic tool from cianfhoghlaim
(per the wholesale-copy convention). The previous session's
claim of '9 stub sources' was incorrect — this is the actual file.
"""
from tuatha.sources.mythology.celtic_mythology import (
    MythologyResult,
    search_mythology,
    search_owain_glyndwr,
    search_tuatha_de_danann,
)

__all__ = [
    "MythologyResult",
    "search_mythology",
    "search_owain_glyndwr",
    "search_tuatha_de_danann",
]
