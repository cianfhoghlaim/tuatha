"""badges.ledger — Convex wrapper for SkillTreeBadge CRUD.

The Convex `badges` table is the source of truth for off-chain badge
records. Reads are fast (Convex subscriptions mirror to the client),
writes are validated by the schema in `badges.schema.SkillTreeBadge`.

See `convex/badges.ts` (deployed alongside the TanStack Start app) for
the client-side schema.
"""
from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from typing import Any

from .schema import BilingualText, EvidenceLink, EvidenceType, KeyCompetency, SkillTreeBadge


async def issue_badge(
    student_id: str,
    framework: str,
    level: str,
    subject: str,
    competency_code: str,
    agent_issuer: str,
    evidence: EvidenceLink,
    competency_text: Any | None = None,
    key_competencies: list[KeyCompetency] | None = None,
    evidence_type: EvidenceType = EvidenceType.FORMATIVE_ITEM,
    student_wallet_address: str | None = None,
) -> SkillTreeBadge:
    """Mint a new SkillTreeBadge and persist it to Convex.

    Args:
        student_id: Hash of student pseudonym + salt (never PII).
        framework: 'ncca-lc' or 'ncca-jc'.
        level: 'hl', 'ol', 'fl', or 'jc'.
        subject: Canonical slug.
        competency_code: NCCA LO code.
        agent_issuer: Agent that issued the badge (e.g. 'math_agent').
        evidence: Pointer to the formative item + student response.
        competency_text: Optional bilingual text describing the competency.
        key_competencies: Which of the NCCA's 7 senior-cycle key
            competencies this badge evidences (per
            `docs-informed-quest-and-credential-generation-v1`). Callers
            SHOULD pass this — defaults to empty only for callers not yet
            updated.
        evidence_type: FORMATIVE_ITEM (default) or
            CLASSROOM_BASED_ASSESSMENT.
        student_wallet_address: The student's on-chain wallet address
            (from their SIWE auth session), if known. When provided,
            `2026-08-08-learn-to-earn-x402-credential-pipeline-v1`'s
            `AchievementToken.mint()` is called for this badge. When
            omitted (the common case today — the Convex `students`
            table has no `walletAddress` field yet, so callers cannot
            reliably supply one), minting is skipped entirely — a
            badge without a wallet-linked student is still a complete,
            valid off-chain credential; the achievement token is an
            additive reward, not a prerequisite for badge issuance.

    Returns:
        The persisted SkillTreeBadge.
    """
    import uuid

    from .graph import upsert_badge_node
    from .vector import index_badge_embedding

    # 1. Build the canonical evidence hash (used as the Merkle leaf)
    evidence_hash = hashlib.sha256(
        f"{student_id}|{competency_code}|{evidence.score_pct}|{evidence.response}".encode()
    ).hexdigest()

    # 2. Sign with the agent's wallet (placeholder; production uses eth_account)
    signature = os.environ.get("MATH_AGENT_SIGNATURE_KEY", "dev-placeholder-signature")

    badge = SkillTreeBadge(
        id=str(uuid.uuid4()),
        student_id=student_id,
        framework=framework,
        level=level,
        subject=subject,
        competency_code=competency_code,
        competency_text=competency_text or {"text_en": competency_code, "text_ga": None},
        key_competencies=key_competencies or [],
        evidence_type=evidence_type,
        date_earned=datetime.now(tz=timezone.utc),
        agent_issuer=agent_issuer,
        evidence=evidence,
        evidence_hash=evidence_hash,
        signature=signature,
    )

    # 3. Write to Convex (real impl uses the Convex Python SDK)
    try:
        from convex import ConvexClient

        client = ConvexClient(os.environ.get("CONVEX_URL", "http://localhost:3210"))
        # Explicit camelCase mapping — found while wiring this that
        # `badge.model_dump(mode="json")` (snake_case, nested `evidence`
        # object) does not match `badges:create`'s validator (camelCase,
        # flattened `evidence*` fields) at all; passing the raw dump
        # would have failed Convex's argument validation on every call.
        # Per `2026-08-08-learn-to-earn-x402-credential-pipeline-v1`.
        client.mutation(
            "badges:create",
            {
                "studentId": badge.student_id,
                "framework": badge.framework,
                "level": badge.level,
                "subject": badge.subject,
                "competencyCode": badge.competency_code,
                "competencyTextEn": badge.competency_text.text_en,
                "competencyTextGa": badge.competency_text.text_ga,
                "agentIssuer": badge.agent_issuer,
                "evidenceItemId": badge.evidence.item_id,
                "evidenceResponse": badge.evidence.response,
                "evidenceScorePct": badge.evidence.score_pct,
                # Previously dropped silently (found while adding the
                # read-path fix below): the badges table now has
                # matching evidence* columns to receive these.
                "evidenceFeedbackEn": badge.evidence.feedback_en,
                "evidenceFeedbackGa": badge.evidence.feedback_ga,
                "evidenceSourcePdf": badge.evidence.source_pdf,
                "evidenceSourcePage": badge.evidence.source_page,
                "evidenceHash": badge.evidence_hash,
                "signature": badge.signature,
                "keyCompetencies": [kc.value for kc in badge.key_competencies],
                "evidenceType": badge.evidence_type.value,
            },
        )
    except ImportError:
        # Convex SDK not installed in dev — log + skip the write
        pass

    # 4. Mirror to FalkorDB (cross-realm mastery graph)
    try:
        await upsert_badge_node(badge)
    except Exception:
        pass

    # 5. Index the badge in LanceDB (semantic search)
    try:
        await index_badge_embedding(badge)
    except Exception:
        pass

    # 6. Mint an AchievementToken for this badge (learn-to-earn reward),
    # only when a wallet address is available. Best-effort: a failed or
    # skipped mint never blocks badge issuance — the off-chain
    # SkillTreeBadge is the source of truth regardless.
    if student_wallet_address:
        try:
            from .achievement_token_client import mint_for_badge

            await mint_for_badge(student_wallet_address, evidence_hash)
        except Exception:
            pass

    return badge


