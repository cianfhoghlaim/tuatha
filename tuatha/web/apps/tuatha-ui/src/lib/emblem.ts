/**
 * lib/emblem — the emblem cache client helper.
 *
 * Wraps the Convex `emblems` table behind a small, pure
 * function that the mastery dashboard route can call. The
 * helper does NOT bake in a Convex client — the consuming
 * component passes its `useMutation` / `useQuery` bindings in.
 *
 * The cache key is `(topSubject, studentId, seed)` per the
 * spec.
 */

import type { MasteryAxisKey } from "@tuatha/mastery-chart";

export interface EmblemKey {
  readonly studentId: string;
  readonly topSubject: MasteryAxisKey;
  readonly seed: number;
}

export interface EmblemCacheEntry {
  readonly studentId: string;
  readonly topSubject: MasteryAxisKey;
  readonly seed: number;
  readonly imageUrl: string;
  readonly modelId: string;
  readonly modelVersion: string;
}

/**
 * Build the canonical cache key from the dashboard state. Pure
 * function — safe to use in render code.
 */
export function buildEmblemKey(studentId: string, topSubject: MasteryAxisKey, seed: number): EmblemKey {
  return { studentId, topSubject, seed };
}

/**
 * Compute a stable seed from the student id + the chart's top
 * subject. The hash makes the seed reproducible across renders
 * and across SSR/hydration boundaries.
 */
export function defaultEmblemSeed(studentId: string): number {
  let hash = 0;
  for (let i = 0; i < studentId.length; i += 1) {
    hash = (hash * 33 + studentId.charCodeAt(i)) | 0;
  }
  return Math.abs(hash) || 1;
}

/**
 * Format the URL the `<img>` tag will load. Phase 1 will replace
 * the stub URL with the real FIBO CDN URL; for now this is the
 * deterministic placeholder that the Convex function returns.
 */
export function emblemSrc(entry: EmblemCacheEntry): string {
  return entry.imageUrl;
}

/**
 * Minimal contract test: a key is "fresh" when no cache row has
 * yet been written for `(studentId, topSubject, seed)`. The
 * Convex function `ensureEmblem` decides freshness server-side;
 * this helper mirrors that decision client-side for UI hints.
 */
export function isEmblemCacheFresh(entry: EmblemCacheEntry | null, key: EmblemKey): boolean {
  if (entry === null) return false;
  return (
    entry.studentId === key.studentId &&
    entry.topSubject === key.topSubject &&
    entry.seed === key.seed &&
    entry.imageUrl !== "" &&
    entry.modelId !== ""
  );
}