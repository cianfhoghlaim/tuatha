/**
 * web/apps/tuatha-ui/src/routes/credential/[badge_id].tsx
 *
 * The public `/credential/<badge_id>` verification page (Layer 5
 * P5 / D.1 of the 2026-08-27 KCG rename).
 *
 * Renders the SkillTreeBadge record for a given `<badge_id>` —
 * the canonical credential verification surface for employers,
 * universities, parents, etc. Privacy is preserved by never
 * exposing student PII; only the public fields (subject,
 * competency, evidence_hash, on_chain_anchor) are rendered.
 *
 * The kcg- → cianfhoghlaim- prefix rotation:
 *
 * Per the `2026-08-27-tuatha-let-ta-id-rotation-v1` change (T11.1 /
 * T11.2), the public credential verifier MUST accept BOTH the
 * legacy `kcg-mathematics-...` prefix and the canonical
 * `cianfhoghlaim-mathematics-...` prefix during the 90-day
 * transition window. After 2026-11-25, only the canonical prefix
 * is accepted; the `prefixRewriteBadgeId` helper is removed.
 *
 * The rewrite is intentionally LBYL + idempotent: a URL carrying
 * the legacy prefix resolves to the SAME Convex row as the URL
 * carrying the canonical prefix, because the underlying
 * `evidence_hash` (the Merkle leaf) is hash-stable across the
 * rename.
 */

import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "convex/react";
import { api } from "../../convex/_generated/api";

// ── Prefix rewrite ───────────────────────────────────────────────────

/**
 * The legacy badge_id prefix (pre-2026-08-27 rotation). Minted
 * against `tuatha/tools/mathematics_response_score.py` before the
 * KCG rename commit 5209691f.
 */
const LEGACY_PREFIX = "kcg-";

/**
 * The canonical badge_id prefix (post-2026-08-27 rotation). This
 * is the prefix the post-rename `mathematics_response_score.py`
 * f-string emits.
 */
const CANONICAL_PREFIX = "cianfhoghlaim-";

/**
 * The 90-day transition window deadline. After this date the
 * legacy-prefix branch is removed (T11.2). Pinned to the openspec
 * change's G6 gate (2026-08-27 + 90 days = 2026-11-25).
 */
const TRANSITION_DEADLINE_ISO = "2026-11-25";

/**
 * Rewrite a legacy `kcg-` badge_id to its canonical
 * `cianfhoghlaim-` form. Idempotent for canonical inputs (returns
 * the input unchanged). Returns the input unchanged for any
 * prefix other than `kcg-` so future renames follow the same
 * single-rewrite pattern.
 *
 * @param badgeId The raw badge_id from the URL.
 * @returns The canonical badge_id suitable for the Convex
 *   `badges:get` lookup.
 */
export function prefixRewriteBadgeId(badgeId: string): string {
  if (badgeId.startsWith(LEGACY_PREFIX)) {
    return `${CANONICAL_PREFIX}${badgeId.slice(LEGACY_PREFIX.length)}`;
  }
  return badgeId;
}

/**
 * True iff the input badge_id carries the legacy `kcg-` prefix.
 * Used by the route to render the "this URL carries a legacy
 * prefix" banner during the transition window.
 */
export function isLegacyBadgeId(badgeId: string): boolean {
  return badgeId.startsWith(LEGACY_PREFIX);
}

/**
 * True iff the current date is on-or-before the 2026-11-25
 * transition deadline. Pure LBYL helper — no timezone surprises,
 * just a `Date.now()` comparison.
 */
export function isTransitionWindowOpen(now: Date = new Date()): boolean {
  return now.getTime() <= new Date(TRANSITION_DEADLINE_ISO).getTime();
}

// ── Route definition ─────────────────────────────────────────────────

export const Route = createFileRoute("/credential/$badge_id")({
  component: CredentialPage,
});

// ── Page ──────────────────────────────────────────────────────────────

interface BadgeRecord {
  readonly _id: string;
  readonly studentId: string;
  readonly subject: string;
  readonly competencyCode: string;
  readonly dateEarned: number;
  readonly evidenceHash: string;
  readonly onChainAnchor?: string | null;
  readonly anchorDate?: string | null;
  readonly isRevoked?: boolean;
  readonly revocationReason?: string | null;
}

