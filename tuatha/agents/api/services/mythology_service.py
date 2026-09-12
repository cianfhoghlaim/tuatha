"""Mythology service for the Tuatha FastAPI surface.

Status: STUB. The real impl reads from `tuatha/agents/media_intel/` +
the LanceDB-backed mythology corpus (`oideachais.badges.embeddings.lance`
per the consolidated `2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1`
change). Until that corpus is populated in this checkout, this stub
returns deterministic placeholder responses so the FastAPI router can
load + respond to health checks.
"""

from dataclasses import dataclass


@dataclass
class MythologySearchResult:
    """One mythology search hit."""

    character_id: str
    name: str
    tradition: str
    snippet: str


class MythologyService:
    """Stub mythology service — placeholder until the corpus is wired."""

    async def search(
        self,
        query: str,
        tradition: str | None = None,
        limit: int = 10,
    ) -> list[MythologySearchResult]:
        return []

    async def get_character_lore(self, character_id: str) -> dict:
        return {"character_id": character_id, "stub": True}

    async def get_location_lore(self, location_id: str) -> dict:
        return {"location_id": location_id, "stub": True}
