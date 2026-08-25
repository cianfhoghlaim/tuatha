/**
 * web/apps/tuatha-ui/src/lib/merkle_verify.ts
 *
 * Server-side Merkle-path recomputation for the public
 * `/anchor/<date>` verification page. Per Layer 5 (P5) of
 * `2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1`.
 *
 * Mirrors the algorithm used by:
 *   - Python `tuatha/badges/anchor.py::verify_merkle_path`
 *   - Solidity `RevocationList.computeRootFromSortedLeaves`
 *   - marimo `tuatha/notebooks/38_merkle_verifier.py::verify_merkle_path`
 *
 * Convention: sorted-leaves + sorted-pair + SHA-256. At each
 * level, the pair is sorted lexicographically (i.e.
 * `SHA256(min(left, right) + max(left, right))`). This means a
 * `position` flag is NOT needed in the path — the path itself is
 * just the sibling hashes in top-down order.
 *
 * The path is provided off-chain (Convex `badges` row → Merkle
 * path column) — never published on chain. Only the Merkle root
 * + the leaf hashes (via the `/anchor/<date>` page) are public.
 */

/**
 * The canonical Merkle path verification result.
 */
export interface MerkleVerificationResult {
  /** True iff the recomputed root equals the on-chain root. */
  readonly verified: boolean;
  /** The recomputed Merkle root (for the verifier UI). */
  readonly recomputedRoot: string;
  /** The on-chain root provided by the caller (for parity check). */
  readonly onChainRoot: string;
  /** The badge ID provided by the caller (echoed for the UI). */
  readonly badgeId: string;
}

/**
 * Strip a 0x prefix from a hex string, normalising to bare hex.
 * @internal
 */
function stripHexPrefix(hex: string): string {
  const trimmed = hex.trim();
  return trimmed.startsWith("0x") ? trimmed.slice(2) : trimmed;
}

/**
 * Lowercase + strip the 0x prefix from a hex string.
 * @internal
 */
function normalizeHex(hex: string): string {
  return stripHexPrefix(hex).toLowerCase();
}

/**
 * Recompute the Merkle path and compare against the on-chain root.
 *
 * Algorithm: at each level, sort the pair lexicographically,
 * concatenate, hash with SHA-256. The final hash must equal
 * `onChainRoot`.
 *
 * @param leafHashHex  The 0x-prefixed hex of the leaf hash.
 * @param onChainRoot  The 0x-prefixed hex of the on-chain root.
 * @param path         The top-down list of sibling hashes
 *                     (each 0x-prefixed hex).
 * @returns The MerkleVerificationResult, including the
 *          recomputed root for display.
 *
 * Example:
 * ```ts
 * const r = await verifyMerklePath(
 *   "0xabc...",
 *   "0xdef...",
 *   ["0x123...", "0x456..."],
 * );
 * if (r.verified) {
 *   console.log("VERIFIED");
 * }
 * ```
 */
export async function verifyMerklePath(
  leafHashHex: string,
  onChainRoot: string,
  path: readonly string[],
): Promise<MerkleVerificationResult> {
  const target = normalizeHex(onChainRoot);
  let current = normalizeHex(leafHashHex);

  for (const sibling of path) {
    const s = normalizeHex(sibling);
    // Canonical ordering: min(left, right) + max(left, right).
    const [left, right] =
      current <= s ? [current, s] : [s, current];
    const pair = left + right;
    const bytes = new TextEncoder().encode(pair);
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    current = Array.from(new Uint8Array(digest))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  }

  return {
    verified: current === target,
    recomputedRoot: "0x" + current,
    onChainRoot: "0x" + target,
    badgeId: "",
  };
}

/**
 * The standard on-chain Merkle root shape returned by the
 * public anchor query (mirrors the Python
 * `tuatha/badges/schema.py::CredentialAnchor`).
 */
export interface OnChainAnchor {
  /** The YYYY-MM-DD batch ID. */
  readonly batchId: string;
  /** The 0x-prefixed 32-byte Merkle root. */
  readonly merkleRoot: string;
  /** The block timestamp on Base L2 (seconds since epoch). */
  readonly timestamp: number;
  /** The number of leaves (badges) included in the batch. */
  readonly leafCount: number;
  /** The 0x-prefixed Base L2 tx_hash of the publish call. */
  readonly txHash: string;
}

