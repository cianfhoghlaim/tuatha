/**
 * english — the Garden of Living Tongues.
 *
 * Forest green + cream palette + quill-pen trails + book-pages.
 * The 2.5D tilt is shallow (~0.12 rad) — the garden reads
 * like a quiet reading nook with quill trails drifting.
 */

import type { RealmDescriptor } from "../types.js";

export const english: RealmDescriptor = {
  slug: "english",
  title: { en: "Garden of Living Tongues", ga: "Gairdín na dTeangacha Beo" },
  tagline: {
    en: "Sip the metaphor — feel the stanza.",
    ga: "Ól an mheafar — mothaigh an rann.",
  },
  palette: {
    deep: 0x0e1f12,
    mid: 0x1a3920,
    realm: 0x2c5a35,
    foreground: 0x498a55,
    ink: 0xfaf3df,
    parchment: 0xf2e6c6,
    accent: 0xc28a3a,
  },
  sprites: {
    sprites: [
      "leather-bound-book",
      "quill-pen",
      "inkwell",
      "stanza-stone",
      "metaphor-rose",
    ],
    emitters: ["closcríobh"],
    audioCues: ["ambient-quill", "page-turn", "metaphor-spoken"],
  },
  canvasHeight: 2048,
  tiltRadians: 0.12,
};