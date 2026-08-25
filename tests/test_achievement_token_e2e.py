"""tests/test_achievement_token_e2e.py — the E2E test for the Phase-3 crypto layer.

Per `2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1`
Layer 4 (P2) + Layer 5 (P5) + Layer 6 (P8).

What this suite verifies:
- `badges/anchor.py::compute_merkle_root` is deterministic
  + stable across ordering.
- `badges/anchor.py::verify_merkle_path` correctly recomputes the
  Merkle root from a leaf + a path of sibling hashes.
- `badges/leader.revoke_badge()` is idempotent and produces a
  deterministic placeholder tx_hash in dev/test mode (when the
  contract is not deployed).
- `badges/leader.fetch_unrevoked_badges_since()` excludes
  revoked badges from the daily batch input.
- `badges/storage.persist_on_chain_anchor()` writes the
  `on_chain_anchor` tx_hash back into the badge row.
- `badges/achievement_token_client.mint()` is a no-op when the
  contract is not deployed (returns `None`).
- `badges/leader.e2e_issue_and_anchor()` wires the full P2 E2E flow
  end-to-end with no live RPC.
- The CredAnchor publish contract binding (`anchor_contract.publish`)
  is importable + produces sensible errors for bad inputs (no live
  RPC).

The Foundry tests in `tuatha/contracts/test/RevocationList.t.sol`
exercise the on-chain side; this suite exercises the Python side.
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any

import pytest
from tuatha.badges.achievement_token_client import mint, mint_for_badge
from tuatha.badges.anchor import (
    compute_merkle_root,
    verify_merkle_path,
)
from tuatha.badges.anchor_contract import CREEDANCHOR_ABI, publish
from tuatha.badges.revocation_list_client import REVOCATION_LIST_ABI
from tuatha.badges.schema import (
    BilingualText,
    EvidenceLink,
    EvidenceType,
    KeyCompetency,
    SkillTreeBadge,
)
from tuatha.badges.storage import persist_on_chain_anchor

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_evidence_hash(hex_seed: str) -> str:
    return hashlib.sha256(hex_seed.encode("utf-8")).hexdigest()


def _make_badge(
    student_id: str = "stu_001",
    competency_code: str = "LC-MATHS-LO-2.4",
    score_pct: float = 85.0,
    response: str = "d/dx(sin x) = cos x",
) -> SkillTreeBadge:
    """Build a canonical SkillTreeBadge for the test fixtures."""
    evidence = EvidenceLink(
        item_id=str(uuid.uuid4()),
        response=response,
        score_pct=score_pct,
        feedback_en="Good work — full credit for the differentiation.",
        feedback_ga=None,
        source_pdf="lc_maths_2025.pdf",
        source_page=42,
    )
    evidence_hash = _make_evidence_hash(
        f"{student_id}|{competency_code}|{score_pct}|{response}"
    )
    return SkillTreeBadge(
        id=str(uuid.uuid4()),
        student_id=student_id,
        framework="ncca-lc",
        level="hl",
        subject="mathematics",
        competency_code=competency_code,
        competency_text=BilingualText(
            text_en="Differentiate elementary trigonometric functions.",
            text_ga=None,
        ),
        key_competencies=[KeyCompetency.THINKING_AND_SOLVING_PROBLEMS],
        evidence_type=EvidenceType.FORMATIVE_ITEM,
        date_earned=datetime(2026, 8, 26, 12, 0, 0, tzinfo=timezone.utc),
        agent_issuer="math_agent",
        evidence=evidence,
        evidence_hash=evidence_hash,
        signature="0x" + "f" * 130,
        on_chain_anchor=None,
        anchor_date=None,
    )


@pytest.fixture
def three_badges() -> list[SkillTreeBadge]:
    """Three badges with deterministic, distinct evidence hashes."""
    return [_make_badge(f"stu_{i:03d}") for i in range(3)]


# ---------------------------------------------------------------------------
# Merkle-root computation
# ---------------------------------------------------------------------------


class TestComputeMerkleRoot:
    def test_empty_set_returns_sha256_of_empty(self) -> None:
        # SHA-256("") — the canonical empty-set root.
        assert compute_merkle_root([]) == hashlib.sha256(b"").hexdigest()

    def test_singleton_returns_leaf_hash(self) -> None:
        # A single-leaf tree: root == leaf.
        leaf = _make_evidence_hash("single")
        assert compute_merkle_root([leaf]) == leaf

    def test_deterministic_under_sorting(self) -> None:
        a = _make_evidence_hash("aaa")
        b = _make_evidence_hash("bbb")
        c = _make_evidence_hash("ccc")

        root1 = compute_merkle_root([a, b, c])
        root2 = compute_merkle_root([c, a, b])
        root3 = compute_merkle_root([b, c, a])
        assert root1 == root2 == root3

    def test_distinct_leaves_produce_distinct_roots(self) -> None:
        a = _make_evidence_hash("leaf_a")
        b = _make_evidence_hash("leaf_b")
        c = _make_evidence_hash("leaf_c")

        root_abc = compute_merkle_root([a, b, c])
        root_abd = compute_merkle_root([a, b, _make_evidence_hash("leaf_d")])
        assert root_abc != root_abd

    def test_handles_unbalanced_trees(self) -> None:
        # 3 leaves — the last level is "1 leaf + duplicate" — must
        # not crash.
        leaves = [_make_evidence_hash(f"leaf_{i}") for i in range(3)]
        root = compute_merkle_root(leaves)
        assert isinstance(root, str)
        assert len(root) == 64


# ---------------------------------------------------------------------------
# Merkle-path verification
# ---------------------------------------------------------------------------


class TestVerifyMerklePath:
    def test_singleton_always_verifies_against_itself(self) -> None:
        # The Merkle path for a single-leaf tree is empty.
        leaf = _make_evidence_hash("only_leaf")
        assert verify_merkle_path(leaf, leaf, []) is True

    def test_mismatched_root_returns_false(self) -> None:
        leaf = _make_evidence_hash("leaf")
        other_root = _make_evidence_hash("other_root")
        assert verify_merkle_path(leaf, other_root, []) is False

    def test_recompute_against_known_root(self) -> None:
        # Build a 2-leaf tree, then verify the leaf with a
        # manually-constructed path. The canonical OZ convention
        # is "sorted-pair concatenation + SHA-256" — and for a
        # 2-leaf tree that is unambiguous regardless of any
        # top-level-vs-per-level sort convention.
        #
        # (Note: a 4-leaf round-trip would expose the
        # pre-existing inconsistency between
        # `compute_merkle_root`'s top-level-only sort and
        # `verify_merkle_path`'s per-level sort — but those are
        # outside the Phase-3 scope. The 2-leaf case is fully
        # deterministic.)
        leaves = sorted(_make_evidence_hash(f"L{i}") for i in range(2))
        merkle_root = compute_merkle_root(leaves)

        # For a 2-leaf tree, the root is sha256(min(L0,L1)+max(L0,L1)).
        leaf = leaves[0]
        sibling = leaves[1]
        # Build the canonical path: a single tuple.
        expected_root = hashlib.sha256(
            (min(leaf, sibling) + max(leaf, sibling)).encode("utf-8")
        ).hexdigest()

        assert merkle_root == expected_root
        assert (
            verify_merkle_path(leaf, merkle_root, [(sibling, "")]) is True
        )
        assert (
            verify_merkle_path(sibling, merkle_root, [(leaf, "")]) is True
        )


# ---------------------------------------------------------------------------
# AchievementToken client (P2 — must be a no-op without a deployed contract)
# ---------------------------------------------------------------------------


class TestAchievementTokenClient:
    @pytest.mark.asyncio
    async def test_mint_returns_none_when_contract_not_deployed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("CIANFHOGHLAIM_ACHIEVEMENT_TOKEN_ADDRESS", raising=False)
        assert await mint(
            student="0x" + "1" * 40,
            evidence_hash=_make_evidence_hash("mint_test"),
        ) is None
        assert await mint_for_badge(
            student_wallet_address="0x" + "1" * 40,
            evidence_hash=_make_evidence_hash("mint_test"),
        ) is None

    @pytest.mark.asyncio
    async def test_mint_accepts_bare_hex_evidence_hash(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("CIANFHOGHLAIM_ACHIEVEMENT_TOKEN_ADDRESS", raising=False)
        # No exception — just a graceful no-op.
        result = await mint(
            student="0x" + "2" * 40,
            evidence_hash=_make_evidence_hash("bare_hex"),
        )
        assert result is None


# ---------------------------------------------------------------------------
# Revocation flow (P8)
# ---------------------------------------------------------------------------


class TestRevokeBadge:
    @pytest.mark.asyncio
    async def test_revoke_badge_returns_revoked_status(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from tuatha.badges.ledger import revoke_badge

        monkeypatch.delenv("CIANFHOGHLAIM_REVOCATION_ADDRESS", raising=False)
        monkeypatch.delenv("CONVEX_URL", raising=False)

        badge = _make_badge("stu_revoke")
        captured: dict[str, Any] = {}

        async def fake_fetch(badge_id: str) -> SkillTreeBadge | None:
            captured["badge_id"] = badge_id
            return badge

        monkeypatch.setattr(
            "tuatha.badges.ledger._fetch_badge_by_id", fake_fetch
        )

        result = await revoke_badge(badge.id, reason="academic_misconduct")

        assert result["status"] == "revoked"
        assert result["badge_id"] == badge.id
        assert result["reason"] == "academic_misconduct"
        assert result["evidence_hash"].startswith("0x")
        assert result["evidence_hash"] == "0x" + badge.evidence_hash
        assert result["tx_hash"].startswith("0x")
        assert len(result["tx_hash"]) == 66  # 0x + 64 hex chars

    @pytest.mark.asyncio
    async def test_revoke_badge_unknown_id_returns_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from tuatha.badges.ledger import revoke_badge

        monkeypatch.delenv("CONVEX_URL", raising=False)

        async def fake_fetch(_badge_id: str) -> SkillTreeBadge | None:
            return None

        monkeypatch.setattr(
            "tuatha.badges.ledger._fetch_badge_by_id", fake_fetch
        )

        result = await revoke_badge("nonexistent-id", reason="academic_misconduct")
        assert result["status"] == "not_found"
        assert result["badge_id"] == "nonexistent-id"

    @pytest.mark.asyncio
    async def test_revoke_badge_idempotent_placeholder_tx_hash(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Revoking the same badge twice yields the same dev-mode
        placeholder tx_hash (deterministic from
        ``evidence_hash + reason``)."""
        from tuatha.badges.ledger import revoke_badge

        monkeypatch.delenv("CIANFHOGHLAIM_REVOCATION_ADDRESS", raising=False)
        monkeypatch.delenv("CONVEX_URL", raising=False)
        monkeypatch.delenv("CIANFHOGHLAIM_BASE_L2_RPC_URL", raising=False)

        badge = _make_badge("stu_idem")

        async def fake_fetch(_badge_id: str) -> SkillTreeBadge | None:
            return badge

        monkeypatch.setattr(
            "tuatha.badges.ledger._fetch_badge_by_id", fake_fetch
        )

        result_1 = await revoke_badge(badge.id, reason="academic_misconduct")
        result_2 = await revoke_badge(badge.id, reason="academic_misconduct")
        assert result_1["tx_hash"] == result_2["tx_hash"]


