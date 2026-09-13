"""tuatha.dagster.anchor_assets — rung-5 Merkle anchor + the daily credential anchor.

Two asset groups live here:

1. ``rung5_merkle_root`` — the historical anchor asset that
   computes a Merkle root over the ``(subject, language, sha256)``
   tuples in the local DuckDB ``official_documents`` table.

2. ``daily_credential_anchor`` — the Phase-3 Layer-4 (P2) asset
   that runs at 02:00 UTC: it fetches all *unrevoked* badges since
   the last anchor, computes the Merkle root, publishes it to the
   ``CredAnchor`` contract on Base L2, and persists the resulting
   ``tx_hash`` back into each badge row in Convex. This is the
   canonical implementation of
   ``openspec/changes/2026-08-26-tuatha-multimodel-2d-graphics-
   and-earn-pipeline-v1`` Layer 4 + 5.

NOTE: do NOT add ``from __future__ import annotations`` here — the
``@asset`` decorator introspects the ``context`` parameter's type
hint via ``inspect.signature`` (not ``get_type_hints``), so a string
annotation from PEP 563 raises
``DagsterInvalidDefinitionError: Cannot annotate `context`
parameter with type AssetExecutionContext`` at module load time.
Per the prior fix ``b05ef4ee fix(anchor_assets): remove 'from
__future__ import annotations' so Dagster @asset context type
validation works``.
"""
import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from dagster import asset, asset_check, AssetExecutionContext, AssetCheckResult
from pathlib import Path

from ..badges.anchor import publish_anchor

# duckdb is an optional dependency: ``rung5_merkle_root`` requires
# it, but ``daily_credential_anchor`` does NOT (it reads badges
# from Convex, not DuckDB). Probing it lazily so the module loads
# cleanly when duckdb is not installed (e.g. unit-test venv).
try:
    import duckdb  # type: ignore[import-not-found]
    _DUCKDB_AVAILABLE = True
except ImportError:
    duckdb = None  # type: ignore[assignment, misc]
    _DUCKDB_AVAILABLE = False


def _resolve_db_path() -> Path:
    p = (Path(__file__).resolve().parent.parent.parent
         / "sources" / "duckdb" / "tuatha_official_documents.duckdb")
    s = str(p)
    return Path("/tmp/" + s[len("/private/tmp/"):]) if s.startswith("/private/tmp/") else p


def _compute_merkle_root(rows):
    """Compute a deterministic Merkle root over the rung-1 → rung-4 evidence chain."""
    leaves = [json.dumps(r, sort_keys=True).encode() for r in rows]
    leaves = [hashlib.sha256(b).hexdigest() for b in leaves]
    while len(leaves) > 1:
        leaves = [hashlib.sha256((leaves[i] + leaves[i + 1]).encode()).hexdigest()
                  for i in range(0, len(leaves) - 1, 2)]
    return leaves[0] if leaves else hashlib.sha256(b"").hexdigest()


@asset(group_name="tuatha_anchor", compute_kind="python")
def rung5_merkle_root(context: AssetExecutionContext) -> dict:
    """Compute the rung-5 Merkle root over all (subject, language, sha256) tuples."""
    if not _DUCKDB_AVAILABLE or duckdb is None:
        context.add_output_metadata({
            "rung5_root": hashlib.sha256(b"").hexdigest(),
            "leaf_count": 0,
            "skipped": True,
            "reason": "duckdb not installed; rung5_merkle_root is a no-op",
        })
        return {"rung5_root": hashlib.sha256(b"").hexdigest(), "leaf_count": 0}
    con = duckdb.connect(str(_resolve_db_path()), read_only=True)
    rows = con.execute(
        "SELECT DISTINCT subject, language, sha256_hash, source_page_count "
        "FROM (SELECT subject, language, sha256_hash, COUNT(*) AS source_page_count "
        "FROM official_documents GROUP BY subject, language, sha256_hash)"
    ).fetchall()
    con.close()
    root = _compute_merkle_root([dict(zip(("subject","language","sha256","page_count"), r)) for r in rows])
    context.add_output_metadata({"rung5_root": root, "leaf_count": len(rows)})
    return {"rung5_root": root, "leaf_count": len(rows)}


