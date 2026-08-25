/**
 * chemistry — the Periodic Alchemist's Hall.
 *
 * Green + copper palette + bubbling flasks + reaction sparks.
 * The 2.5D tilt is minimal (~0.10 rad) — the focus is on
 * foreground bubbling flasks and reaction sparks.
 */

import type { RealmDescriptor } from "../types.js";

export const chemistry: RealmDescriptor = {
  slug: "chemistry",
  title: { en: "Periodic Alchemist's Hall", ga: "Halla an Alcamóra Pheiriadaigh" },
  tagline: {
    en: "Mix the element — taste the spark.",
    ga: "Cumaisc an dúil — blais an spréach.",
  },
  palette: {
    deep: 0x082013,
    mid: 0x103a25,
    realm: 0x1d5d3a,
    foreground: 0x2e8c5c,
    ink: 0xf2e7d0,
    parchment: 0xe9d8b8,
    accent: 0xc06f3b,
  },
  sprites: {
    sprites: [
      "round-bottom-flask",
      "periodic-table-tablet",
      "copper-coil",
      "bunsen-burner",
      "reaction-vial",
    ],
    emitters: ["bubblingFlasks", "reactionSparks"],
    audioCues: ["ambient-bubble", "reaction-bang", "element-named"],
  },
  canvasHeight: 2048,
  tiltRadians: 0.1,
};