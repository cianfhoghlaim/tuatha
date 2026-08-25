"""tuatha.dagster.anchor_assets — the `daily_credential_anchor` Dagster asset.

The Phase-3 P2 + P5 + P8 crypto layer. Runs at 02:00 UTC every day,
computes the day's Merkle root over the non-revoked SkillTreeBadge
set, and publishes it to the `CredAnchor` contract on Base L2.

Per Layer 4 (P2) + Layer 5 (P5) + Layer 6 (P8) of
`2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1`:

    1. Fetch all un-anchored, non-revoked SkillTreeBadge rows from
       Convex since the last anchor.
    2. Compute the Merkle root (SHA-256, sorted leaves).
    3. Call `CredAnchor.publish(batchId, merkleRoot, leafCount)`.
    4. Write the resulting `tx_hash` back into each badge row.
    5. (P8) Exclude any badges that were revoked on or before the
       batch date — the next day's `/anchor/<date>` page shows the
       *post-revocation* root.

Idempotency: the asset skips when there are 0 badges to anchor
(matches the CredAnchor `leafCount > 0` requires).

Reference:
- `tuatha/badges/anchor.py` — the underlying Merkle + publish helpers
- `tuatha/badges/anchor_contract.py` — the Python `publish(root, batchId)` binding
- `tuatha/badges/ledger.py::fetch_unrevoked_badges_since` — the badge fetcher
- `tuatha/docs/REVOCATION_POLICY.md` — the 24h propagation guarantee
"""
from __future__ import annotations

import asyncio
import contextlib
from datetime import datetime, timedelta, timezone

try:
    from dagster import (
        AssetExecutionContext,
        DailyPartitionsDefinition,
        asset,
    )
    _DAGSTER_AVAILABLE = True
except ImportError:
    # Dagster isn't installed in dev/test environments. Provide
    # stubs that let the module still be importable (so unit
    # tests can exercise the underlying logic via direct calls).
    _DAGSTER_AVAILABLE = False

    def asset(*_args: object, **_kwargs: object):  # type: ignore[no-redef]
        def _decorator(fn):  # type: ignore[no-untyped-def]
            return fn
        return _decorator

    class DailyPartitionsDefinition:  # type: ignore[no-redef]
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

    class AssetExecutionContext:  # type: ignore[no-redef]
        partition_key: str = "1970-01-01"

        def log(self, *args: object, **kwargs: object) -> None:  # type: ignore[no-untyped-def]
            pass

        def add_output_metadata(self, *args: object, **kwargs: object) -> None:  # type: ignore[no-untyped-def]
            pass

from tuatha.badges.anchor import compute_merkle_root, publish_anchor
from tuatha.badges.ledger import fetch_unrevoked_badges_since
from tuatha.badges.storage import persist_on_chain_anchor

_UTC = timezone.utc

# 02:00 UTC daily schedule. The partition definition uses the
# canonical YYYY-MM-DD key — the same shape used by CredAnchor's
# `batchId` parameter + the public `/anchor/<date>` route.
DAILY_PARTITION = DailyPartitionsDefinition(
    start_date="2026-08-01",
    hour_offset=2,
)