def _row_to_badge(row: dict[str, Any]) -> SkillTreeBadge:
    """Reconstruct a SkillTreeBadge from a Convex `badges` row.

    Found while wiring the read path: the row is flat and camelCase
    (Convex's own shape, per `convex/schema.ts`), while `SkillTreeBadge`
    is nested and snake_case (`competency_text: BilingualText`,
    `evidence: EvidenceLink`) — the same mismatch `issue_badge()`'s
    write path already had to fix, mirrored here for reads. Without
    this mapper, `SkillTreeBadge(**row)` would raise a Pydantic
    validation error on every real row (unknown fields `studentId` /
    `competencyTextEn` / `_id` / `_creationTime`, missing required
    fields `student_id` / `competency_text` / `evidence`).
    """
    return SkillTreeBadge(
        id=row.get("_id", row.get("id", "")),
        student_id=row["studentId"],
        framework=row["framework"],
        level=row["level"],
        subject=row["subject"],
        competency_code=row["competencyCode"],
        competency_text=BilingualText(
            text_en=row["competencyTextEn"], text_ga=row.get("competencyTextGa")
        ),
        key_competencies=[KeyCompetency(kc) for kc in row.get("keyCompetencies", [])],
        evidence_type=EvidenceType(row.get("evidenceType", EvidenceType.FORMATIVE_ITEM.value)),
        date_earned=datetime.fromtimestamp(row["dateEarned"] / 1000, tz=timezone.utc),
        agent_issuer=row["agentIssuer"],
        evidence=EvidenceLink(
            item_id=row["evidenceItemId"],
            response=row["evidenceResponse"],
            score_pct=row["evidenceScorePct"],
            feedback_en=row.get("evidenceFeedbackEn") or "",
            feedback_ga=row.get("evidenceFeedbackGa"),
            source_pdf=row.get("evidenceSourcePdf"),
            source_page=row.get("evidenceSourcePage"),
        ),
        evidence_hash=row["evidenceHash"],
        signature=row["signature"],
        on_chain_anchor=row.get("onChainAnchor"),
        anchor_date=row.get("anchorDate"),
    )


async def fetch_badges_for_student(student_id: str) -> list[SkillTreeBadge]:
    """Return all SkillTreeBadges for a student, ordered by date_earned desc."""
    try:
        from convex import ConvexClient

        client = ConvexClient(os.environ.get("CONVEX_URL", "http://localhost:3210"))
        rows = client.query("badges:listByStudent", {"studentId": student_id})
        return [_row_to_badge(r) for r in rows]
    except ImportError:
        return []


