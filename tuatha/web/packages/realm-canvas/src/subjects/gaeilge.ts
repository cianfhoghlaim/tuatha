/**
 * gaeilge — the Celtic Crossroads.
 *
 * Connemara purple + bog-oak black palette + clóscríobh +
 * bodhrán rhythm. The 2.5D tilt is medium (~0.18 rad) — the
 * crossroads feel comes from the clóscríobh (handwritten
 * Irish) trails drifting on the bog-oak dark backdrop.
 */

import type { RealmDescriptor } from "../types.js";

export const gaeilge: RealmDescriptor = {
  slug: "gaeilge",
  title: { en: "The Celtic Crossroads", ga: "Crosbhealach Cheilteach" },
  tagline: {
    en: "Speak the crossroads — walk the clóscríobh.",
    ga: "Labhair an crosbhealach — siúl an clóscríobh.",
  },
  palette: {
    deep: 0x0d0a18,
    mid: 0x1d1432,
    realm: 0x382555,
    foreground: 0x5a3d7e,
    ink: 0xf2e7d0,
    parchment: 0xe2cea3,
    accent: 0xa96cd6,
  },
  sprites: {
    sprites: [
      "bog-oak-stave",
      "bodhrán-drum",
      "triskele-brooch",
      "clóscríobh-vellum",
      "connemara-horse",
    ],
    emitters: ["closcríobh"],
    audioCues: ["ambient-bodhran", "scriobh-laetha", "crois-bhealach-bell"],
  },
  canvasHeight: 2048,
  tiltRadians: 0.18,
};