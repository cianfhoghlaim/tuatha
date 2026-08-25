// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.20;

/**
 * @title RevocationList
 * @notice Cianfhoghlaim Educational MMO — the on-chain revocation list
 *         for Soulbound AchievementTokens.
 * @dev Companion contract to `AchievementToken.sol` (per
 *      `2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1`,
 *      Layer 6 / P8).
 *
 *      Holds the on-chain authoritative list of revoked
 *      `evidenceHash` values. The flow:
 *
 *      1. `tuatha/badges/ledger.py::revoke_badge(badge_id, reason)`
 *         is called on academic-misconduct findings.
 *      2. The off-chain `SkillTreeBadge.is_revoked = True` flag is
 *         set in Convex.
 *      3. `RevocationList.revoke(evidenceHash, reason)` is called
 *         here (Base L2).
 *      4. The next daily Merkle batch (02:00 UTC, run by
 *         `daily_credential_anchor`) rebuilds the root over the
 *         non-revoked badge set and re-publishes the new Merkle
 *         root to `CredAnchor.publish(batchId, newRoot, leafCount)`.
 *
 *      AchievementToken's `effectiveBalanceOf` is intentionally a
 *      stub returning 0 — the post-revocation *authoritative*
 *      balance is the Merkle-root-verified sum across the
 *      non-revoked badge set, surfaced via the public
 *      `/anchor/<date>` verification page. See
 *      `tuatha/docs/REVOCATION_POLICY.md` for the 24h propagation
 *      guarantee.
 *
 *      Storage model:
 *      - `revoked[evidenceHash]` mapping — O(1) check
 *      - `revocationReasons[evidenceHash]` — the human-readable
 *        reason string per revoked hash (academic-misconduct,
 *        plagiarism, etc.)
 *      - `revokedAt[evidenceHash]` — the block timestamp of the
 *        revocation (for the audit trail + the 24h SLA)
 *      - The full list of currently-revoked hashes is also
 *        enumerable via `revokedAtIndex(index)` (push-only; we
 *        never un-revoke a credential).
 *
 *      Idempotent: re-revoking the same evidenceHash is a no-op
 *      (the existing entry is preserved + a no-op event is emitted).
 *      This matters because `issue_badge()` + `revoke_badge()` may
 *      both be re-run safely (retry semantics) without producing
 *      duplicate events or breaking off-chain analytics.
 *
 *      Merkle-tree format:
 *      Sorted-leaves + sorted-pair concatenation + keccak256 hashing
 *      — the canonical OpenZeppelin MerkleTree convention. The
 *      Solidity helper `computeRootFromSortedLeaves` matches the
 *      Python `tuatha/badges/anchor.py::compute_merkle_root` byte-
 *      for-byte (after substituting SHA-256 → keccak256, which the
 *      Python helper accepts via a hashlib override — see the
 *      tuatha/notebooks/38_merkle_verifier.py marimo notebook for
 *      the off-chain verification demo).
 *
 *      Reference:
 *      - openspec/changes/2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1/
 *      - tuatha/badges/ledger.py (the revoke caller)
 *      - tuatha/contracts/AchievementToken.sol (the sibling token contract)
 *      - tuatha/contracts/CredAnchor.sol (the sibling anchor contract)
 *      - tuatha/docs/REVOCATION_POLICY.md (the 24h propagation SLA)
 */
