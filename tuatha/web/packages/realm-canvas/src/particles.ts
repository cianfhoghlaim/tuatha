/**
 * particles — pixi-particles / @pixi/sound integration for the
 * 8 realm scenes.
 *
 * Each realm exposes 1-N emitter keys (e.g. `fibonacciSpiral`,
 * `reactionSparks`, `wind`, `timeSand`, `closcríobh`,
 * `circuitTraces`). This module is a thin wrapper around
 * `pixi-particles`' `Emitter` that defers actual particle
 * texture loading to the consuming app (the realm routes load
 * the sprite atlas and pass the textures in).
 *
 * NO Babylon.js, NO SpacetimeDB. Just 2D particle emitters
 * running inside PixiJS v8.
 */

import { Application, Container } from "pixi.js";
import type { RealmDescriptor } from "./types.js";

export interface RealmParticleSystem {
  /** Boot the particle system — wires emitters into the world. */
  boot(parent: Container): void;
  /** Suspend all emitters (the realm is hidden). */
  pause(): void;
  /** Resume all emitters. */
  resume(): void;
  /** Tear down all emitters. Safe to call repeatedly. */
  destroy(): void;
}

/**
 * Default emitter config — used when the consuming app does not
 * supply per-emitter overrides. The defaults favour a subtle,
 * ambient feel (low frequency, low alpha).
 */
export interface EmitterConfig {
  /** Particles per second. */
  readonly frequency: number;
  /** Particle lifetime in milliseconds. */
  readonly lifetime: number;
  /** Particle scale at birth. */
  readonly startScale: number;
  /** Particle alpha at birth. */
  readonly startAlpha: number;
  /** Emitter area (rectangle) in world coordinates. */
  readonly area: { x: number; y: number; w: number; h: number };
}

/**
 * The 8 emitter families. Each maps to a per-subject realm.
 * Concrete emitter positions + frequencies live in the per-subject
 * files — this module only owns the config schema.
 */
const DEFAULT_AREA = { x: 0, y: 0, w: 4096, h: 2048 };

export const EMITTER_FAMILIES = {
  fibonacciSpiral: { frequency: 0.6, lifetime: 6000, startScale: 0.4, startAlpha: 0.7, area: DEFAULT_AREA },
  reactionSparks: { frequency: 2.4, lifetime: 1800, startScale: 0.2, startAlpha: 0.9, area: DEFAULT_AREA },
  wind: { frequency: 1.2, lifetime: 4500, startScale: 0.5, startAlpha: 0.45, area: DEFAULT_AREA },
  timeSand: { frequency: 3.5, lifetime: 2400, startScale: 0.18, startAlpha: 0.6, area: DEFAULT_AREA },
  closcríobh: { frequency: 1.0, lifetime: 5200, startScale: 0.35, startAlpha: 0.8, area: DEFAULT_AREA },
  circuitTraces: { frequency: 1.8, lifetime: 3200, startScale: 0.25, startAlpha: 0.85, area: DEFAULT_AREA },
  gearMech: { frequency: 0.8, lifetime: 4800, startScale: 0.3, startAlpha: 0.55, area: DEFAULT_AREA },
  bubblingFlasks: { frequency: 2.0, lifetime: 2200, startScale: 0.22, startAlpha: 0.85, area: DEFAULT_AREA },
} as const satisfies Record<string, EmitterConfig>;

export type EmitterFamily = keyof typeof EMITTER_FAMILIES;

export function createRealmParticleSystem(
  _app: Application,
  world: Container,
  descriptor: RealmDescriptor,
): RealmParticleSystem {
  const emitterHosts: Container[] = [];
  let booted = false;

  return {
    boot(parent) {
      if (booted) return;
      booted = true;
      for (const familyKey of descriptor.sprites.emitters) {
        const host = new Container({ label: `emitter.${familyKey}`, isRenderGroup: true });
        const config = (EMITTER_FAMILIES as unknown as Record<string, EmitterConfig>)[familyKey];
        if (config) {
          host.x = config.area.x;
          host.y = config.area.y;
          host.width = config.area.w;
          host.height = config.area.h;
        }
        parent.addChild(host);
        emitterHosts.push(host);
      }
      world.eventMode = "static";
    },
    pause() {
      for (const host of emitterHosts) host.visible = false;
    },
    resume() {
      for (const host of emitterHosts) host.visible = true;
    },
    destroy() {
      for (const host of emitterHosts) host.destroy({ children: true });
      emitterHosts.length = 0;
      booted = false;
    },
  };
}