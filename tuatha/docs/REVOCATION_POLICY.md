# Revocation Policy — Tuatha AchievementToken

> **The 24h propagation guarantee** for academic-misconduct
> revocations of SkillTreeBadges + the companion `AchievementToken`
> ERC20-shaped soulbound credential.

Per Layer 6 (P8) of
[`2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1`](../openspec/changes/2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1/proposal.md).

## The four-step revocation flow

1. **Operator trigger** —
   `tuatha/badges/ledger.py::revoke_badge(badge_id, reason)` is
   called (e.g. from a manual academic-misconduct finding workflow
   or from the future automated plagiarism sensor).
2. **Off-chain flag** — the `SkillTreeBadge.is_revoked = True` is
   set in Convex via `badges:setRevoked`.
3. **On-chain flag** —
   `RevocationList.revoke(evidenceHash, reason)` is called on the
   Base L2 `RevocationList` contract (the
   `tuatha/badges/ledger.py::_call_revocationlist_revoke` helper).
   Idempotent: re-revoking the same hash is a no-op except for an
   observability event.
4. **Daily Merkle batch** —
   the `daily_credential_anchor` Dagster asset runs at
   **02:00 UTC** the following day, rebuilds the day's Merkle
   tree over the *non-revoked* badge set, and publishes the new
   root via `CredAnchor.publish(batchId, newRoot, leafCount)`.

## The 24h propagation guarantee

Once `revoke_badge()` is called, the credential is **guaranteed
to appear revoked on the public `/anchor/<date>` verification page
within 24 hours**.

The SLA breakdown:

| Step | Max latency | Why |
|:--|:--|:--|
| Operator call → Convex flag | < 60s | Convex mutation latency |
| Convex flag → on-chain RevocationList | < 60s | web3.py transaction confirms in 1 block on Base L2 (~2s) + monitoring poll |
| On-chain RevocationList → next daily batch | < 24h | The 02:00 UTC cron is the worst-case clock |
| Daily batch → new `/anchor/<date>` page | < 60s | Convex mutation writes the new tx_hash back into each badge row |

The worst-case total wall-clock time from
`revoke_badge()` returning → the public page showing the new
excluded root is therefore **24 hours + ~3 minutes**.

### Why 24h (and not e.g. 5 minutes)?

The annual gas budget for a 24h-cadence daily anchor is
~$3.65 (Base L2 ≈ $0.01 / anchor × 365 days). A 5-minute cadence
would multiply this by ~288 (≈$1,050 / year) — and the Merkle
batch is mostly empty most of the time, so the higher cadence
wastes the operator's gas budget without a corresponding
verification-throughput benefit.

### Why is the policy 24h and not "instant"?

A *real-time* revocation surface (e.g. a multicallable per-badge
flag on the AchievementToken contract itself) would require every
balance query to read through a hot storage slot, gas-costing the
issuer for every read. The 24h-cadence batch amortises the cost
across the day's badge set, and the public verification page
(which is the only authoritative read surface for a third party)
is still authoritative within the SLA.

## What happens DURING the 24h window?

Between `revoke_badge()` returning and the next 02:00 UTC batch
publishing the new root, the badge's `is_revoked` flag IS set
on-chain (via `RevocationList.isRevoked(evidenceHash)`) and
the off-chain Convex row IS marked. So:

- **A direct `RevocationList.isRevoked(evidenceHash)` call from a
  verifier returns `true` immediately.** The verifier just needs
  to know to call this — it is part of the
  `AchievementToken._isRevoked` staticcall check that the public
  `/anchor/<date>` page surfaces as a post-verification status
  banner ("this evidenceHash has been revoked on
  `<block-timestamp>`").
- **The `/anchor/<date>` page for the batch BEFORE the
  revocation day still shows the revoked badge as part of the
  Merkle root** (because that root was already published). This
  is the load-bearing reason the policy documents a 24h window:
  there is a 24h window during which a badge can pass verification
  on the *prior* anchor (because the prior root still includes
  it) AND fail verification on the *current* anchor (because the
  new root excludes it).

## How a verifier should consume the page

The public `/anchor/<date>` page should always:

1. Fetch the on-chain Merkle root for the requested date.
2. Look up the badge's `evidence_hash` + its Merkle path.
3. Verify the path against the on-chain root (pass/fail).
4. **Cross-check the on-chain `RevocationList.isRevoked(evidenceHash)`** —
   if true, surface a "REVOKED" banner even when the path
   verification passed (the path may be valid for a now-revoked
   badge that was anchored in an earlier batch).

This dual check is what makes the verification surface
authoritative within the 24h window.

## Reference

- `tuatha/badges/ledger.py::revoke_badge` — the entry point.
- `tuatha/badges/ledger.py::fetch_unrevoked_badges_since` —
  the daily batch's badge fetcher (excludes revoked).
- `tuatha/dagster/anchor_assets.py::daily_credential_anchor` —
  the daily Merkle batch asset.
- `tuatha/contracts/RevocationList.sol` — the on-chain revocation
  list.
- `tuatha/contracts/AchievementToken.sol` — the companion
  soulbound token, with the `_isRevoked` staticcall modifier on
  `balanceOf` via `effectiveBalanceOf`.
- `tuatha/notebooks/38_merkle_verifier.py` — the marimo notebook
  for offline / 3rd-party verification.

## Changelog

- **2026-08-26** — initial policy (this document), per the
  `2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1`
  Layer 6 (P8) change.
