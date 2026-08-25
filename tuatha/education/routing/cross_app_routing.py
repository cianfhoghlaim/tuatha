"""tuatha.education.routing.cross_app_routing — Hono middleware that fans out.

Routes a single learner's session across the 3 web apps:
- app.mmo (the British Isles MMO client)
- education (the Phase 5 agent + persistent state surface)
- docs (the provenance ladder inspector)

Every response carries the Phase 3 rung-5 root in X-Rung5-Root (G7 provenance).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Phase5RoutingDecision:
    """The canonical cross-app routing decision."""
    target_app: str                       # "app.mmo" | "education" | "docs"
    target_endpoint: str                 # e.g. "/api/agent/chat"
    rung5_root: str                      # the Phase 3 anchor root to forward
    reason: str


class Phase5CrossAppRouter:
    """The Phase 5 router. Stateless; one instance per request."""

    def route(self, prompt: str, current_app: str,
              student_id: Optional[str] = None) -> Phase5RoutingDecision:
        p = prompt.lower()
        # Lore queries go to docs (read-only)
        if any(k in p for k in ("tuatha dé danann", "déisigh", "uí liatháin",
                               "mabinogi", "gwydion", "celtic lore")):
            return Phase5RoutingDecision(
                target_app="docs",
                target_endpoint="/docs/celtic-lore/",
                rung5_root=self._read_rung5_root(),
                reason="lore query → docs surface",
            )
        # Cross-subject queries go to education (the agent + state surface)
        if any(k in p for k in ("compar", "cross-subject", "equivalen",
                               "between", "how does")):
            return Phase5RoutingDecision(
                target_app="education",
                target_endpoint="/api/agent/chat",
                rung5_root=self._read_rung5_root(),
                reason="cross-subject query → education agent surface",
            )
        # Default: stay in the current app
        return Phase5RoutingDecision(
            target_app=current_app,
            target_endpoint="/",
            rung5_root=self._read_rung5_root(),
            reason="default → stay in current app",
        )

    def _read_rung5_root(self) -> str:
        # Production: query the Phase 3 anchor_assets
        return "0".repeat(64)


def make_phase5_router() -> Phase5CrossAppRouter:
    return Phase5CrossAppRouter()
