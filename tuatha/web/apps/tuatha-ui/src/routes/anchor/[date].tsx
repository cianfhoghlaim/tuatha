/**
 * web/apps/tuatha-ui/src/routes/anchor/[date].tsx
 *
 * The public `/anchor/<date>` verification page (Layer 5 P5).
 *
 * Renders the on-chain CredAnchor record for a given YYYY-MM-DD
 * batch + a per-badge verification table. Each row shows the
 * badge's evidence_hash + its Merkle verification result + its
 * revocation status.
 *
 * No login required — this is the public-facing verification
 * surface for employers, universities, parents, etc. Privacy
 * is preserved by never exposing student PII: only the
 * evidence_hash (a SHA-256 of the student's pseudonym + salt)
 * is rendered.
 */

import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "convex/react";
import { api } from "../../convex/_generated/api";
import type { AnchorPageResult } from "../../lib/merkle_verify";
import { AnchorVerificationPanel } from "./_components/AnchorVerificationPanel";

export const Route = createFileRoute("/anchor/$date")({
  component: AnchorPage,
  validateSearch: (search: Record<string, unknown>) => ({
    badgeId: typeof search.badgeId === "string" ? search.badgeId : undefined,
    evidenceHash:
      typeof search.evidenceHash === "string" ? search.evidenceHash : undefined,
  }),
});

function AnchorPage() {
  const { date } = Route.useParams();
  const { badgeId, evidenceHash } = Route.useSearch();

  // Step 1: read the on-chain anchor (cheap Convex query).
  const anchor = useQuery(api.anchor.getAnchorByDate, {
    batchDate: date,
  });

  // Step 2: load the per-badge verification (only when we have a
  // single badge to verify OR when the user clicks "Verify all").
  const verification = useQuery(
    api.anchor.verifyBatch,
    anchor ? { batchDate: date } : "skip",
  ) as AnchorPageResult | undefined | null;

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <header className="mb-8">
        <Link
          to="/"
          className="text-sm text-blue-600 hover:text-blue-800 hover:underline"
        >
          ← Back to home
        </Link>
        <h1 className="mt-4 text-3xl font-bold text-gray-900">
          Daily Credential Anchor
        </h1>
        <p className="mt-2 text-sm text-gray-600">
          Public Merkle-root verification for the Tuatha SkillTreeBadge
          daily batch. The root is published on Base L2 via the{" "}
          <code className="rounded bg-gray-100 px-1 py-0.5 text-xs">
            CredAnchor
          </code>{" "}
          contract; this page reads it via Convex + recomputes the
          Merkle path for any badge in the batch.
        </p>
      </header>

      {!anchor && (
        <section className="rounded-lg border border-yellow-200 bg-yellow-50 p-6">
          <h2 className="text-lg font-semibold text-yellow-900">
            No anchor published for {date}
          </h2>
          <p className="mt-2 text-sm text-yellow-800">
            The daily batch runs at 02:00 UTC. If you are checking
            today's date, the anchor has not been published yet —
            check back after 02:00 UTC. If you are checking a past
            date with no anchor, no badges were issued that day
            (the anchor is only published when there are ≥1 new
            non-revoked badges since the last anchor).
          </p>
        </section>
      )}

      {anchor && (
        <AnchorVerificationPanel
          anchor={anchor}
          verification={verification ?? undefined}
          focusedBadgeId={badgeId}
          focusedEvidenceHash={evidenceHash}
        />
      )}

      <footer className="mt-12 border-t border-gray-200 pt-6 text-xs text-gray-500">
        <p>
          See{" "}
          <code className="rounded bg-gray-100 px-1 py-0.5">
            tuatha/docs/REVOCATION_POLICY.md
          </code>{" "}
          for the 24h revocation propagation guarantee.
        </p>
      </footer>
    </main>
  );
}
