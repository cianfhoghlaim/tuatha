/**
 * computer_science — the Silicon Atelier.
 *
 * Cyan + charcoal palette + circuit traces + data-flow particles.
 * The 2.5D tilt is shallow (~0.10 rad) — the clean grid of the
 * Silicon Atelier reads as a tidy workshop, with circuit traces
 * pulsing across the foreground.
 */

import type { RealmDescriptor } from "../types.js";

export const computer_science: RealmDescriptor = {
  slug: "computer_science",
  title: { en: "The Silicon Atelier", ga: "Ceardlann an Sileacain" },
  tagline: {
    en: "Trace the circuit — feel the data flow.",
    ga: "Lorg an ciorcad — mothaigh an tsrutha sonraí.",
  },
  palette: {
    deep: 0x0a1218,
    mid: 0x14202a,
    realm: 0x1f3340,
    foreground: 0x34586b,
    ink: 0xddf3ff,
    parchment: 0xc4dbe9,
    accent: 0x36d6c0,
  },
  sprites: {
    sprites: [
      "breadboard-grid",
      "silicon-wafer",
      "fpga-tablet",
      "data-flow-arrow",
      "logic-gate-stone",
    ],
    emitters: ["circuitTraces"],
    audioCues: ["ambient-pulse", "logic-gate-click", "compile-success"],
  },
  canvasHeight: 2048,
  tiltRadians: 0.1,
};