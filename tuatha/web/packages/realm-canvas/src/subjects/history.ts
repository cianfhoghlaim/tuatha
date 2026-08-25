/**
 * history — the Long Hall of Chronicles.
 *
 * Burgundy + gold palette + time-sand + torch flames.
 * The 2.5D tilt is shallow (~0.12 rad) — the hall reads
 * like a long reading room with torchlight flickering.
 */

import type { RealmDescriptor } from "../types.js";

export const history: RealmDescriptor = {
  slug: "history",
  title: { en: "Long Hall of Chronicles", ga: "Halla Fada na gCuntas" },
  tagline: {
    en: "Turn the hourglass — read the chronicle.",
    ga: "Cas an clog — léigh an cuntas.",
  },
  palette: {
    deep: 0x2a0810,
    mid: 0x48121d,
    realm: 0x722133,
    foreground: 0x9c3c4d,
    ink: 0xf3e1b8,
    parchment: 0xe8d29b,
    accent: 0xd1a047,
  },
  sprites: {
    sprites: [
      "illuminated-manuscript",
      "iron-crown",
      "torch-flame",
      "hourglass",
      "stone-battlement",
    ],
    emitters: ["timeSand"],
    audioCues: ["ambient-torch", "page-turn", "chronicle-bell"],
  },
  canvasHeight: 2048,
  tiltRadians: 0.12,
};