function CredentialPage() {
  const { badge_id } = Route.useParams();

  // 1. Resolve the canonical badge_id (handles kcg- → cianfhoghlaim-).
  const canonicalBadgeId = prefixRewriteBadgeId(badge_id);
  const wasRewritten = canonicalBadgeId !== badge_id;

  // 2. Fetch the badge row (public fields only).
  const badge = useQuery(
    api.badge_query.getBadgeById as never,
    { badgeId: canonicalBadgeId } as never,
  ) as BadgeRecord | null | undefined;

  const isLoading = badge === undefined;
  const isMissing = badge === null;

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
          Credential Verification
        </h1>
        <p className="mt-2 text-sm text-gray-600">
          Public SkillTreeBadge verification for the Tuatha Educational
          MMO. The badge contents are hashed (SHA-256 evidence_hash);
          the Merkle root is published on Base L2 via the{" "}
          <code className="rounded bg-gray-100 px-1 py-0.5 text-xs">
            CredAnchor
          </code>{" "}
          contract. This page reads the badge row via Convex + links
          to the on-chain anchor for cryptographic verification.
        </p>
      </header>

      {wasRewritten && isTransitionWindowOpen() && (
        <section
          className="mb-6 rounded-lg border border-blue-200 bg-blue-50 p-4"
          data-testid="legacy-prefix-banner"
        >
          <h2 className="text-sm font-semibold text-blue-900">
            Legacy badge ID prefix
          </h2>
          <p className="mt-1 text-xs text-blue-800">
            The URL carried the legacy <code>kcg-</code> prefix
            minted before the 2026-08-27 KCG rename. Resolved to the
            canonical <code>cianfhoghlaim-</code> form for lookup.
            The legacy prefix rewrite is scheduled for removal on{" "}
            {TRANSITION_DEADLINE_ISO}; bookmark the canonical URL to
            future-proof your references.
          </p>
        </section>
      )}

      {isLoading && (
        <section className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <p className="text-sm text-gray-500">Loading credential…</p>
        </section>
      )}

      {isMissing && (
        <section
          className="rounded-lg border border-red-200 bg-red-50 p-6"
          data-testid="badge-not-found"
        >
          <h2 className="text-lg font-semibold text-red-900">
            No credential found
          </h2>
          <p className="mt-2 text-sm text-red-800">
            No SkillTreeBadge row exists for{" "}
            <code className="break-all font-mono text-xs">
              {canonicalBadgeId}
            </code>
            . If this URL was copied from a pre-2026-08-27 reference,
            confirm that the legacy <code>kcg-</code> prefix has
            been resolved to the canonical <code>cianfhoghlaim-</code>{" "}
            form above. Otherwise, the badge may have been revoked —
            check the revocation list at{" "}
            <code>tuatha/docs/REVOCATION_POLICY.md</code>.
          </p>
        </section>
      )}

      {badge && (
        <section
          className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
          data-testid="badge-details"
          data-badge-id={badge._id}
        >
          <dl className="grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2">
            <dt className="text-sm font-medium text-gray-500">
              Badge ID
            </dt>
            <dd className="break-all font-mono text-sm text-gray-900">
              {badge._id}
            </dd>

            <dt className="text-sm font-medium text-gray-500">Subject</dt>
            <dd className="font-mono text-sm text-gray-900">
              {badge.subject}
            </dd>

            <dt className="text-sm font-medium text-gray-500">
              Competency (NCCA LO)
            </dt>
            <dd className="font-mono text-sm text-gray-900">
              {badge.competencyCode}
            </dd>

            <dt className="text-sm font-medium text-gray-500">
              Date earned
            </dt>
            <dd className="font-mono text-sm text-gray-900">
              {new Date(badge.dateEarned).toISOString()}
            </dd>

            <dt className="text-sm font-medium text-gray-500">
              Evidence hash (Merkle leaf)
            </dt>
            <dd className="break-all font-mono text-xs text-gray-900">
              {badge.evidenceHash}
            </dd>

            <dt className="text-sm font-medium text-gray-500">
              On-chain anchor (Base L2)
            </dt>
            <dd className="break-all font-mono text-xs text-gray-900">
              {badge.onChainAnchor ? (
                <a
                  href={`https://basescan.org/tx/${badge.onChainAnchor}`}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="text-blue-600 hover:text-blue-800 hover:underline"
                >
                  {badge.onChainAnchor}
                </a>
              ) : (
                <span className="text-gray-400">
                  (not yet anchored — daily batch runs at 02:00 UTC)
                </span>
              )}
            </dd>

            <dt className="text-sm font-medium text-gray-500">
              Anchor date
            </dt>
            <dd className="font-mono text-sm text-gray-900">
              {badge.anchorDate ?? "—"}
            </dd>

            <dt className="text-sm font-medium text-gray-500">Status</dt>
            <dd>
              {badge.isRevoked ? (
                <span className="inline-flex items-center rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-800">
                  REVOKED
                  {badge.revocationReason ? (
                    <span className="ml-2 font-normal text-red-700">
                      ({badge.revocationReason})
                    </span>
                  ) : null}
                </span>
              ) : (
                <span className="inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-800">
                  ACTIVE
                </span>
              )}
            </dd>
          </dl>

          {badge.anchorDate && (
            <p className="mt-6 text-xs text-gray-500">
              Verify cryptographic inclusion in the daily batch at{" "}
              <Link
                to="/anchor/$date"
                params={{ date: badge.anchorDate }}
                className="text-blue-600 hover:text-blue-800 hover:underline"
              >
                /anchor/{badge.anchorDate}
              </Link>
              .
            </p>
          )}
        </section>
      )}

      <footer className="mt-12 border-t border-gray-200 pt-6 text-xs text-gray-500">
        <p>
          See{" "}
          <code className="rounded bg-gray-100 px-1 py-0.5">
            tuatha/docs/REVOCATION_POLICY.md
          </code>{" "}
          for the 24h revocation propagation guarantee + the
          operator-side archive timeline for legacy badge IDs (see
          openspec/changes/2026-08-27-tuatha-let-ta-id-rotation-v1/).
        </p>
      </footer>
    </main>
  );
}
