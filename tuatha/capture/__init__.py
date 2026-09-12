"""tuatha.capture — the ANAM capture surface.

Sub-packages:
- `macos/` — DEPRECATED (per the 2026-08-27 change). The Phase-1
  Swift capture daemon (see macos/DEPRECATED.md).
- `python/` — Python-side capture helpers (GBA + comic subcommands).
- `hermes_client.py` — the Hermes Agent computer-use HTTP client
  (Phase-2 capture path).

The canonical capture pipeline for Hades boons + X-Men powers +
Avatar elemental bending is:

  NCCA source PDF → DLT → DuckDB rung-1
    → CocoIndex v1 embed → Lance rung-4
      → BAML ExtractXxxSource(image) → typed Source row
        → BAML MapToAnamParticle(source, source_payload) → Celtic-deity + palette
          → Lance cianfhoghlaim.tuatha.anam.particles rung-4
            → RAGAS anam_color_anchor ΔE CIE76 ≤ 8

The capture module handles only the frame ingestion step (the
Swift daemon or Hermes Agent path). The rest is the CocoIndex +
BAML pipeline in `tuatha/cocoindex/anam/`.
"""

from __future__ import annotations

from .hermes_client import (
    HERMES_BASE_URL,
    HermesClient,
    HermesConfig,
    HermesRunState,
)

__all__ = [
    "HERMES_BASE_URL",
    "HermesClient",
    "HermesConfig",
    "HermesRunState",
]
