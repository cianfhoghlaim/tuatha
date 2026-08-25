/**
 * subjects — the 8 per-subject realm palettes + sprite banks.
 *
 * Per the spec:
 * - mathematics — Library of Infinite Proofs (deep blue + parchment)
 * - applied_mathematics — Workshop of Applied Forces (amber + iron)
 * - chemistry — Periodic Alchemist's Hall (green + copper)
 * - geography — Atlas of the British Isles (teal + terracotta)
 * - history — Long Hall of Chronicles (burgundy + gold)
 * - english — Garden of Living Tongues (forest green + cream)
 * - gaeilge — The Celtic Crossroads (Connemara purple + bog-oak black)
 * - computer_science — The Silicon Atelier (cyan + charcoal)
 */

import type { RealmDescriptor, RealmDescriptorMap, SubjectSlug } from "../types.js";
import { ALL_SUBJECT_SLUGS } from "../types.js";

export { ALL_SUBJECT_SLUGS } from "../types.js";
export type { SubjectSlug } from "../types.js";

import { mathematics } from "./mathematics.js";
import { applied_mathematics } from "./applied_mathematics.js";
import { chemistry } from "./chemistry.js";
import { geography } from "./geography.js";
import { history } from "./history.js";
import { english } from "./english.js";
import { gaeilge } from "./gaeilge.js";
import { computer_science } from "./computer_science.js";

const REALM_DESCRIPTORS: RealmDescriptorMap = {
  mathematics,
  applied_mathematics,
  chemistry,
  geography,
  history,
  english,
  gaeilge,
  computer_science,
};

/**
 * Look up the realm descriptor for a subject slug. Throws if
 * the slug is unknown (which should never happen if the slug
 * was type-checked against `SubjectSlug`).
 */
export function loadRealmDescriptor(slug: SubjectSlug): RealmDescriptor {
  const descriptor = REALM_DESCRIPTORS[slug];
  if (!descriptor) {
    throw new Error(`Unknown realm slug: ${slug}`);
  }
  return descriptor;
}

/**
 * Iterate every realm descriptor (used by the per-subject route
 * registry + the cross-subject mastery dashboard).
 */
export function iterRealmDescriptors(): Iterable<RealmDescriptor> {
  return ALL_SUBJECT_SLUGS.map((slug) => REALM_DESCRIPTORS[slug]).values();
}