contract RevocationList {
    /// @notice evidenceHash -> true iff this credential has been revoked.
    mapping(bytes32 => bool) public revoked;

    /// @notice evidenceHash -> the human-readable revocation reason.
    mapping(bytes32 => string) public revocationReasons;

    /// @notice evidenceHash -> the block timestamp of the revocation.
    mapping(bytes32 => uint256) public revokedAt;

    /// @notice Append-only enumeration of all currently-revoked hashes.
    ///         We never remove from this list (a credential is never
    ///         un-revoked — academic-misconduct findings stick).
    bytes32[] public revokedList;

    /// @notice Total number of distinct revocations ever recorded.
    uint256 public totalRevocations;

    /// @notice The contract owner (the platform's revocation service wallet).
    address public owner;

    event Revoked(
        bytes32 indexed evidenceHash,
        string reason,
        address indexed revokedBy,
        uint256 timestamp
    );

    event RevocationReplayed(
        bytes32 indexed evidenceHash,
        address indexed replayedBy,
        uint256 timestamp
    );

    event OwnerRotated(address indexed previousOwner, address indexed newOwner);

    modifier onlyOwner() {
        require(msg.sender == owner, "RevocationList: caller is not the owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /**
     * @notice Revoke one SkillTreeBadge's underlying evidenceHash.
     *         Idempotent: re-revoking an already-revoked hash is a
     *         no-op (the existing reason + timestamp are preserved,
     *         only `RevocationReplayed` is emitted for observability).
     * @param evidenceHash  The SkillTreeBadge's evidence_hash (the
     *                      same value used as the Merkle leaf in
     *                      CredAnchor + the mint key in
     *                      AchievementToken).
     * @param reason        A short human-readable reason string
     *                      (e.g. "academic_misconduct"). Persisted
     *                      for the audit trail.
     */
    function revoke(bytes32 evidenceHash, string calldata reason) external onlyOwner {
        require(evidenceHash != bytes32(0), "RevocationList: evidenceHash required");
        if (revoked[evidenceHash]) {
            // Idempotent — re-revoking is a no-op except for an
            // observability event. Preserves the original reason +
            // timestamp (the audit trail is monotonic).
            emit RevocationReplayed(evidenceHash, msg.sender, block.timestamp);
            return;
        }

        revoked[evidenceHash] = true;
        revocationReasons[evidenceHash] = reason;
        revokedAt[evidenceHash] = block.timestamp;
        revokedList.push(evidenceHash);
        totalRevocations += 1;

        emit Revoked(evidenceHash, reason, msg.sender, block.timestamp);
    }

    /**
     * @notice Batch revocation. Useful for the academic-misconduct
     *         backfill flow (a single misconduct finding that
     *         invalidates a cohort's badges). Each evidenceHash is
     *         revoked individually under the same idempotent
     *         semantics as `revoke()`.
     * @param evidenceHashes  The batch of evidenceHashes to revoke.
     * @param reason          The shared reason string for the batch.
     */
    function revokeBatch(
        bytes32[] calldata evidenceHashes,
        string calldata reason
    ) external onlyOwner {
        for (uint256 i = 0; i < evidenceHashes.length; i++) {
            bytes32 evidenceHash = evidenceHashes[i];
            if (evidenceHash == bytes32(0)) {
                continue;
            }
            if (revoked[evidenceHash]) {
                emit RevocationReplayed(evidenceHash, msg.sender, block.timestamp);
                continue;
            }
            revoked[evidenceHash] = true;
            revocationReasons[evidenceHash] = reason;
            revokedAt[evidenceHash] = block.timestamp;
            revokedList.push(evidenceHash);
            totalRevocations += 1;
            emit Revoked(evidenceHash, reason, msg.sender, block.timestamp);
        }
    }

    /**
     * @notice Read whether an evidenceHash is revoked. Cheap view
     *         call (no event emission) used by the daily Merkle
     *         batch to exclude revoked hashes + by the public
     *         `/anchor/<date>` verification page to surface the
     *         post-revocation balance.
     */
    function isRevoked(bytes32 evidenceHash) external view returns (bool) {
        return revoked[evidenceHash];
    }

    /**
     * @notice Read the human-readable reason for a revocation.
     *         Returns the empty string when the hash is not revoked.
     */
    function reasonOf(bytes32 evidenceHash) external view returns (string memory) {
        return revocationReasons[evidenceHash];
    }

    /**
     * @notice Read the block timestamp at which a revocation
     *         occurred. Returns 0 when the hash is not revoked.
     */
    function revokedAtOf(bytes32 evidenceHash) external view returns (uint256) {
        return revokedAt[evidenceHash];
    }

    /**
     * @notice Return the i-th revoked evidenceHash in insertion
     *         order. For the public verification UI to iterate the
     *         full list. O(n) reads only; not used by the daily
     *         Merkle batch hot path (which uses `isRevoked`).
     */
    function revokedAtIndex(uint256 index) external view returns (bytes32) {
        return revokedList[index];
    }

    /**
     * @notice Total count of currently-revoked hashes. Equivalent
     *         to `revokedList.length` but exposed as its own view
     *         for symmetry with `totalRevocations`.
     */
    function revokedCount() external view returns (uint256) {
        return revokedList.length;
    }

    /**
     * @notice Compute the Merkle root of a sorted-leaves array
     *         using the canonical OpenZeppelin MerkleTree pattern
     *         (sorted-pair concatenation + keccak256). This matches
     *         the Python `tuatha/badges/anchor.py::compute_merkle_root`
     *         helper byte-for-byte when the Python helper is
     *         configured to use keccak256 instead of SHA-256.
     *
     *         Use case: a Foundry unit test that wants to mirror
     *         the off-chain root computation; the daily Merkle
     *         batch itself is computed off-chain and published
     *         via `CredAnchor.publish()`, but having an on-chain
     *         verifier lets Solidity tests assert the algorithm.
     *
     * @param sortedLeaves  The leaf hashes, in ascending lexicographic
     *                      order (the same order the off-chain batch
     *                      sorts them in).
     * @return root         The Merkle root.
     */
    function computeRootFromSortedLeaves(
        bytes32[] memory sortedLeaves
    ) external pure returns (bytes32 root) {
        uint256 n = sortedLeaves.length;
        if (n == 0) {
            return bytes32(0);
        }
        if (n == 1) {
            return sortedLeaves[0];
        }

        // OpenZeppelin MerkleTree convention: each parent =
        // keccak256(min(left, right) || max(left, right)). This
        // matches the Python `verify_merkle_path` helper exactly.
        bytes32[] memory level = sortedLeaves;
        while (level.length > 1) {
            bytes32[] memory next = new bytes32[]((level.length + 1) / 2);
            uint256 j = 0;
            for (uint256 i = 0; i < level.length; i += 2) {
                bytes32 left = level[i];
                bytes32 right = (i + 1 < level.length) ? level[i + 1] : left;
                bytes32 lo = (uint256(left) <= uint256(right)) ? left : right;
                bytes32 hi = (uint256(left) <= uint256(right)) ? right : left;
                next[j++] = keccak256(abi.encodePacked(lo, hi));
            }
            // shrink next[] to its actual length
            assembly {
                mstore(next, j)
            }
            level = next;
        }
        root = level[0];
    }

    /**
     * @notice Rotate the contract owner.
     * @param newOwner  The new owner address.
     */
    function rotateOwner(address newOwner) external onlyOwner {
        require(newOwner != address(0), "RevocationList: newOwner is zero address");
        emit OwnerRotated(owner, newOwner);
        owner = newOwner;
    }

    /**
     * @notice Transfer ownership (alias for rotateOwner, matches
     *         the OpenZeppelin Ownable convention used by the
     *         sibling contracts).
     * @param newOwner  The new owner address.
     */
    function transferOwnership(address newOwner) external onlyOwner {
        this.rotateOwner(newOwner);
    }
}
