/**
 * applied_mathematics — the Workshop of Applied Forces.
 *
 * Amber + iron palette + mechanical gears + projectile arcs.
 * The 2.5D tilt is steeper than mathematics (~0.20 rad) —
 * the "applied" feel comes from kinetic projectile arcs.
 */

import type { RealmDescriptor } from "../types.js";

export const applied_mathematics: RealmDescriptor = {
  slug: "applied_mathematics",
  title: { en: "Workshop of Applied Forces", ga: "Ceardlann na bhFórsaí Feidhmeach" },
  tagline: {
    en: "Hammer the gear — measure the arc.",
    ga: "Buail an ghaist — tomhais an stua.",
  },
  palette: {
    deep: 0x2b1306,
    mid: 0x4d2407,
    realm: 0x7a3d10,
    foreground: 0xa6581b,
    ink: 0xf7e0b6,
    parchment: 0xeed3a1,
    accent: 0xc98a3c,
  },
  sprites: {
    sprites: [
      "iron-gear",
      "brass-pendulum",
      "projectile-arc",
      "leather-apron",
      "anvil-stone",
    ],
    emitters: ["gearMech"],
    audioCues: ["ambient-forge", "gear-clank", "hammer-fall"],
  },
  canvasHeight: 2048,
  tiltRadians: 0.2,
};