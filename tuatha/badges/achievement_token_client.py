"""badges.achievement_token_client — async bridge from `ledger.py` to the
deployed `AchievementToken` contract.

`tuatha/contracts/achievement_token.py` is a synchronous, web3.py-based
module (mirroring `cred_anchor.py`'s style); `ledger.py::issue_badge()`
is async. This thin wrapper reads the deployed contract address from env
config and runs the synchronous mint call in a thread, so a slow/blocked
RPC call never stalls the badge-issuance event loop.

Per `2026-08-08-learn-to-earn-x402-credential-pipeline-v1`,
extended per `2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1`
to expose a direct `mint(student, evidence_hash)` wrapper that
mirrors the on-chain `AchievementToken.mint(address student, bytes32
evidenceHash)` selector — so a caller can invoke the mint path with
no Convex/FalkorDB plumbing.
"""
from __future__ import annotations

import asyncio
import os


async def mint_for_badge(student_wallet_address: str, evidence_hash: str) -> str | None:
    """Mint achievement tokens for a badge's evidence_hash.

    Returns the transaction hash on success, or None if minting is not
    configured (no deployed contract address / no minter key / web3.py
    not installed) — all of which are legitimate, expected states in
    dev/test environments, not errors.
    """
    contract_address = os.environ.get("CIANFHOGHLAIM_ACHIEVEMENT_TOKEN_ADDRESS")
    if not contract_address:
        return None

    evidence_hash_hex = evidence_hash if evidence_hash.startswith("0x") else f"0x{evidence_hash}"

    def _mint() -> str:
        from tuatha.contracts.achievement_token import mint_achievement

        return mint_achievement(
            contract_address=contract_address,
            student_address=student_wallet_address,
            evidence_hash_hex=evidence_hash_hex,
        )

    return await asyncio.to_thread(_mint)


async def mint(student: str, evidence_hash: str) -> str | None:
    """Mint AchievementToken for one ``(student, evidence_hash)`` pair.

    Direct wrapper around the on-chain ``mint(address, bytes32)``
    selector — equivalent to ``mint_for_badge`` but renamed so the
    Python call site matches the Solidity selector, per the
    Layer-4 P2 implementation in
    ``2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1``.

    Idempotent: re-minting the same ``evidence_hash`` reverts on
    chain (the ``mintedForEvidence`` mapping already marks it as
    minted). In dev/test where the contract is not deployed, returns
    ``None`` rather than raising — mirroring the legitimate
    "contract not configured" branch of ``mint_for_badge``.

    Args:
        student: 0x-prefixed wallet address of the student.
        evidence_hash: SHA-256 hex string of the badge evidence
            (either ``0x``-prefixed or bare hex). Will be normalised
            to ``0x`` + 64 hex chars before the on-chain call.

    Returns:
        The 0x-prefixed transaction hash on success, or ``None`` when
        the contract is not deployed (dev/test mode).
    """
    contract_address = os.environ.get("CIANFHOGHLAIM_ACHIEVEMENT_TOKEN_ADDRESS")
    if not contract_address:
        return None

    return await mint_for_badge(student, evidence_hash)


__all__ = ["mint", "mint_for_badge"]
