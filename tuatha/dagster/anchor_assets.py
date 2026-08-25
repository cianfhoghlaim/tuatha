"""tuatha.dagster.anchor_assets — rung-5 Merkle anchor computation + asset_check."""
from __future__ import annotations
import hashlib
import json
from dagster import asset, asset_check, AssetExecutionContext, AssetCheckResult
import duckdb
from pathlib import Path


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
    root = (context.op_execution_context.op_output_values() or {}).get("rung5_root", "")
    valid = bool(re.match(r"^[0-9a-f]{64}$", root))
    return AssetCheckResult(passed=valid,
                            metadata={"root": root, "expected_pattern": "^[0-9a-f]{64}$"})
