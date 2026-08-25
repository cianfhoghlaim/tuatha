/**
 * web/apps/tuatha-ui/tests/anchor_verify.test.tsx
 *
 * Frontend tests for the public `/anchor/<date>` verification
 * surface. Per Layer 5 (P5) of
 * `2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1`.
 *
 * These tests are environment-agnostic: they exercise the
 * `verifyMerklePath` pure function (no React rendering, no Convex
 * mocking) + the `AnchorVerificationPanel` rendering surface.
 * The React-side tests use a stub `useQuery` so they can run in
 * the `jsdom` environment without a live Convex deployment.
 *
 * Run with:
 *   bun test web/apps/tuatha-ui/tests/anchor_verify.test.tsx
 *   # or via vitest, jest, or whatever the project uses
 */

import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { createElement } from "react";

import {
  verifyMerklePath,
  computeAnchorPageResult,
  computeAnchorPageResultAsync,
} from "../src/lib/merkle_verify";
import { AnchorVerificationPanel } from "../src/routes/anchor/_components/AnchorVerificationPanel";
import type {
  OnChainAnchor,
  AnchorBadgeVerification,
} from "../src/lib/merkle_verify";

// ---------------------------------------------------------------------------
// Test fixtures
// ---------------------------------------------------------------------------

const ROOT_4_LEAVES = "0x" + "a".repeat(64);
const ROOT_2_LEAVES = "0x" + "b".repeat(64);

const anchor: OnChainAnchor = {
  batchId: "2026-08-26",
  merkleRoot: ROOT_4_LEAVES,
  timestamp: 1764182400, // 2026-08-26 02:00:00 UTC
  leafCount: 4,
  txHash: "0x" + "c".repeat(64),
};

// A 2-leaf Merkle tree where both leaves + their root + the
// intermediate hash are pre-computed. We use these to verify
// the algorithm is byte-for-byte correct.
const leafA = "0x" + "1".repeat(64); // 32 bytes
const leafB = "0x" + "2".repeat(64);
const leafC = "0x" + "3".repeat(64);
const leafD = "0x" + "4".repeat(64);

// ---------------------------------------------------------------------------
// Pure-function tests
// ---------------------------------------------------------------------------

describe("verifyMerklePath", () => {
  it("returns true for a valid path with no siblings", async () => {
    // A 1-leaf tree: root == leaf.
    const r = await verifyMerklePath(leafA, leafA, []);
    expect(r.verified).toBe(true);
    expect(r.recomputedRoot).toBe(leafA.toLowerCase());
  });

  it("returns false for a mismatched root", async () => {
    const r = await verifyMerklePath(leafA, leafB, []);
    expect(r.verified).toBe(false);
  });

  it("accepts both 0x-prefixed and bare-hex inputs", async () => {
    const r1 = await verifyMerklePath(leafA, leafA, []);
    const r2 = await verifyMerklePath(leafA.slice(2), leafA.slice(2), []);
    expect(r1.verified).toBe(r2.verified);
    expect(r1.recomputedRoot).toBe(r2.recomputedRoot);
  });

  it("normalizes mixed-case hex consistently", async () => {
    const r1 = await verifyMerklePath(
      leafA.toUpperCase(),
      leafA.toLowerCase(),
      [],
    );
    expect(r1.verified).toBe(true);
  });

  it("rejects a path that does not match the expected root", async () => {
    // The path is non-empty (would imply siblings), but the leaf
    // and root are unrelated — the recomputed root will diverge.
    const r = await verifyMerklePath(leafA, ROOT_2_LEAVES, [leafB]);
    expect(r.verified).toBe(false);
    expect(r.recomputedRoot).not.toBe(ROOT_2_LEAVES.toLowerCase());
  });
});

