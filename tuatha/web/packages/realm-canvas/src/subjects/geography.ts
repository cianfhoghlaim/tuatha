/**
 * geography — the Atlas of the British Isles.
 *
 * Teal + terracotta palette + wind + rain + sea foam.
 * The 2.5D tilt is medium (~0.18 rad) — the parallaxed
 * wind/rain layers evoke the Atlantic weather rolling in.
 */

import type { RealmDescriptor } from "../types.js";

export const geography: RealmDescriptor = {
  slug: "geography",
  title: { en: "Atlas of the British Isles", ga: "Atlas Oileáin na Breataine" },
  tagline: {
    en: "Chart the coastline — read the wind.",
    ga: "Léarscáil an chósta — léigh an ghaoth.",
  },
  palette: {
    deep: 0x052229,
    mid: 0x0c3d49,
    realm: 0x16616f,
    foreground: 0x2e8c9a,
    ink: 0xf4ead7,
    parchment: 0xe9d6b6,
    accent: 0xc77a4e,
  },
  sprites: {
    sprites: [
      "ordnance-survey-map",
      "atlantic-wave",
      "limestone-cliff",
      "compass-rose",
      "rain-glyph",
    ],
    emitters: ["wind", "timeSand"],
    audioCues: ["ambient-wind", "wave-crash", "compass-spin"],
  },
  canvasHeight: 2048,
  tiltRadians: 0.18,
};