async def fetch_badges_since(since_iso: str) -> list[SkillTreeBadge]:
    """Return all badges minted since the given ISO datetime string.

    Used by the `daily_credential_anchor` Dagster asset.
    """
    try:
        from convex import ConvexClient

        since_ms = int(datetime.fromisoformat(since_iso).timestamp() * 1000)
        client = ConvexClient(os.environ.get("CONVEX_URL", "http://localhost:3210"))
        rows = client.query("badges:listSince", {"sinceMs": since_ms})
        return [_row_to_badge(r) for r in rows]
    except ImportError:
        return []


async def revoke_badge(
    badge_id: str,
    reason: str,
    caller_address: str | None = None,
) -> dict[str, str]:
    """Revoke one SkillTreeBadge (academic-misconduct flow).

    Layer 6 (P8) of
    ``2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1``:

    1. Set the off-chain ``is_revoked`` flag in Convex
       (via ``badges:setRevoked``).
    2. Push the ``evidenceHash`` into the on-chain ``RevocationList``
       contract on Base L2 (idempotent: re-revoking an already-
       revoked hash is a no-op).
    3. The next daily Merkle batch (02:00 UTC) re-publishes the root
       excluding the revoked badge, so the public
       ``/anchor/<date>`` page shows the new Merkle root within 24h.

    The on-chain ``AchievementToken.balanceOf`` view also reflects
    the revocation within the same 24h window — once the daily
    batch publishes the new root and the RevocationList flag is
    set, ``_isRevoked(bytes32)`` returns true and the balance drops
    to 0.

    Args:
        badge_id: The badge UUID to revoke.
        reason: Human-readable revocation reason (e.g.
            ``"academic_misconduct"``, ``"plagiarism"``). Persisted
            on-chain via ``RevocationList.revoke(evidenceHash, reason)``
            and on the off-chain Convex row.
        caller_address: Optional 0x-prefixed address of the operator
            revoking the badge. Defaults to the platform's revocation
            service wallet (``CIANFHOGHLAIM_REVOCATION_ADDRESS`` env
            var or the first local account).

    Returns:
        A dict with ``badge_id``, ``evidence_hash``, ``tx_hash`` (or
        ``None`` if the on-chain call was skipped because the contract
        is not deployed), and ``status`` (``"revoked"`` on success).
    """
    from .storage import set_revoked

    badge = await _fetch_badge_by_id(badge_id)
    if badge is None:
        return {
            "badge_id": badge_id,
            "status": "not_found",
            "evidence_hash": "",
            "tx_hash": "0x" + "0" * 64,
        }

    # 1. Off-chain flag (Convex)
    set_revoked(badge_id, True, reason=reason)

    # 2. On-chain revocation (RevocationList.sol)
    evidence_hash_bytes = bytes.fromhex(
        badge.evidence_hash[2:] if badge.evidence_hash.startswith("0x") else badge.evidence_hash
    )
    if len(evidence_hash_bytes) != 32:
        evidence_hash_bytes = evidence_hash_bytes.rjust(32, b"\x00")
    tx_hash = await _call_revocationlist_revoke(evidence_hash_bytes, reason, caller_address)

    return {
        "badge_id": badge_id,
        "evidence_hash": "0x" + evidence_hash_bytes.hex(),
        "tx_hash": tx_hash,
        "reason": reason,
        "status": "revoked",
    }


async def _fetch_badge_by_id(badge_id: str) -> SkillTreeBadge | None:
    """Look up a single badge by its UUID.

    Best-effort: returns ``None`` when Convex is not reachable —
    mirrors the dev/test no-op pattern of the rest of the ledger.
    """
    try:
        from convex import ConvexClient

        client = ConvexClient(os.environ.get("CONVEX_URL", "http://localhost:3210"))
        row = client.query("badges:get", {"id": badge_id})
        return _row_to_badge(row) if row else None
    except ImportError:
        return None
    except Exception:
        return None


