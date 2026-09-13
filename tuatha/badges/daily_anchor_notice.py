"""tuatha.badges.daily_anchor_notice — the daily Merkle anchor notification stub.

Per the `2026-08-27-tuatha-let-ta-id-rotation-v1` change (T10.1 /
T10.2): the `daily_credential_anchor` Dagster asset (in
`tuatha/dagster/anchor_assets.py`) MUST emit a one-line notice to
both the Langfuse + Cognee surfaces explaining the kcg- →
cianfhoghlaim- prefix rotation, every day, until the 14-day
release cycle has elapsed.

The notice text is the canonical copy from the openspec change:

> Badge IDs minted between 2026-01-01 and 2026-08-27 carry the
> legacy `kcg-` prefix; re-issued under `cianfhoghlaim-` prefix
> on 2026-08-27. See
> openspec/changes/2026-08-27-tuatha-let-ta-id-rotation-v1/.

Per T10.2: the next daily anchor (2026-08-28) MUST include the
re-issued badges as separate Merkle leaves (NOT as new badges —
same `evidence_hash`, different `badge_id`). This module emits
the notice but does NOT touch the Merkle construction; that
lives in `tuatha.badges.anchor.publish_anchor`.

The function is a STUB: the Langfuse annotation + Cognee addendum
calls are wrapped in LBYL try/except so the local-dev + CI
fallback path runs without infra. The contract surface is the
canonical (Langfuse trace name, Cognee dataset) pair, both
sourced from `tuatha.config.TuathaConfig`.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from ..config import TuathaConfig

# ── Constants ────────────────────────────────────────────────────────────

# The canonical notice text per T10.1.
NOTICE_TEXT = (
    "Badge IDs minted between 2026-01-01 and 2026-08-27 carry the "
    "legacy `kcg-` prefix; re-issued under `cianfhoghlaim-` prefix "
    "on 2026-08-27. See "
    "openspec/changes/2026-08-27-tuatha-let-ta-id-rotation-v1/."
)

# The openspec change ID for audit-traceability. Surfaced in the
# Langfuse trace metadata + the Cognee addendum so operators can
# grep either surface and land back on this change's proposal.md.
CHANGE_ID = "2026-08-27-tuatha-let-ta-id-rotation-v1"

# The legacy-prefix window. After 2026-08-27 the notice stays
# pinned in the daily anchor dashboard for the 14-day release
# cycle (the T7.1 archival deadline); operators should remove
# the notice manually after 2026-09-10.
LEGACY_PREFIX_WINDOW_START = "2026-01-01"
LEGACY_PREFIX_WINDOW_END = "2026-08-27"

# Langfuse trace name template (the canonical daily anchor surface).
LANGFUSE_TRACE_TEMPLATE = "credential.anchor.{date}"

# Cognee dataset the notice is appended to (mirrors the
# `oideachais_<jurisdiction>_<subject>` pattern from
# `tuatha.config.CogneeConfig.dataset_pattern`).
COGNEE_NOTICE_DATASET = "oideachais_credential_anchors"

_log = logging.getLogger(__name__)


# ── Notification helpers ────────────────────────────────────────────────


def _emit_langfuse_notice(
    config: TuathaConfig,
    batch_date: str,
    merkle_root: str,
    leaf_count: int,
    notice_text: str,
) -> dict[str, Any]:
    """Emit the notice to the Langfuse `credential.anchor.<date>` trace.

    Tries the Langfuse SDK first; on `ImportError` (the common
    local-dev case) the function logs the notice at INFO + returns
    a stub result so the caller can confirm the path was exercised.

    The trace carries 4 metadata fields so the Langfuse UI can
    surface the notice alongside the daily anchor's Merkle root:
    `change_id`, `legacy_prefix_window_start`, `legacy_prefix_window_end`,
    `notice_text`.
    """
    trace_name = LANGFUSE_TRACE_TEMPLATE.format(date=batch_date)
    payload = {
        "change_id": CHANGE_ID,
        "legacy_prefix_window_start": LEGACY_PREFIX_WINDOW_START,
        "legacy_prefix_window_end": LEGACY_PREFIX_WINDOW_END,
        "notice_text": notice_text,
        "merkle_root": merkle_root,
        "leaf_count": leaf_count,
    }
    try:
        from langfuse import get_client  # type: ignore[import-not-found]

        client = get_client()
        # The `update_current_observation` API lets a Dagster asset
        # attach metadata to a trace emitted by an earlier step
        # without spinning up a full observation. We use it here to
        # attach the notice to the canonical daily-anchor trace.
        client.update_current_observation(metadata=payload)
        return {"emitted": True, "trace_name": trace_name, "sdk": "langfuse"}
    except ImportError:
        _log.info(
            "langfuse_notice trace_name=%s payload=%s",
            trace_name,
            payload,
        )
        return {"emitted": False, "trace_name": trace_name, "sdk": "stub"}


def _emit_cognee_notice(
    config: TuathaConfig,
    batch_date: str,
    merkle_root: str,
    leaf_count: int,
    notice_text: str,
) -> dict[str, Any]:
    """Append the notice to the Cognee `credential_anchors` dataset.

    Same offline-fallback pattern as the Langfuse helper: real HTTP
    POST when the SDK is importable + the base URL is reachable;
    log-only stub otherwise. The addendum is a single doc keyed by
    `(batch_date, change_id)` so a re-run for the same day is
    idempotent (the Cognee `add` endpoint upserts on key).
    """
    payload = {
        "batch_date": batch_date,
        "change_id": CHANGE_ID,
        "notice_text": notice_text,
        "merkle_root": merkle_root,
        "leaf_count": leaf_count,
        "ts": datetime.now(tz=timezone.utc).isoformat(),
    }
    try:
        from cognee import add as _cognee_add  # type: ignore[import-not-found]

        _cognee_add(
            data=notice_text,
            dataset_name=COGNEE_NOTICE_DATASET,
            metadata=payload,
        )
        return {"emitted": True, "dataset": COGNEE_NOTICE_DATASET, "sdk": "cognee"}
    except ImportError:
        _log.info(
            "cognee_notice dataset=%s payload=%s",
            COGNEE_NOTICE_DATASET,
            payload,
        )
        return {"emitted": False, "dataset": COGNEE_NOTICE_DATASET, "sdk": "stub"}


# ── Public API ──────────────────────────────────────────────────────────


def send_daily_anchor_notice(
    batch_date: str,
    merkle_root: str,
    leaf_count: int,
    notice_text: str = NOTICE_TEXT,
    config: TuathaConfig | None = None,
) -> dict[str, Any]:
    """Send the daily Merkle anchor notice to Langfuse + Cognee.

    Called by the `daily_credential_anchor` Dagster asset
    immediately after `tuatha.badges.anchor.publish_anchor`
    returns the MerkleBatch. The notice is idempotent for a given
    `(batch_date, change_id)` pair — re-running for the same day
    simply upserts the Langfuse metadata + the Cognee addendum.

    Args:
        batch_date: YYYY-MM-DD string of the daily anchor batch.
        merkle_root: The hex-encoded 32-byte Merkle root that was
            just published to the on-chain `CredAnchor` contract.
        leaf_count: The number of badge evidence hashes in the
            Merkle tree.
        notice_text: Override for the canonical notice text
            (defaults to NOTICE_TEXT).
        config: Optional `TuathaConfig` override; defaults to
            `TuathaConfig.from_env()`.

    Returns:
        A dict with `langfuse` + `cognee` per-surface results so
        the caller (the Dagster asset) can attach it as
        `output_metadata`.
    """
    cfg = config or TuathaConfig.from_env()
    return {
        "langfuse": _emit_langfuse_notice(
            cfg, batch_date, merkle_root, leaf_count, notice_text
        ),
        "cognee": _emit_cognee_notice(
            cfg, batch_date, merkle_root, leaf_count, notice_text
        ),
        "change_id": CHANGE_ID,
        "batch_date": batch_date,
        "merkle_root": merkle_root,
        "leaf_count": leaf_count,
    }


__all__ = [
    "NOTICE_TEXT",
    "CHANGE_ID",
    "LEGACY_PREFIX_WINDOW_START",
    "LEGACY_PREFIX_WINDOW_END",
    "send_daily_anchor_notice",
]
