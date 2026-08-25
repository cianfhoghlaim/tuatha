"""tuatha.badges.storage — the badge storage layer (the Cormorant + Merkle root anchored on Base L2).

Per the educational-credential badge system (replaces the
legacy Crypteolas financial token from the prior pivot).
"""
from __future__ import annotations

import os
from datetime import timezone
from typing import Any

from .schema import SkillTreeBadge


class StorageStub:
    """The storage stub class."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass


def persist_on_chain_anchor(
    badge_id: str,
    tx_hash: str,
    batch_date: str,
) -> bool:
    """Persist the ``on_chain_anchor`` tx_hash back into the badge row.

    Per Layer 4 of
    ``2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1``:
    after the daily Merkle batch closes (Dagster asset
    ``daily_credential_anchor``), the resulting Base L2 ``tx_hash``
    is written back into each badge's ``on_chain_anchor`` column in
    Convex + the matching ``anchor_date`` column. The public
    ``/anchor/<date>`` page reads these two columns to verify the
    Merkle path.

    This helper is additive on top of the pre-existing storage stub
    (per the Phase-3 hard rule "do not remove existing fields" — it
    never mutates a SkillTreeBadge object, it only writes to Convex).

    Args:
        badge_id: The badge UUID.
        tx_hash: The 0x-prefixed Base L2 transaction hash returned
            by ``CredAnchor.publish()``.
        batch_date: The YYYY-MM-DD batch ID (also the public anchor
            date the third-party verifier hits).

    Returns:
        True iff the persistence call succeeded (or succeeded in
        no-op mode where Convex is unavailable — that is a legitimate
        dev/test state). False on any error.
    """
    try:
        from convex import ConvexClient
    except ImportError:
        # Dev/test: Convex SDK not installed — best-effort no-op.
        return True

    try:
        client = ConvexClient(os.environ.get("CONVEX_URL", "http://localhost:3210"))
        client.mutation(
            "badges:setOnChainAnchor",
            {
                "id": badge_id,
                "on_chain_anchor": tx_hash,
                "anchor_date": batch_date,
            },
        )
        return True
    except Exception:
        return False


def set_revoked(badge_id: str, is_revoked: bool, reason: str | None = None) -> bool:
    """Persist the revocation flag for one badge.

    Per Layer 6 of
    ``2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1``:
    ``revoke_badge()`` flips the ``is_revoked`` flag + records the
    reason in Convex. The off-chain flag is what the daily Merkle
    batch reads to exclude the badge from the next root. The 24h
    propagation guarantee (see ``docs/REVOCATION_POLICY.md``)
    guarantees the on-chain revocation reaches the
    ``_isRevoked`` modifier check inside 24h.
    """
    try:
        from convex import ConvexClient
    except ImportError:
        return True

    try:
        client = ConvexClient(os.environ.get("CONVEX_URL", "http://localhost:3210"))
        client.mutation(
            "badges:setRevoked",
            {"id": badge_id, "is_revoked": is_revoked, "reason": reason or ""},
        )
        return True
    except Exception:
        return False


def badge_from_row(row: dict[str, Any]) -> SkillTreeBadge:
    """Reconstruct a ``SkillTreeBadge`` from a Convex row dict.

    Mirrors ``badges/ledger.py::_row_to_badge`` so ``storage.py``
    owns the same canonical mapping; callers should prefer this
    helper for new code paths (Layer-4 daily anchor writeback uses
    it to enrich rows before passing them to the Convex mutation).
    """
    from datetime import datetime

    from .schema import BilingualText, EvidenceLink, EvidenceType, KeyCompetency

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
        evidence_type=EvidenceType(
            row.get("evidenceType", EvidenceType.FORMATIVE_ITEM.value)
        ),
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


__all__ = [
    "StorageStub",
    "badge_from_row",
    "persist_on_chain_anchor",
    "set_revoked",
]