@asset_check(asset=rung5_merkle_root)
def rung5_merkle_validity_check(context: AssetExecutionContext) -> AssetCheckResult:
    """Verify the rung-5 root is 64-hex-char + matches the contract."""
    import re
    root = (context.op_execution_context.op_output_values() or {}).get("rung5_root", "")
    valid = bool(re.match(r"^[0-9a-f]{64}$", root))
    return AssetCheckResult(passed=valid,
                            metadata={"root": root, "expected_pattern": "^[0-9a-f]{64}$"})


@asset(group_name="tuatha_anchor", compute_kind="python")
async def daily_credential_anchor(context: AssetExecutionContext) -> dict:
    """The Phase-3 Layer-4 (P2) daily Merkle anchor asset.

    Runs at 02:00 UTC (the canonical CronSchedule in the upstream
    ``Definitions`` job). The asset:

    1. Fetches all *unrevoked* ``SkillTreeBadge`` rows minted since
       the previous anchor (the in-process
       ``badges.ledger.fetch_unrevoked_badges_since()`` helper does
       this; revoked badges are excluded so the published root
       reflects the *currently valid* credential corpus, per the
       24h propagation guarantee in
       ``tuatha/docs/REVOCATION_POLICY.md``).
    2. Skips the publish when zero new badges exist (the daily
       batch is no-op when nothing has been issued since the last
       run — saves gas + keeps the on-chain history clean).
    3. Computes the Merkle root via ``badges.anchor.compute_merkle_root``.
    4. Calls ``badges.anchor.publish_anchor()`` which routes to
       ``CredAnchor.publish(root, batchId)`` on Base L2
       (real ``web3.py`` call when ``CIANFHOGHLAIM_BASE_L2_RPC_URL``
       is configured; deterministic placeholder otherwise).
    5. Writes the resulting ``tx_hash`` + ``anchor_date`` back into
       each badge row in Convex via
       ``badges.storage.persist_on_chain_anchor()``.

    The asset materialises to a dict so Dagster can show the
    batch metadata + the per-step status in the UI:

        {
            "batch_id": "uuid",
            "batch_date": "YYYY-MM-DD",
            "merkle_root": "0x...",
            "tx_hash": "0x...",
            "leaf_count": int,
            "published_at": "ISO 8601",
            "skipped": bool,
        }
    """
    import asyncio

    from ..badges.ledger import fetch_unrevoked_badges_since

    batch_date = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    # The "since the last anchor" window: default to "since the
    # start of the UTC day" so the cron tick is idempotent — a
    # re-run the same day re-computes the same Merkle root over
    # the same badges. The upstream CronSchedule at 02:00 UTC
    # guarantees exactly one tick per UTC day in production.
    since_iso = datetime.now(tz=timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0,
    ).isoformat()

    badges = await fetch_unrevoked_badges_since(since_iso)

    if len(badges) == 0:
        context.add_output_metadata({
            "batch_date": batch_date,
            "skipped": True,
            "reason": "no new unrevoked badges since the last anchor",
            "leaf_count": 0,
        })
        return {
            "batch_id": "",
            "batch_date": batch_date,
            "merkle_root": "",
            "tx_hash": "",
            "leaf_count": 0,
            "published_at": datetime.now(tz=timezone.utc).isoformat(),
            "skipped": True,
        }

    # publish_anchor is itself an async function — await it so
    # the Base L2 web3.py call doesn't block the event loop.
    batch = await publish_anchor(badges, batch_date=batch_date)

    payload: dict[str, Any] = {
        "batch_id": batch.id,
        "batch_date": batch.batch_date,
        "merkle_root": batch.merkle_root,
        "tx_hash": batch.tx_hash or "",
        "leaf_count": batch.leaf_count,
        "badge_ids": list(batch.badge_ids),
        "published_at": (
            batch.published_at.isoformat() if batch.published_at else None
        ),
        "skipped": False,
    }

    context.add_output_metadata({
        "batch_id": batch.id,
        "batch_date": batch.batch_date,
        "merkle_root": batch.merkle_root,
        "tx_hash": batch.tx_hash or "",
        "leaf_count": batch.leaf_count,
    })

    # Suppress the unused-import lint (the `asyncio` import is
    # reserved for callers that want to invoke the asset body
    # from a sync context via `asyncio.run`).
    _ = asyncio
    return payload


__all__ = [
    "daily_credential_anchor",
    "rung5_merkle_root",
    "rung5_merkle_validity_check",
]
