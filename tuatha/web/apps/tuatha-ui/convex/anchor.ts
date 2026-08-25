/**
 * web/apps/tuatha-ui/convex/anchor.ts
 *
 * Public anchor query + verification action for the
 * `/anchor/<date>` page. Per Layer 5 (P5) of
 * `2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1`.
 *
 * Two surfaces:
 *
 * 1. `getAnchorByDate` — returns the on-chain CredAnchor record
 *    (batchId, merkleRoot, timestamp, leafCount, txHash) for a
 *    given YYYY-MM-DD batch date. Pure read; no auth required.
 * 2. `verifyBadgeForDate` — given a `(badgeId, evidenceHash)`
 *    pair, looks up the badge's stored Merkle path and runs the
 *    verification against the on-chain root + the RevocationList.
 *
 * The Convex action delegates the Merkle-path verification to
 * the same algorithm used in the marimo notebook + the Python
 * ledger — sorted-leaves + sorted-pair + SHA-256, byte-for-byte
 * parity. The Solidity `RevocationList.isRevoked` staticcall is
 * the source of truth for the revocation cross-check.
 */

import { action, query } from "./_generated/server";
import { v } from "convex/values";
import {
  verifyMerklePath,
  type AnchorPageResult,
  type OnChainAnchor,
  type AnchorBadgeVerification,
} from "../src/lib/merkle_verify";

// --------------------------------------------------------------------------
// Public query: the on-chain anchor for a given date.
// --------------------------------------------------------------------------

/**
 * Look up the on-chain CredAnchor record for `batchDate`.
 *
 * Returns `null` when no anchor has been published for that date
 * (the daily batch has not yet completed, or the date is in the
 * future). The /anchor/[date].tsx route renders a friendly
 * "anchor not yet published" state when this happens.
 */
export const getAnchorByDate = query({
  args: {
    batchDate: v.string(), // YYYY-MM-DD
  },
  handler: async (ctx, args): Promise<OnChainAnchor | null> => {
    const row = await ctx.db
      .query("anchors")
      .withIndex("by_batchDate", (q) => q.eq("batchDate", args.batchDate))
      .first();

    if (!row) {
      return null;
    }

    return {
      batchId: row.batchDate,
      merkleRoot: row.merkleRoot,
      timestamp: row.timestamp,
      leafCount: row.leafCount,
      txHash: row.txHash,
    };
  },
});

// --------------------------------------------------------------------------
// Public action: verify a single badge against a date's anchor.
// --------------------------------------------------------------------------

/**
 * Verify one `(badgeId, evidenceHash)` pair against the on-chain
 * anchor for `batchDate`. The verification runs both the Merkle
 * path recomputation AND the on-chain RevocationList cross-check.
 *
 * Returns `null` when the anchor for `batchDate` does not exist.
 */
export const verifyBadgeForDate = action({
  args: {
    batchDate: v.string(), // YYYY-MM-DD
    badgeId: v.string(),
    evidenceHash: v.string(),
  },
  handler: async (
    ctx,
    args,
  ): Promise<AnchorBadgeVerification | null> => {
    // 1. Fetch the anchor.
    const anchor = await ctx.runQuery("anchors:getByBatchDate", {
      batchDate: args.batchDate,
    });
    if (!anchor) {
      return null;
    }

    // 2. Fetch the badge row + its Merkle path.
    const badge = await ctx.runQuery("badges:get", { id: args.badgeId });
    if (!badge || !badge.merklePath) {
      return null;
    }

    // 3. Fetch the revocation metadata (if any).
    const revocation = await ctx.runQuery("revocations:get", {
      evidenceHash: args.evidenceHash,
    });

    // 4. Run the Merkle-path verification.
    const result = await verifyMerklePath(
      args.evidenceHash,
      anchor.merkleRoot,
      badge.merklePath as string[],
    );

    // 5. Compose the result.
    const isRevoked = revocation !== null && revocation !== undefined;
    return {
      badgeId: args.badgeId,
      evidenceHash: args.evidenceHash,
      path: badge.merklePath as string[],
      merkleVerified: result.verified,
      isRevoked,
      revokedAt: revocation?.revokedAt,
      revocationReason: revocation?.reason,
      passes: result.verified && !isRevoked,
    };
  },
});

// --------------------------------------------------------------------------
// Public action: verify a whole batch (the canonical /anchor/<date> render).
// --------------------------------------------------------------------------

/**
 * Verify every badge for a given date at once. Returns the full
 * `AnchorPageResult` shape consumed by the
 * `/anchor/[date].tsx` route.
 *
 * If `badgeIds` is omitted, the action verifies every badge in
 * the batch (i.e. every Convex row whose `anchorDate == batchDate`
 * and whose `is_revoked == false`).
 */
export const verifyBatch = action({
  args: {
    batchDate: v.string(),
    badgeIds: v.optional(v.array(v.string())),
  },
  handler: async (ctx, args): Promise<AnchorPageResult | null> => {
    const anchor = await ctx.runQuery("anchors:getByBatchDate", {
      batchDate: args.batchDate,
    });
    if (!anchor) {
      return null;
    }

    const badges = args.badgeIds
      ? await ctx.runQuery("badges:listByIds", { ids: args.badgeIds })
      : await ctx.runQuery("badges:listByAnchorDate", {
          anchorDate: args.batchDate,
        });

    const verifications: AnchorBadgeVerification[] = [];
    let passing = 0;
    let failing = 0;

    for (const badge of badges) {
      if (!badge.merklePath) {
        continue;
      }
      const revocation = await ctx.runQuery("revocations:get", {
        evidenceHash: badge.evidenceHash,
      });
      const isRevoked = revocation !== null && revocation !== undefined;
      const result = await verifyMerklePath(
        badge.evidenceHash,
        anchor.merkleRoot,
        badge.merklePath as string[],
      );
      const passes = result.verified && !isRevoked;
      if (passes) {
        passing += 1;
      } else {
        failing += 1;
      }
      verifications.push({
        badgeId: badge._id,
        evidenceHash: badge.evidenceHash,
        path: badge.merklePath as string[],
        merkleVerified: result.verified,
        isRevoked,
        revokedAt: revocation?.revokedAt,
        revocationReason: revocation?.reason,
        passes,
      });
    }

    return {
      anchor,
      badgeVerifications: verifications,
      passingCount: passing,
      failingCount: failing,
      renderedAt: new Date().toISOString(),
    };
  },
});
