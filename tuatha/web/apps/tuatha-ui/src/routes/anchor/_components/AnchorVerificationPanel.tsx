/**
 * web/apps/tuatha-ui/src/routes/anchor/_components/AnchorVerificationPanel.tsx
 *
 * The body of the `/anchor/<date>` route. Renders the on-chain
 * anchor record + the per-badge verification table. Self-contained:
 * no external state, no navigation — purely a function of the
 * `anchor` + `verification` props.
 */

import type {
  AnchorBadgeVerification,
  AnchorPageResult,
  OnChainAnchor,
} from "../../../lib/merkle_verify";

export interface AnchorVerificationPanelProps {
  readonly anchor: OnChainAnchor;
  readonly verification?: AnchorPageResult;
  readonly focusedBadgeId?: string;
  readonly focusedEvidenceHash?: string;
}

export function AnchorVerificationPanel({
  anchor,
  verification,
  focusedBadgeId,
  focusedEvidenceHash,
}: AnchorVerificationPanelProps) {
  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900">
          On-chain anchor
        </h2>
        <dl className="mt-4 grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2">
          <dt className="text-sm font-medium text-gray-500">Batch ID</dt>
          <dd className="font-mono text-sm text-gray-900">
            {anchor.batchId}
          </dd>

          <dt className="text-sm font-medium text-gray-500">Merkle root</dt>
          <dd className="break-all font-mono text-xs text-gray-900">
            {anchor.merkleRoot}
          </dd>

          <dt className="text-sm font-medium text-gray-500">Leaf count</dt>
          <dd className="font-mono text-sm text-gray-900">
            {anchor.leafCount.toLocaleString()}
          </dd>

          <dt className="text-sm font-medium text-gray-500">Timestamp</dt>
          <dd className="font-mono text-sm text-gray-900">
            {new Date(anchor.timestamp * 1000).toISOString()}
          </dd>

          <dt className="text-sm font-medium text-gray-500">Tx hash</dt>
          <dd className="break-all font-mono text-xs text-gray-900">
            <a
              href={`https://basescan.org/tx/${anchor.txHash}`}
              target="_blank"
              rel="noreferrer noopener"
              className="text-blue-600 hover:text-blue-800 hover:underline"
            >
              {anchor.txHash}
            </a>
          </dd>
        </dl>
      </section>

      {verification && (
        <section className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-baseline justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Per-badge verification
            </h2>
            <p className="text-xs text-gray-500">
              {verification.passingCount} passing ·{" "}
              {verification.failingCount} failing
            </p>
          </div>

          {verification.badgeVerifications.length === 0 ? (
            <p className="mt-4 text-sm text-gray-500">
              No badges in this batch.
            </p>
          ) : (
            <ul className="mt-4 divide-y divide-gray-100">
              {verification.badgeVerifications.map((b) => (
                <BadgeRow
                  key={b.badgeId}
                  verification={b}
                  isFocused={
                    b.badgeId === focusedBadgeId ||
                    b.evidenceHash === focusedEvidenceHash
                  }
                />
              ))}
            </ul>
          )}
        </section>
      )}
    </div>
  );
}

function BadgeRow({
  verification,
  isFocused,
}: {
  verification: AnchorBadgeVerification;
  isFocused: boolean;
}) {
  const { badgeId, evidenceHash, merkleVerified, isRevoked, passes } =
    verification;

  let statusLabel: string;
  let statusClasses: string;
  if (passes) {
    statusLabel = "VERIFIED";
    statusClasses = "bg-green-100 text-green-800";
  } else if (isRevoked) {
    statusLabel = "REVOKED";
    statusClasses = "bg-red-100 text-red-800";
  } else if (!merkleVerified) {
    statusLabel = "FAILED";
    statusClasses = "bg-yellow-100 text-yellow-800";
  } else {
    statusLabel = "UNKNOWN";
    statusClasses = "bg-gray-100 text-gray-800";
  }

  return (
    <li
      className={`flex items-center justify-between gap-4 py-3 ${
        isFocused ? "rounded bg-blue-50 px-3" : ""
      }`}
      data-testid={`badge-row-${badgeId}`}
    >
      <div className="min-w-0 flex-1">
        <p className="break-all font-mono text-xs text-gray-900">
          {evidenceHash}
        </p>
        {verification.revocationReason && (
          <p className="mt-1 text-xs text-red-700">
            Revoked ({verification.revocationReason}) at{" "}
            {verification.revokedAt}
          </p>
        )}
      </div>
      <span
        className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${statusClasses}`}
        data-testid={`badge-status-${badgeId}`}
      >
        {statusLabel}
      </span>
    </li>
  );
}