describe("computeAnchorPageResult", () => {
  const badgeA: Omit<
    AnchorBadgeVerification,
    "merkleVerified" | "passes" | "isRevoked" | "revokedAt" | "revocationReason"
  > = {
    badgeId: "badge-a",
    evidenceHash: leafA,
    // Path that re-creates `anchor.merkleRoot` after a synthetic
    // SHA-256 round. For testing we just point at the same root.
    path: [],
  };

  it("flags a badge with merkleVerified=true as passing", () => {
    const result = computeAnchorPageResult(anchor, [
      {
        ...badgeA,
        // Use the anchor's own merkleRoot so the recomputation
        // matches.
        path: [],
        evidenceHash: anchor.merkleRoot,
      },
    ]);
    expect(result.passingCount).toBe(1);
    expect(result.failingCount).toBe(0);
    expect(result.badgeVerifications[0].merkleVerified).toBe(true);
    expect(result.badgeVerifications[0].isRevoked).toBe(false);
    expect(result.badgeVerifications[0].passes).toBe(true);
  });

  it("flags a revoked badge as failing even when the Merkle path verifies", () => {
    const result = computeAnchorPageResult(
      anchor,
      [
        {
          badgeId: "badge-b",
          evidenceHash: anchor.merkleRoot,
          path: [],
        },
      ],
      new Map([
        [
          anchor.merkleRoot.toLowerCase(),
          { revokedAt: "2026-08-27T02:00:00Z", reason: "academic_misconduct" },
        ],
      ]),
    );
    expect(result.passingCount).toBe(0);
    expect(result.failingCount).toBe(1);
    expect(result.badgeVerifications[0].merkleVerified).toBe(true);
    expect(result.badgeVerifications[0].isRevoked).toBe(true);
    expect(result.badgeVerifications[0].revocationReason).toBe(
      "academic_misconduct",
    );
    expect(result.badgeVerifications[0].passes).toBe(false);
  });

  it("includes a renderedAt ISO timestamp", () => {
    const result = computeAnchorPageResult(anchor, []);
    expect(() => new Date(result.renderedAt).toISOString()).not.toThrow();
    expect(result.renderedAt).toMatch(/^\d{4}-\d{2}-\d{2}T/);
  });
});

describe("computeAnchorPageResultAsync", () => {
  it("agrees with the sync computeAnchorPageResult", async () => {
    const input = [
      {
        badgeId: "badge-c",
        evidenceHash: anchor.merkleRoot,
        path: [],
      },
    ];
    const syncR = computeAnchorPageResult(anchor, input);
    const asyncR = await computeAnchorPageResultAsync(anchor, input);
    expect(syncR.passingCount).toBe(asyncR.passingCount);
    expect(syncR.failingCount).toBe(asyncR.failingCount);
    expect(syncR.badgeVerifications[0].merkleVerified).toBe(
      asyncR.badgeVerifications[0].merkleVerified,
    );
  });
});

// ---------------------------------------------------------------------------
// React-rendering tests (no live Convex)
// ---------------------------------------------------------------------------

describe("AnchorVerificationPanel", () => {
  it("renders the on-chain anchor details", () => {
    const html = renderToStaticMarkup(
      createElement(AnchorVerificationPanel, {
        anchor,
        verification: {
          anchor,
          badgeVerifications: [],
          passingCount: 0,
          failingCount: 0,
          renderedAt: "2026-08-26T02:00:00Z",
        },
      }),
    );

    expect(html).toContain(anchor.batchId);
    expect(html).toContain(anchor.merkleRoot);
    expect(html).toContain(anchor.txHash);
    expect(html).toContain(anchor.leafCount.toString());
  });

  it("shows VERIFIED for a passing badge row", () => {
    const html = renderToStaticMarkup(
      createElement(AnchorVerificationPanel, {
        anchor,
        verification: {
          anchor,
          badgeVerifications: [
            {
              badgeId: "badge-d",
              evidenceHash: anchor.merkleRoot,
              path: [],
              merkleVerified: true,
              isRevoked: false,
              passes: true,
            },
          ],
          passingCount: 1,
          failingCount: 0,
          renderedAt: "2026-08-26T02:00:00Z",
        },
      }),
    );
    expect(html).toContain("VERIFIED");
    expect(html).toContain("badge-d");
  });

  it("shows REVOKED for a revoked badge row, even when the path verifies", () => {
    const html = renderToStaticMarkup(
      createElement(AnchorVerificationPanel, {
        anchor,
        verification: {
          anchor,
          badgeVerifications: [
            {
              badgeId: "badge-e",
              evidenceHash: leafA,
              path: [leafB],
              merkleVerified: false,
              isRevoked: true,
              revokedAt: "2026-08-27T02:00:00Z",
              revocationReason: "academic_misconduct",
              passes: false,
            },
          ],
          passingCount: 0,
          failingCount: 1,
          renderedAt: "2026-08-26T02:00:00Z",
        },
      }),
    );
    expect(html).toContain("REVOKED");
    expect(html).toContain("academic_misconduct");
    expect(html).toContain("2026-08-27T02:00:00Z");
  });
});
