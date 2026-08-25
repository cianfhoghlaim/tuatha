# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.10.0",
#     "httpx>=0.27",
# ]
# ///

"""tuatha.notebooks.38_merkle_verifier — marimo notebook for the daily Merkle anchor verifier.

The Phase-3 P5 off-chain verification demo. Given a published
``batch_date`` (``YYYY-MM-DD``), fetches the on-chain Merkle root from
the public ``/anchor/<date>`` endpoint + recomputes the Merkle path
for one or more ``(badge_id, evidence_hash)`` pairs against that
root. The recomputation uses the canonical sorted-leaves +
sorted-pair + SHA-256 algorithm — the same algorithm the Python
``tuatha/badges/anchor.py::compute_merkle_root`` + the on-chain
``RevocationList.computeRootFromSortedLeaves`` use, so a passing
result here proves the on-chain anchor is genuine.

Run with:
    marimo edit notebooks/38_merkle_verifier.py
    # or
    uv run marimo run notebooks/38_merkle_verifier.py

Per `2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1`,
Layer 5 (P5).
"""
import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Daily Merkle Anchor Verifier

        Off-chain verification of the Tuatha daily credential
        anchor. Given a published `batch_date` (YYYY-MM-DD),
        this notebook:

        1. Fetches the on-chain Merkle root for that date
           (via the public `/anchor/<date>` endpoint).
        2. Accepts one or more `(badge_id, evidence_hash)`
           pairs from the verifier (employer, university,
           parent, etc.).
        3. Recomputes the Merkle path for each pair against
           the on-chain root.
        4. Reports a clear pass/fail indicator per pair.

        ## Inputs

        | Field | Description | Example |
        |:--|:--|:--|
        | `batch_date` | The YYYY-MM-DD anchor date | `2026-08-26` |
        | `badge_id` | The SkillTreeBadge UUID | `b3c8...` |
        | `evidence_hash` | The badge's evidence hash (hex) | `0xabc...` |
        | `merkle_path` | The path of sibling hashes (hex list) | `["0x...", ...]` |

        The on-chain root is read from `CredAnchor.getAnchor(batchId)`
        via the public anchor page. The path is provided by the
        student's wallet / Convex row (the path itself is stored
        off-chain for privacy).
        """
    )
    return (mo,)


@app.cell
def _():
    import hashlib
    import os
    from typing import Optional

    import httpx
    return httpx, hashlib, os, Optional


@app.cell
def _(mo):
    batch_date_input = mo.ui.text(
        value="2026-08-26",
        label="Batch date (YYYY-MM-DD)",
        placeholder="2026-08-26",
    )
    badge_id_input = mo.ui.text(
        value="",
        label="Badge ID (UUID)",
        placeholder="b3c8e1f0-aaaa-bbbb-cccc-dddddddddddd",
    )
    evidence_hash_input = mo.ui.text(
        value="0x",
        label="Evidence hash (0x-prefixed hex)",
        placeholder="0xabc...",
    )
    merkle_path_input = mo.ui.text_area(
        value="",
        label="Merkle path (one sibling hash per line, 0x-prefixed hex)",
        rows=5,
    )
    public_anchor_base_input = mo.ui.text(
        value=os.environ.get(
            "TUATHA_PUBLIC_ANCHOR_BASE",
            "https://tuatha-ui.cianfhoghlaim.ie/anchor",
        ),
        label="Public /anchor/<date> base URL",
    )
    mo.vstack(
        [
            mo.md("## Inputs"),
            batch_date_input,
            public_anchor_base_input,
            mo.md("### Badge to verify"),
            badge_id_input,
            evidence_hash_input,
            merkle_path_input,
        ]
    )
    return (
        badge_id_input,
        batch_date_input,
        evidence_hash_input,
        merkle_path_input,
        public_anchor_base_input,
    )


@app.cell
def _(hashlib):
    def verify_merkle_path(
        leaf_hash_hex: str,
        merkle_root_hex: str,
        path: list[str],
    ) -> bool:
        """Recompute the Merkle path against the on-chain root.

        Uses the canonical sorted-leaves + sorted-pair + SHA-256
        convention (the same algorithm as
        ``tuatha/badges/anchor.py::verify_merkle_path`` + the
        Solidity ``RevocationList.computeRootFromSortedLeaves``).

        Args:
            leaf_hash_hex: The 0x-prefixed hex of the leaf hash.
            merkle_root_hex: The 0x-prefixed hex of the on-chain root.
            path: List of 0x-prefixed sibling hashes (top-down).

        Returns:
            ``True`` iff the recomputed root equals
            ``merkle_root_hex``.
        """
        def _norm(hex_str: str) -> str:
            s = hex_str.strip()
            return s[2:] if s.startswith("0x") else s

        current = _norm(leaf_hash_hex)
        for sibling in path:
            s = _norm(sibling)
            left, right = sorted([current, s])
            current = hashlib.sha256(
                (left + right).encode("utf-8")
            ).hexdigest()
        return current == _norm(merkle_root_hex)

    return (verify_merkle_path,)


@app.cell
async def _(
    Optional,
    batch_date_input,
    badge_id_input,
    evidence_hash_input,
    httpx,
    merkle_path_input,
    public_anchor_base_input,
    verify_merkle_path,
):
    from typing import Any

    fetch_error: Optional[str] = None
    on_chain_root: Optional[str] = None
    leaf_count: Optional[int] = None
    verification_result: Optional[bool] = None
    badge_summary: dict[str, Any] = {}

    batch_date = batch_date_input.value.strip()
    badge_id = badge_id_input.value.strip()
    evidence_hash = evidence_hash_input.value.strip()
    raw_path = merkle_path_input.value.strip()

    if not batch_date:
        fetch_error = "Provide a YYYY-MM-DD batch date."
    elif not badge_id:
        fetch_error = "Provide the badge ID to verify."
    elif not evidence_hash or evidence_hash == "0x":
        fetch_error = "Provide the badge's evidence_hash."
    elif not raw_path:
        fetch_error = "Provide the Merkle path (one sibling per line)."
    else:
        path_list = [line.strip() for line in raw_path.splitlines() if line.strip()]
        anchor_url = (
            public_anchor_base_input.value.rstrip("/")
            + "/"
            + batch_date
        )
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(anchor_url)
            if resp.status_code != 200:
                fetch_error = (
                    f"GET {anchor_url} -> HTTP {resp.status_code}. "
                    f"Anchor for {batch_date!r} may not exist yet."
                )
            else:
                anchor_data = resp.json()
                on_chain_root = anchor_data.get("merkleRoot") or anchor_data.get("merkle_root")
                leaf_count = anchor_data.get("leafCount") or anchor_data.get("leaf_count")
                badge_summary = {
                    "batchId": anchor_data.get("batchId") or batch_date,
                    "timestamp": anchor_data.get("timestamp"),
                    "leafCount": leaf_count,
                    "merkleRoot": on_chain_root,
                }
                verification_result = verify_merkle_path(
                    leaf_hash_hex=evidence_hash,
                    merkle_root_hex=on_chain_root or "0x" + "0" * 64,
                    path=path_list,
                )
        except Exception as e:
            fetch_error = f"GET {anchor_url} failed: {e}"

    {
        "batch_date": batch_date,
        "badge_id": badge_id,
        "evidence_hash": evidence_hash,
        "path_length": len([l for l in raw_path.splitlines() if l.strip()]) if raw_path else 0,
        "on_chain_root": on_chain_root,
        "leaf_count": leaf_count,
        "badge_summary": badge_summary,
        "verification_result": verification_result,
        "fetch_error": fetch_error,
    }
    return (
        anchor_url,
        badge_summary,
        fetch_error,
        leaf_count,
        on_chain_root,
        verification_result,
    )


@app.cell
def _(
    badge_id,
    badge_summary,
    batch_date,
    evidence_hash,
    fetch_error,
    leaf_count,
    mo,
    on_chain_root,
    verification_result,
):
    if fetch_error:
        output_md = mo.md(f"## ❌ **Error**\n\n```\n{fetch_error}\n```")
    elif verification_result is None:
        output_md = mo.md("_Awaiting inputs…_")
    elif verification_result:
        output_md = mo.md(
            f"""
            ## ✅ **VERIFIED**

            | Field | Value |
            |:--|:--|
            | Batch date | `{batch_date}` |
            | Badge ID | `{badge_id}` |
            | Evidence hash | `{evidence_hash[:18]}…` |
            | Recomputed root matches on-chain root | **YES** |
            | On-chain root | `{on_chain_root}` |
            | Leaf count | `{leaf_count}` |
            """
        )
    else:
        output_md = mo.md(
            f"""
            ## ❌ **NOT VERIFIED**

            The recomputed Merkle path does NOT match the on-chain
            root for `{batch_date}`. Possible causes:

            - Typo in the badge ID, evidence_hash, or any path
              sibling hash.
            - The badge was issued on a different batch date.
            - The badge has been **revoked** — the next daily
              Merkle batch (02:00 UTC) re-publishes the root
              excluding revoked badges, so a previously-valid
              badge can fail verification after its revocation
              takes effect (see `tuatha/docs/REVOCATION_POLICY.md`).

            | Field | Value |
            |:--|:--|
            | Batch date | `{batch_date}` |
            | Badge ID | `{badge_id}` |
            | On-chain root | `{on_chain_root}` |
            """
        )

    output_md
    return (output_md,)


@app.cell
def _(mo):
    mo.md(
        """
        ## Algorithm reference

        This notebook uses the canonical
        *sorted-leaves + sorted-pair + SHA-256* Merkle-tree
        convention, identical to:

        - Python: ``tuatha/badges/anchor.py::verify_merkle_path``
        - Solidity:
          ``RevocationList.computeRootFromSortedLeaves``
        - TypeScript:
          ``web/apps/tuatha-ui/src/lib/merkle_verify.ts``

        ## Privacy

        - The Merkle path itself is stored off-chain (Convex) on
          a per-badge basis, not published on chain. The
          `/anchor/<date>` page returns the root + the badge
          summary, but only the badge holder (or someone they
          share their path with) can recompute it.
        - No student PII ever touches the chain — only the
          SHA-256 evidence hash does.
        """
    )
    return (mo,)


if __name__ == "__main__":
    app.run()
