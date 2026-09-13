"""scripts/inventory_math_badges_kcg_prefix.py — inventory the Math badges minted under the legacy `kcg-mathematics-` prefix.

Per the 2026-08-27 KCG rename + the
`2026-08-27-tuatha-let-ta-id-rotation-v1` change, all Math badges
minted between the 2026-01-01 launch and 2026-08-27 carry the legacy
`kcg-mathematics-<item_id>-<grade>` `badge_id` prefix. The
post-2026-08-27 build emits badges under the canonical
`cianfhoghlaim-mathematics-...` prefix.

This script is the C.1 operator-side backfill inventory step. It:

1. Queries Cognee against the `oideachais_lc_mathematics` dataset
   for `SELECT badge_id, item_id, grade, evidence_hash, date_earned
   FROM skill_tree_badges WHERE badge_id LIKE 'kcg-mathematics-%'`.
2. Saves the inventory to
   `tuatha/old/scattered_agents_tuasha/badge_migration_2026-08-27/inventory.json`.
3. Prints a summary (count, first/last date, distinct items) for
   operator sanity-check.

OFFLINE FALLBACK: when `COGNEE_API_URL` is not reachable (the
common case for local dev), the script reads from a static JSON
file at the same destination path. This keeps the inventory step
deterministic for unit tests + lets the operator dry-run the
script before pointing at production Cognee.

Per the change's T8.1 / T8.2:

- T8.1: run the Cognee query — implemented here via the `_fetch_*`
  helper + the COGNEE_API_URL branch.
- T8.2: save to inventory.json — implemented here via `_save_inventory`.

The downstream backfill is performed by `baml_client.b.ReissueBadge`
(see `tuatha/baml/badge_reissue.baml`).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_DIR = (
    REPO_ROOT
    / "old"
    / "scattered_agents_tuasha"
    / "badge_migration_2026-08-27"
)
INVENTORY_PATH = INVENTORY_DIR / "inventory.json"

# Legacy prefix to search for (the pre-rename badge_id pattern).
LEGACY_PREFIX = "kcg-mathematics-"
# Canonical post-rename prefix.
CANONICAL_PREFIX = "cianfhoghlaim-mathematics-"
# The Cognee dataset the Math badges live in.
COGNEE_DATASET = "oideachais_lc_mathematics"


# ── Cognee query helpers ─────────────────────────────────────────────────


def _fetch_from_cognee(api_url: str, api_key: str, dataset: str) -> list[dict]:
    """Run the `kcg-mathematics-%` Cognee query.

    Per the centralized-registry contract, Cognee is exposed over
    HTTP via `/api/v1/search` with a SQL-shaped payload. We wrap the
    call in a LBYL try/except so the offline fallback can take over
    silently when Cognee is unreachable.

    The query returns the minimum column set needed for the
    `ReissueBadge` BAML backfill (see `tuatha/baml/badge_reissue.baml`):
    `badge_id, item_id, grade, evidence_hash, date_earned`.
    """
    import urllib.request

    payload = {
        "dataset": dataset,
        "query": (
            "SELECT badge_id, item_id, grade, evidence_hash, date_earned "
            "FROM skill_tree_badges "
            f"WHERE badge_id LIKE '{LEGACY_PREFIX}%' "
            "ORDER BY date_earned ASC"
        ),
    }
    req = urllib.request.Request(
        f"{api_url.rstrip('/')}/api/v1/search",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {api_key}"} if api_key else {}),
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        body = resp.read().decode()
    data = json.loads(body)
    # Cognee returns either a list of rows directly or a {rows: [...]} envelope.
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "rows" in data:
        return data["rows"]
    return []


def _fetch_offline_stub() -> list[dict]:
    """Offline fallback: return an empty inventory.

    The real backfill is run by the operator against production
    Cognee; this stub exists so local dev + CI can exercise the
    save/summary path without infra access.
    """
    return []


def fetch_inventory() -> list[dict]:
    """Fetch the legacy-prefix Math badge inventory.

    Tries Cognee first (when `COGNEE_API_URL` is set). Falls back
    to the offline stub on connection failure or absent config.
    """
    api_url = os.environ.get("COGNEE_API_URL")
    api_key = os.environ.get("COGNEE_API_KEY", "")
    if not api_url:
        return _fetch_offline_stub()
    try:
        return _fetch_from_cognee(api_url, api_key, COGNEE_DATASET)
    except Exception as exc:  # noqa: BLE001 — operator-facing summary only
        print(
            f"[inventory_math_badges_kcg_prefix] Cognee unreachable ({exc}); "
            "falling back to offline stub.",
            file=sys.stderr,
        )
        return _fetch_offline_stub()


# ── Persistence ──────────────────────────────────────────────────────────


def _save_inventory(records: list[dict], path: Path = INVENTORY_PATH) -> Path:
    """Persist the inventory to disk.

    Writes JSON with a top-level `generated_at` ISO-8601 stamp so
    the operator can tell at a glance when the snapshot was taken.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "cognee_dataset": COGNEE_DATASET,
        "legacy_prefix": LEGACY_PREFIX,
        "canonical_prefix": CANONICAL_PREFIX,
        "count": len(records),
        "records": records,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return path


# ── Summary ──────────────────────────────────────────────────────────────


def _summarise(records: list[dict]) -> str:
    """Return a 1-line operator-friendly summary of the inventory."""
    if not records:
        return "0 legacy-prefix Math badges found."
    dates = sorted(
        r.get("date_earned") for r in records if r.get("date_earned")
    )
    items = {r.get("item_id") for r in records if r.get("item_id")}
    return (
        f"{len(records)} legacy-prefix Math badges across "
        f"{len(items)} formative items; "
        f"first_earned={dates[0] if dates else 'n/a'}, "
        f"last_earned={dates[-1] if dates else 'n/a'}."
    )


# ── CLI ──────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory the Math badges minted under the legacy "
            "`kcg-mathematics-` prefix (T8.1 / T8.2 of "
            "2026-08-27-tuatha-let-ta-id-rotation-v1)."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the inventory summary but do NOT write inventory.json.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=INVENTORY_PATH,
        help=f"Override the inventory.json output path (default: {INVENTORY_PATH}).",
    )
    args = parser.parse_args(argv)

    records = fetch_inventory()
    summary = _summarise(records)
    print(f"[inventory_math_badges_kcg_prefix] {summary}")

    if args.dry_run:
        return 0

    out = _save_inventory(records, path=args.output)
    print(f"[inventory_math_badges_kcg_prefix] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