/**
 * Result of the per-badge verification, enriched with the
 * post-revocation cross-check against the RevocationList.
 */
export interface AnchorBadgeVerification {
  /** The badge ID (Convex UUID). */
  readonly badgeId: string;
  /** The 0x-prefixed evidence_hash of the badge. */
  readonly evidenceHash: string;
  /** The Merkle path of sibling hashes (top-down). */
  readonly path: readonly string[];
  /** True iff the Merkle proof passes. */
  readonly merkleVerified: boolean;
  /** True iff the evidence_hash is revoked on the RevocationList. */
  readonly isRevoked: boolean;
  /** Wall-clock UTC ISO timestamp at which this badge was revoked (if applicable). */
  readonly revokedAt?: string;
  /** Human-readable revocation reason (if applicable). */
  readonly revocationReason?: string;
  /** True iff the verification should be considered PASS overall
   *  (merkleVerified AND NOT isRevoked). */
  readonly passes: boolean;
}

/**
 * The full per-batch verification surface — the canonical shape
 * returned by the public `/anchor/<date>` page.
 */
export interface AnchorPageResult {
  readonly anchor: OnChainAnchor;
  readonly badgeVerifications: readonly AnchorBadgeVerification[];
  /** Aggregate pass count for the UI's summary line. */
  readonly passingCount: number;
  /** Aggregate fail count for the UI's summary line. */
  readonly failingCount: number;
  /** Wall-clock UTC ISO timestamp at which this page was rendered. */
  readonly renderedAt: string;
}

/**
 * Compute the per-batch verification result for the public
 * `/anchor/<date>` page. Pure function: no I/O. The Convex
 * `anchor:verifyBatch` query supplies the inputs.
 *
 * @param anchor          The on-chain anchor + the per-badge path.
 * @param revocationMap   evidenceHash -> revocation metadata (empty
 *                        when no revocations recorded for this date).
 * @returns The per-batch verification result.
 */
export function computeAnchorPageResult(
  anchor: OnChainAnchor,
  badgeVerificationsInput: readonly Omit<
    AnchorBadgeVerification,
    "merkleVerified" | "passes" | "isRevoked" | "revokedAt" | "revocationReason"
  >[],
  revocationMap: ReadonlyMap<
    string,
    { revokedAt: string; reason: string }
  > = new Map(),
): AnchorPageResult {
  return computeAnchorPageResultAsync(
    anchor,
    badgeVerificationsInput,
    revocationMap,
  );
}

/**
 * Async variant — used when the verification runs in the browser
 * (the marimo notebook + the TanStack Start route both call this).
 *
 * @param anchor            The on-chain anchor.
 * @param badges            The badge paths to verify.
 * @param revocationMap     Evidence-hash revocation metadata.
 */
export async function computeAnchorPageResultAsync(
  anchor: OnChainAnchor,
  badges: readonly Omit<
    AnchorBadgeVerification,
    "merkleVerified" | "passes" | "isRevoked" | "revokedAt" | "revocationReason"
  >[],
  revocationMap: ReadonlyMap<
    string,
    { revokedAt: string; reason: string }
  > = new Map(),
): Promise<AnchorPageResult> {
  const out: AnchorBadgeVerification[] = [];
  let passing = 0;
  let failing = 0;

  for (const b of badges) {
    const revocation = revocationMap.get(b.evidenceHash.toLowerCase());
    const isRevoked = revocation !== undefined;
    const result = await verifyMerklePath(
      b.evidenceHash,
      anchor.merkleRoot,
      b.path,
    );
    const passes = result.verified && !isRevoked;
    if (passes) {
      passing += 1;
    } else {
      failing += 1;
    }
    out.push({
      badgeId: b.badgeId,
      evidenceHash: b.evidenceHash,
      path: b.path,
      merkleVerified: result.verified,
      isRevoked,
      revokedAt: revocation?.revokedAt,
      revocationReason: revocation?.reason,
      passes,
    });
  }

  return {
    anchor,
    badgeVerifications: out,
    passingCount: passing,
    failingCount: failing,
    renderedAt: new Date().toISOString(),
  };
}