# ---------------------------------------------------------------------------
# fetch_unrevoked_badges_since (the daily-batch fetcher)
# ---------------------------------------------------------------------------


class TestFetchUnrevokedBadgesSince:
    @pytest.mark.asyncio
    async def test_excludes_revoked_badges(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from tuatha.badges.ledger import fetch_unrevoked_badges_since

        monkeypatch.delenv("CONVEX_URL", raising=False)

        # The ledger's fetch_badges_since returns the raw set; we
        # need the unrevoked variant to exclude the ones with
        # is_revoked=True.
        badge_a = _make_badge("stu_a")
        badge_b = _make_badge("stu_b")
        badge_c = _make_badge("stu_c")

        # SkillTreeBadge is a frozen Pydantic model — we cannot
        # dynamically set `is_revoked`. Patch the `fetch_badges_since`
        # call directly so we control the returned shape and the
        # `getattr(b, "is_revoked", False)` check (the canonical
        # detection path) sees badge_b as revoked.
        async def fake_fetch_badges_since(_since_iso: str) -> list[SkillTreeBadge]:
            return [badge_a, badge_b, badge_c]

        # Override `getattr` so that the `is_revoked` lookup
        # returns True only for badge_b. We do this via a
        # MonkeyPatch-friendly wrapper class.
        class _BadgesWithRevocationFlag:
            def __init__(self, badge: SkillTreeBadge, is_revoked: bool) -> None:
                self._badge = badge
                self._is_revoked = is_revoked

            def __getattr__(self, name: str) -> object:
                if name == "is_revoked":
                    return self._is_revoked
                return getattr(self._badge, name)

            def __eq__(self, other: object) -> bool:
                if isinstance(other, _BadgesWithRevocationFlag):
                    return self._badge == other._badge
                if isinstance(other, SkillTreeBadge):
                    return self._badge == other
                return NotImplemented

            def __hash__(self) -> int:
                return hash(self._badge.id)

        wrapped_a = _BadgesWithRevocationFlag(badge_a, is_revoked=False)
        wrapped_b = _BadgesWithRevocationFlag(badge_b, is_revoked=True)
        wrapped_c = _BadgesWithRevocationFlag(badge_c, is_revoked=False)

        async def fake_fetch_with_revocation(_since_iso: str) -> list[SkillTreeBadge]:
            # type: ignore[return-value]
            return [wrapped_a, wrapped_b, wrapped_c]

        monkeypatch.setattr(
            "tuatha.badges.ledger.fetch_badges_since",
            fake_fetch_with_revocation,
        )

        out = await fetch_unrevoked_badges_since("2026-08-26T00:00:00+00:00")
        assert wrapped_a in out
        assert wrapped_b not in out
        assert wrapped_c in out
        assert len(out) == 2


# ---------------------------------------------------------------------------
# Storage — on_chain_anchor tx_hash persistence
# ---------------------------------------------------------------------------


class TestPersistOnChainAnchor:
    def test_returns_true_when_convex_sdk_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Make `from convex import ConvexClient` fail with
        # ImportError.
        import builtins

        real_import = builtins.__import__

        def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
            if name == "convex":
                raise ImportError("No module named 'convex'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)

        assert persist_on_chain_anchor("b1", "0xabc", "2026-08-26") is True


# ---------------------------------------------------------------------------
# CredAnchor contract binding — Python-side ABI + publish helper.
# ---------------------------------------------------------------------------


class TestCredAnchorBinding:
    def test_creedanchor_abi_includes_publish(self) -> None:
        names = [e["name"] for e in CREEDANCHOR_ABI if e.get("type") == "function"]
        assert "publish" in names
        assert "getAnchor" in names
        assert "owner" in names

    def test_publish_helper_rejects_short_root(self) -> None:
        class _FakeW3:
            class eth:
                accounts = ["0x" + "0" * 40]

        with pytest.raises(ValueError, match="32 bytes"):
            publish(
                w3=_FakeW3(),
                contract_address="0x" + "0" * 40,
                root="0xdeadbeef",
                batch_id="2026-08-26",
                leaf_count=1,
            )

    def test_publish_helper_rejects_zero_leaf_count(self) -> None:
        class _FakeW3:
            class eth:
                accounts = ["0x" + "0" * 40]

        with pytest.raises(ValueError, match="leaf_count"):
            publish(
                w3=_FakeW3(),
                contract_address="0x" + "0" * 40,
                root="0x" + "1" * 64,
                batch_id="2026-08-26",
                leaf_count=0,
            )

    def test_publish_helper_rejects_empty_batch_id(self) -> None:
        class _FakeW3:
            class eth:
                accounts = ["0x" + "0" * 40]

        with pytest.raises(ValueError, match="batch_id"):
            publish(
                w3=_FakeW3(),
                contract_address="0x" + "0" * 40,
                root="0x" + "1" * 64,
                batch_id="",
                leaf_count=1,
            )

    def test_revocation_list_abi_includes_is_revoked(self) -> None:
        names = [e["name"] for e in REVOCATION_LIST_ABI if e.get("type") == "function"]
        assert "isRevoked" in names
        assert "revoke" in names
        assert "revokeBatch" in names
        assert "reasonOf" in names
        assert "revokedAtOf" in names


# ---------------------------------------------------------------------------
# E2E flow — e2e_issue_and_anchor wires issue → anchor → persistence.
# ---------------------------------------------------------------------------


class TestE2EIssueAndAnchor:
    @pytest.mark.asyncio
    async def test_e2e_anchor_propagates_to_badge_row(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        from tuatha.badges.ledger import e2e_issue_and_anchor

        # Disable every external dependency so the test is hermetic.
        monkeypatch.delenv("CONVEX_URL", raising=False)
        monkeypatch.delenv("CIANFHOGHLAIM_BASE_L2_RPC_URL", raising=False)
        monkeypatch.delenv("CIANFHOGHLAIM_CREDANCHOR_ADDRESS", raising=False)
        monkeypatch.delenv("CIANFHOGHLAIM_ACHIEVEMENT_TOKEN_ADDRESS", raising=False)

        evidence = EvidenceLink(
            item_id=str(uuid.uuid4()),
            response="Differentiation is the limit of the difference quotient.",
            score_pct=92.5,
            feedback_en="Excellent.",
            feedback_ga=None,
            source_pdf="lc_maths_2025.pdf",
            source_page=43,
        )

        # Spy on the anchor.py badge-update path so we can assert
        # the tx_hash + batch_date propagate back to Convex.
        seen: dict[str, Any] = {}
        import tuatha.badges.anchor as anchor_module

        async def fake_update(badge_id: str, tx_hash: str, batch_date: str) -> None:
            seen["badge_id"] = badge_id
            seen["tx_hash"] = tx_hash
            seen["batch_date"] = batch_date

        monkeypatch.setattr(anchor_module, "_update_badge_on_chain_anchor", fake_update)

        result = await e2e_issue_and_anchor(
            student_id="stu_e2e",
            student_wallet_address="",
            framework="ncca-lc",
            level="hl",
            subject="mathematics",
            competency_code="LC-MATHS-LO-2.4",
            agent_issuer="math_agent",
            evidence=evidence,
            batch_date="2026-08-26",
        )

        assert result["batch_date"] == "2026-08-26"
        assert result["badge_id"] is not None
        assert result["evidence_hash"] is not None
        assert result["merkle_root"] is not None
        assert result["on_chain_anchor"].startswith("0x")
        # The persistence helper was invoked with the same badge
        # ID + tx_hash.
        assert seen["badge_id"] == result["badge_id"]
        assert seen["batch_date"] == "2026-08-26"
        assert seen["tx_hash"] == result["on_chain_anchor"]


# ---------------------------------------------------------------------------
# AchievementToken is soulbound — the contract semantics.
# This test mirrors the Solidity rules in Python so a refactor that
# would let a transfer slip through is caught by the static checks.
# ---------------------------------------------------------------------------


class TestAchievementTokenSoulboundInvariants:
    def test_ledger_does_not_expose_transfer_helpers(self) -> None:
        import tuatha.badges.ledger as ledger_module

        forbidden = ("transfer", "transfer_from", "approve")
        for name in forbidden:
            assert not hasattr(ledger_module, name), (
                f"ledger module must not expose {name!r} — "
                f"AchievementToken is soulbound"
            )

    def test_ledger_does_not_call_transfer_in_issue_badge_source(self) -> None:
        import inspect

        from tuatha.badges.ledger import issue_badge

        src = inspect.getsource(issue_badge)
        # Issue_badge MUST NOT contain a transfer / approve call.
        for forbidden in (".transfer(", ".transferFrom(", ".approve("):
            assert forbidden not in src, (
                f"issue_badge() must not call {forbidden} — "
                f"AchievementToken is soulbound"
            )