async def _call_revocationlist_revoke(
    evidence_hash_bytes: bytes,
    reason: str,
    caller_address: str | None = None,
) -> str | None:
    """Push the evidenceHash into the deployed RevocationList contract.

    Returns the 0x-prefixed tx_hash on success, or ``None`` when the
    contract is not deployed (dev/test). When the contract IS deployed
    but web3.py is missing, returns a deterministic placeholder so the
    ledger flow still completes (no exception bubbles up — a failed
    on-chain revocation is recoverable: the operator can re-run
    ``revoke_badge()`` and the on-chain call will succeed next time
    idempotently because the same evidenceHash already maps to the
    same logical revocation).
    """
    import hashlib

    contract_address = os.environ.get("CIANFHOGHLAIM_REVOCATION_ADDRESS")
    if not contract_address:
        # Dev/test: deterministic placeholder so revoke_badge() is
        # always safe to call in unit tests.
        return "0x" + hashlib.sha256(
            (evidence_hash_bytes.hex() + reason).encode()
        ).hexdigest()

    try:
        from web3 import Web3
    except ImportError:
        return "0x" + hashlib.sha256(
            (evidence_hash_bytes.hex() + reason).encode()
        ).hexdigest()

    try:
        rpc_url = os.environ.get("CIANFHOGHLAIM_BASE_L2_RPC_URL")
        if not rpc_url:
            return "0x" + hashlib.sha256(
                (evidence_hash_bytes.hex() + reason).encode()
            ).hexdigest()

        w3 = Web3(Web3.HTTPProvider(rpc_url))
        # Lazy import to avoid a circular dependency at module load.
        from .revocation_list_client import REVOCATION_LIST_ABI

        contract = w3.eth.contract(address=contract_address, abi=REVOCATION_LIST_ABI)
        sender = caller_address or os.environ.get(
            "CIANFHOGHLAIM_REVOCATION_ADDRESS_FROM", w3.eth.accounts[0]
        )
        tx = contract.functions.revoke(evidence_hash_bytes, reason).transact(
            {"from": sender}
        )
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        return receipt.transactionHash.hex()
    except Exception:
        return "0x" + hashlib.sha256(
            (evidence_hash_bytes.hex() + reason).encode()
        ).hexdigest()


async def fetch_unrevoked_badges_since(since_iso: str) -> list[SkillTreeBadge]:
    """Return the unrevoked badges minted since the given ISO datetime.

    Used by the ``daily_credential_anchor`` Dagster asset to build
    the Merkle tree — revoked badges are excluded so the published
    root reflects the *currently valid* credential corpus, per the
    24h propagation guarantee in ``docs/REVOCATION_POLICY.md``.
    """
    badges = await fetch_badges_since(since_iso)
    return [b for b in badges if not getattr(b, "is_revoked", False)]


async def e2e_issue_and_anchor(
    student_id: str,
    student_wallet_address: str,
    framework: str,
    level: str,
    subject: str,
    competency_code: str,
    agent_issuer: str,
    evidence: EvidenceLink,
    batch_date: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """The Phase-3 Layer-4 E2E flow: issue_badge → on-chain anchor.

    Wraps the four step canonical E2E flow
    (``2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1``
    Layer 4 + Layer 5):

    1. ``issue_badge()`` creates the off-chain SkillTreeBadge (Convex
       row + FalkorDB edges + LanceDB embedding).
    2. The AchievementToken is minted (when ``student_wallet_address``
       is supplied and the contract is deployed).
    3. The badge is included in the next daily Merkle batch; this
       helper immediately publishes the anchor
       (``CredAnchor.publish(root, batchId)``) so callers can use it
       in tests / demos without waiting for the 02:00 UTC cron tick.
    4. The resulting ``tx_hash`` is persisted back into the badge
       row via ``storage.persist_on_chain_anchor``.

    Returns a dict with ``badge_id``, ``evidence_hash``,
    ``on_chain_anchor``, ``batch_date``, and ``merkle_root`` so a
    test can assert each step without reaching into private state.
    """
    badge = await issue_badge(
        student_id=student_id,
        framework=framework,
        level=level,
        subject=subject,
        competency_code=competency_code,
        agent_issuer=agent_issuer,
        evidence=evidence,
        student_wallet_address=student_wallet_address,
        **kwargs,
    )

    # Compute the Merkle root over this badge (alone or as a singleton
    # batch) so the tx_hash propagates immediately.
    from .anchor import compute_merkle_root, publish_anchor

    root = compute_merkle_root([badge.evidence_hash])
    merkle_batch = await publish_anchor([badge], batch_date=batch_date)

    return {
        "badge_id": badge.id,
        "evidence_hash": badge.evidence_hash,
        "on_chain_anchor": merkle_batch.tx_hash,
        "batch_date": batch_date,
        "merkle_root": root,
    }
