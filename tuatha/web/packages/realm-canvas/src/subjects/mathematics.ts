/**
 * mathematics — the Library of Infinite Proofs.
 *
 * Deep blue + parchment palette + Fibonacci spiral particles.
 * The 2.5D tilt is subtle (~0.15 rad) — the "infinite" feel
 * comes from the parallaxed parchment scrolls.
 */

import type { RealmDescriptor } from "../types.js";

export const mathematics: RealmDescriptor = {
  slug: "mathematics",
  title: { en: "Library of Infinite Proofs", ga: "Leabharlann na gCruthúnas Éagcríochnach" },
  tagline: {
    en: "Walk the Fibonacci spiral — every axiom a parchment.",
    ga: "Siúl an spíral Fibionaice — gach axiom sclábhaí.",
  },
  palette: {
    deep: 0x0b1733,
    mid: 0x162c5c,
    realm: 0x22427f,
    foreground: 0x3d5a99,
    ink: 0xf3e9c8,
    parchment: 0xf6efd9,
    accent: 0xd9b15a,
  },
  sprites: {
    sprites: [
      "parchment-scroll",
      "quill-pen",
      "axiom-stone",
      "compass-rose",
      "fibonacci-golden-rectangle",
    ],
    emitters: ["fibonacciSpiral"],
    audioCues: ["ambient-quill", "proof-resolved", "axiom-revealed"],
  },
  canvasHeight: 2048,
  tiltRadians: 0.15,
};