@asset(
    group_name="tuatha_credentials",
    compute_kind="web3.py",
    partitions_def=DAILY_PARTITION,
    description=(
        "Daily Merkle root anchor for the SkillTreeBadge ledger. "
        "Runs at 02:00 UTC, computes the root over the day's "
        "non-revoked badges, and publishes it to the CredAnchor "
        "contract on Base L2. Writes the resulting tx_hash back "
        "into each badge row so the public /anchor/<date> page can "
        "verify Merkle paths."
    ),
)
def daily_credential_anchor(
    context: AssetExecutionContext,
) -> dict[str, object]:
    """The daily Merkle root anchor asset.

    Partition key format: ``YYYY-MM-DD`` (UTC). The asset materialises
    once per day at 02:00 UTC. Materialisation is skipped (returns
    ``status='no_new_badges'``) when there are no new badges since
    the previous day's anchor — mirrors the `CredAnchor.publish()`
    `leafCount > 0` requirement.

    Returns a dict with:
    - ``status``: ``"anchored"`` or ``"no_new_badges"``
    - ``batch_id``: the YYYY-MM-DD partition key
    - ``merkle_root``: 0x-prefixed 32-byte root (or ``None``)
    - ``leaf_count``: number of badges included
    - ``on_chain_anchor``: 0x-prefixed Base L2 tx_hash (or ``None``)
    - ``badges_persisted``: how many badge rows had ``on_chain_anchor``
      updated in Convex
    """
    partition_key: str = getattr(context, "partition_key", "2026-08-26")
    batch_date: str = partition_key
    batch_start = datetime.fromisoformat(batch_date).replace(tzinfo=_UTC)
    batch_end = batch_start + timedelta(days=1)

    context.log.info(
        f"daily_credential_anchor: processing batch {batch_date} "
        f"({batch_start.isoformat()} -> {batch_end.isoformat()})"
    )

    badges = _fetch_unrevoked_badges_for_batch(batch_start, batch_end, context)

    if not badges:
        with contextlib.suppress(Exception):
            context.add_output_metadata(
                {
                    "status": "no_new_badges",
                    "batch_id": batch_date,
                    "leaf_count": 0,
                }
            )
        return {
            "status": "no_new_badges",
            "batch_id": batch_date,
            "merkle_root": None,
            "leaf_count": 0,
            "on_chain_anchor": None,
            "badges_persisted": 0,
        }

    merkle_root = compute_merkle_root([b.evidence_hash for b in badges])
    context.log.info(
        f"daily_credential_anchor: computed merkle_root={merkle_root!r} "
        f"over {len(badges)} badges"
    )

    # `publish_anchor` is async — but Dagster asset functions are
    # sync, so we run it to completion via the sync wrapper. The
    # underlying implementation already handles the
    # dev/test-no-RPC placeholder branch.
    batch = asyncio.run(publish_anchor(badges, batch_date=batch_date))

    # Persist the tx_hash + batch_date back into each badge row in
    # Convex so the public `/anchor/<date>` page can resolve them.
    persisted = 0
    for badge in badges:
        if persist_on_chain_anchor(badge.id, batch.tx_hash or "", batch_date):
            persisted += 1

    with contextlib.suppress(Exception):
        context.add_output_metadata(
            {
                "status": "anchored",
                "batch_id": batch_date,
                "merkle_root": merkle_root,
                "leaf_count": len(badges),
                "on_chain_anchor": batch.tx_hash,
                "badges_persisted": persisted,
            }
        )

    return {
        "status": "anchored",
        "batch_id": batch_date,
        "merkle_root": merkle_root,
        "leaf_count": len(badges),
        "on_chain_anchor": batch.tx_hash,
        "badges_persisted": persisted,
    }


def _fetch_unrevoked_badges_for_batch(
    batch_start: datetime,
    batch_end: datetime,
    context: AssetExecutionContext,
) -> list:
    """Fetch the non-revoked badges minted during the batch window.

    Reads from the ledger's `fetch_unrevoked_badges_since` helper,
    which excludes any badge whose ``is_revoked`` flag is True.
    The result is the input set for the day's Merkle tree.

    Dev/test fallback: when Convex is unavailable, the ledger
    helper returns ``[]`` — the asset then short-circuits with
    ``status='no_new_badges'`` instead of raising.
    """
    since_iso = batch_start.isoformat()
    badges = asyncio.run(fetch_unrevoked_badges_since(since_iso))
    context.log.info(
        f"daily_credential_anchor: fetched {len(badges)} unrevoked "
        f"badges since {since_iso}"
    )
    # Drop badges that landed outside the [batch_start, batch_end)
    # window (the ledger helper queries "since", not "in range").
    return [b for b in badges if batch_start <= b.date_earned < batch_end]


__all__ = [
    "DAILY_PARTITION",
    "daily_credential_anchor",
]
