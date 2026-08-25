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
 * Case-insensitive (handles "0x", "0X").
 * @internal
 */
function stripHexPrefix(hex: string): string {
  const trimmed = hex.trim();
  if (trimmed.length >= 2 && trimmed[0] === "0" && (trimmed[1] === "x" || trimmed[1] === "X")) {
    return trimmed.slice(2);
  }
  return trimmed;
}

/**
 * Lowercase + strip the 0x prefix from a hex string.
 * @internal
 */
function normalizeHex(hex: string): string {
  return stripHexPrefix(hex).toLowerCase();
}

/**
 * Synchronous SHA-256 of a UTF-8 string. Returns bare hex (no 0x
 * prefix). Uses the Node `crypto` module when available; falls
 * back to a pure-JS implementation for browser environments.
 * @internal
 */
let _sha256SyncImpl: ((input: string) => string) | null = null;
function sha256Sync(input: string): string {
  if (_sha256SyncImpl === null) {
    // Lazy detection of the best available sync SHA-256 impl.
    try {
      // Node / Bun: use the built-in crypto module.
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      const nodeCrypto = require("node:crypto") as typeof import("node:crypto");
      _sha256SyncImpl = (s: string) =>
        nodeCrypto.createHash("sha256").update(s, "utf8").digest("hex");
    } catch {
      // Browser fallback: pure-JS SHA-256 implementation.
      _sha256SyncImpl = sha256SyncPureJs;
    }
  }
  return _sha256SyncImpl(input);
}

/**
 * Pure-JS SHA-256 implementation for browser environments where
 * `node:crypto` is unavailable. Returns bare hex (64 chars).
 * Based on FIPS 180-4 reference.
 * @internal
 */
function sha256SyncPureJs(input: string): string {
  // SHA-256 round constants.
  const K = new Uint32Array([
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
    0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
    0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
    0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
    0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
  ]);
  // Convert UTF-8 string to bytes.
  const bytes = new TextEncoder().encode(input);
  const bitLen = bytes.length * 8;
  // Pad the message: append 0x80, then zeros, then 64-bit big-endian length.
  const padLen = (((bytes.length + 9) + 63) & ~63) - bytes.length;
  const padded = new Uint8Array(bytes.length + padLen);
  padded.set(bytes);
  padded[bytes.length] = 0x80;
  // Append the bit length as a 64-bit big-endian integer.
  const view = new DataView(padded.buffer);
  // High 32 bits (we won't realistically hit 2^32 bits).
  view.setUint32(padded.length - 8, Math.floor(bitLen / 0x100000000), false);
  view.setUint32(padded.length - 4, bitLen >>> 0, false);
  // Initial hash values.
  const H = new Uint32Array([
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
  ]);
  const W = new Uint32Array(64);
  // Process each 512-bit chunk.
  for (let chunk = 0; chunk < padded.length; chunk += 64) {
    for (let i = 0; i < 16; i++) {
      W[i] = view.getUint32(chunk + i * 4, false);
    }
    for (let i = 16; i < 64; i++) {
      const s0 = (((W[i - 15] >>> 7) | (W[i - 15] << 25)) ^ ((W[i - 15] >>> 18) | (W[i - 15] << 14)) ^ (W[i - 15] >>> 3)) >>> 0;
      const s1 = (((W[i - 2] >>> 17) | (W[i - 2] << 15)) ^ ((W[i - 2] >>> 19) | (W[i - 2] << 13)) ^ (W[i - 2] >>> 10)) >>> 0;
      W[i] = (W[i - 16] + s0 + W[i - 7] + s1) >>> 0;
    }
    let [a, b, c, d, e, f, g, h] = H;
    for (let i = 0; i < 64; i++) {
      const S1 = (((e >>> 6) | (e << 26)) ^ ((e >>> 11) | (e << 21)) ^ ((e >>> 25) | (e << 7))) >>> 0;
      const ch = ((e & f) ^ (~e & g)) >>> 0;
      const t1 = (h + S1 + ch + K[i] + W[i]) >>> 0;
      const S0 = (((a >>> 2) | (a << 30)) ^ ((a >>> 13) | (a << 19)) ^ ((a >>> 22) | (a << 10))) >>> 0;
      const mj = ((a & b) ^ (a & c) ^ (b & c)) >>> 0;
      const t2 = (S0 + mj) >>> 0;
      h = g;
      g = f;
      f = e;
      e = (d + t1) >>> 0;
      d = c;
      c = b;
      b = a;
      a = (t1 + t2) >>> 0;
    }
    H[0] = (H[0] + a) >>> 0;
    H[1] = (H[1] + b) >>> 0;
    H[2] = (H[2] + c) >>> 0;
    H[3] = (H[3] + d) >>> 0;
    H[4] = (H[4] + e) >>> 0;
    H[5] = (H[5] + f) >>> 0;
    H[6] = (H[6] + g) >>> 0;
    H[7] = (H[7] + h) >>> 0;
  }
  // Concatenate the hash words into a hex string.
  let hex = "";
  for (let i = 0; i < 8; i++) {
    hex += H[i].toString(16).padStart(8, "0");
  }
  return hex;
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
  return verifyMerklePathSync(leafHashHex, onChainRoot, path);
}

/**
 * Synchronous Merkle-path verification. Uses the Node `crypto`
 * module when available; falls back to a pure-JS SHA-256 in the
 * browser. The async `verifyMerklePath` is a thin wrapper around
 * this function.
 */
export function verifyMerklePathSync(
  leafHashHex: string,
  onChainRoot: string,
  path: readonly string[],
): MerkleVerificationResult {
  const target = normalizeHex(onChainRoot);
  let current = normalizeHex(leafHashHex);

  for (const sibling of path) {
    const s = normalizeHex(sibling);
    // Canonical ordering: min(left, right) + max(left, right).
    const [left, right] =
      current <= s ? [current, s] : [s, current];
    const pair = left + right;
    current = sha256Sync(pair);
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
  const out: AnchorBadgeVerification[] = [];
  let passing = 0;
  let failing = 0;

  for (const b of badgeVerificationsInput) {
    const revocation = revocationMap.get(b.evidenceHash.toLowerCase());
    const isRevoked = revocation !== undefined;
    const result = verifyMerklePathSync(
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
