# Spec Delta: learn-to-earn-token-credential

## ADDED Requirements

### Requirement: Soulbound AchievementToken end-to-end flow

The system SHALL provide `AchievementToken` (`tuatha/contracts/
AchievementToken.sol`), an ERC20-shaped contract with `name`,
`symbol`, `decimals`, `totalSupply`, and `balanceOf` for wallet/
explorer compatibility, that mints `MINT_AMOUNT_PER_BADGE` tokens to a
student's wallet only when triggered by a real, verified badge
issuance (`tuatha/badges/ledger.py::issue_badge()`), capped at
`MAX_SUPPLY`. The contract SHALL be structurally non-transferable —
`transfer`, `transferFrom`, and `approve` SHALL all revert
unconditionally — so the token functions as a soulbound achievement
record, not a spendable or tradeable currency. The contract SHALL NOT
implement staking, lending, a DEX, or prediction-market functionality.

The `tuatha/badges/ledger.py::issue_badge()` function SHALL wire the
full E2E flow:
1. Create the off-chain `SkillTreeBadge` row in Convex
2. Create the FalkorDB `SkillTreeBadge` node + edges to the
   player's profile node and to the LO node
3. Persist the `on_chain_anchor` tx_hash back into the Convex
   badge row
4. Enqueue the badge for the next daily Merkle batch (02:00 UTC)

The daily Merkle batch runs via the `daily_credential_anchor`
Dagster asset (`tuatha/dagster/anchor_assets.py`), which:
1. Computes the Merkle root of the day's badges
2. Calls `CredAnchor.publish(root, batchId)` on Base L2
3. Writes the resulting `tx_hash` back into each badge row in
   Convex

#### Scenario: Token minted on real badge issuance

- **GIVEN** a student with a connected wallet address completes a
  formative item and earns a `SkillTreeBadge` with
  `evidence_hash = "0xabc..."`
- **WHEN** `issue_badge()` completes and a wallet address was supplied
- **THEN** `AchievementToken.mint(student, evidenceHash)` is called
- **AND** the student's on-chain balance increases by
  `MINT_AMOUNT_PER_BADGE`
- **AND** a second `mint()` call with the same `evidenceHash` reverts
  (idempotent against retries)

#### Scenario: Token cannot be transferred

- **GIVEN** a student holds a nonzero `AchievementToken` balance
- **WHEN** any address calls `transfer`, `transferFrom`, or `approve`
  on the contract
- **THEN** the call reverts unconditionally
- **AND** no balance changes as a result

#### Scenario: Mint fails gracefully without a wallet on file

- **GIVEN** a student has earned a badge but has no `walletAddress` on
  their Convex `students` row (no SIWE auth flow exists yet)
- **WHEN** `issue_badge()` runs
- **THEN** the off-chain `SkillTreeBadge` is still created successfully
- **AND** the `AchievementToken.mint()` call is skipped entirely,
  logged as a no-op, and does not raise

#### Scenario: Daily Merkle anchor published on Base L2

- **GIVEN** the `daily_credential_anchor` Dagster asset runs at
  02:00 UTC
- **WHEN** there are ≥1 new badges since the last anchor
- **THEN** the asset computes the Merkle root of the new badges
- **AND** the asset calls `CredAnchor.publish(root, batchId)` on
  Base L2
- **AND** the asset writes the resulting `tx_hash` back into each
  badge row in Convex

#### Scenario: Third party verifies a badge via the public anchor page

- **GIVEN** a badge with `id = "uuid"`, `evidence_hash = "0x..."`,
  `on_chain_anchor = "0x..."` (Base L2 tx_hash), and
  `anchor_date = "2026-07-01"`
- **WHEN** a third party visits `/anchor/2026-07-01` and enters the
  badge's `id + evidence_hash`
- **THEN** the page displays the Merkle root published on Base L2
- **AND** the page accepts the badge's `id + evidence_hash` and
  verifies the Merkle path against the on-chain root
- **AND** the verification result is a clear pass/fail indicator

### Requirement: AchievementToken revocation list

The system SHALL provide `RevocationList` (`tuatha/contracts/
RevocationList.sol`), a companion contract that maintains an
on-chain list of revoked `evidenceHash` values. The
`AchievementToken` contract SHALL extend the base contract with a
`_isRevoked(bytes32 evidenceHash)` modifier on `balanceOf`, so that
revoked badges do not contribute to the holder's balance. The
revocation flow is:

1. `tuatha/badges/ledger.py::revoke_badge(badge_id, reason)` is
   called (academic-misconduct finding)
2. The off-chain `SkillTreeBadge.is_revoked = True` flag is set in
   Convex
3. `RevocationList.revoke(evidenceHash, reason)` is called on Base L2
4. The next daily Merkle batch re-publishes the root excluding the
   revoked badge (the Merkle tree is rebuilt over the non-revoked
   set)

The 24h propagation guarantee is documented in
`tuatha/docs/REVOCATION_POLICY.md`.

#### Scenario: Revoked badge does not contribute to balance

- **GIVEN** a student holds a `SkillTreeBadge` with
  `evidence_hash = "0xabc..."` and the badge is not revoked
- **WHEN** the student calls `AchievementToken.balanceOf(student)`
- **THEN** the balance reflects `MINT_AMOUNT_PER_BADGE`

- **WHEN** `revoke_badge(badge_id, reason="academic_misconduct")`
  completes
- **AND** the next daily Merkle batch runs at 02:00 UTC
- **THEN** `AchievementToken.balanceOf(student)` returns 0
  (the revoked badge no longer contributes)
- **AND** the public `/anchor/<date>` page shows the new Merkle
  root excluding the revoked badge within 24h