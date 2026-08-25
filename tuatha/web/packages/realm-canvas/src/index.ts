/**
 * realm-canvas index — the public `TuathaRealmCanvas` class.
 *
 * The 2.5D Hades-orthographic renderer. PixiJS v8 auto-detects
 * WebGPU, falling back to WebGL2. Layered parallax (sky /
 * midground / gameplay / foreground / HUD) gives the 2.5D feel
 * without any 3D world. The orthographic camera comes from
 * pixi-viewport with a configurable tilt.
 *
 * NO Babylon.js. NO SpacetimeDB. NO 3D. NO Three.js.
 */

import { Application, Container, Graphics } from "pixi.js";
import type { SubjectSlug, RealmDescriptor } from "./types.js";
import { createRealmViewport, type TiltedViewport } from "./viewport.js";
import { createRealmParticleSystem, type RealmParticleSystem } from "./particles.js";
import { createRealmAudio, type RealmAudioController } from "./audio.js";
import { loadRealmDescriptor } from "./subjects/index.js";

export type { SubjectSlug, RealmDescriptor, RealmPalette, RealmSpriteBank, RealmBilingualLabel } from "./types.js";
export { ALL_SUBJECT_SLUGS } from "./types.js";
export { loadRealmDescriptor, iterRealmDescriptors } from "./subjects/index.js";
export { EMITTER_FAMILIES, type EmitterFamily, type EmitterConfig } from "./particles.js";

export interface TuathaRealmCanvasOptions {
  /** The NCCA subject realm to render. */
  readonly subject: SubjectSlug;
  /** Container width in CSS pixels (the parent dictates layout). */
  readonly width: number;
  /** Container height in CSS pixels. */
  readonly height: number;
  /**
   * Background canvas colour — defaults to the realm's
   * `palette.deep` (the "far" parallax colour). Pass `0x000000`
   * to suppress the auto-clear.
   */
  readonly backgroundColor?: number;
  /** Disable WebGPU detection (force WebGL). Useful in tests. */
  readonly forceWebGL?: boolean;
  /** Disable audio boot (the renderer is silent until audio is unlocked). */
  readonly audioEnabled?: boolean;
}

export interface TuathaRealmCanvasHandle {
  readonly app: Application;
  readonly viewport: TiltedViewport;
  readonly particles: RealmParticleSystem;
  readonly audio: RealmAudioController;
  readonly descriptor: RealmDescriptor;
  /** Tear down the canvas + stop the ticker. Safe to call repeatedly. */
  destroy(): Promise<void>;
}

/**
 * Boot the 2.5D PixiJS v8 realm canvas against an existing
 * `<div>` host. The host MUST be in the DOM (and sized) before
 * calling this — the renderer binds to its `width` × `height`.
 */
export async function mountTuathaRealmCanvas(
  host: HTMLElement,
  options: TuathaRealmCanvasOptions,
): Promise<TuathaRealmCanvasHandle> {
  const descriptor = loadRealmDescriptor(options.subject);

  const app = new Application();
  await app.init({
    width: options.width,
    height: options.height,
    background: options.backgroundColor ?? descriptor.palette.deep,
    preference: options.forceWebGL ? "webgl" : "webgpu",
    antialias: true,
    resolution: globalThis.devicePixelRatio ?? 1,
    autoDensity: true,
    hello: false,
  });

  host.replaceChildren(app.canvas);
  app.canvas.style.display = "block";
  app.canvas.style.width = "100%";
  app.canvas.style.height = "100%";

  const viewport = createRealmViewport(app, descriptor);
  const particles = createRealmParticleSystem(app, viewport.world, descriptor);
  const audio = createRealmAudio(descriptor, { enabled: options.audioEnabled ?? true });

  return {
    app,
    viewport,
    particles,
    audio,
    descriptor,
    async destroy() {
      particles.destroy();
      viewport.destroy({ children: true });
      audio.destroy();
      app.destroy(true, { children: true });
    },
  };
}

/**
 * Convenience class — wraps `mountTuathaRealmCanvas` with a
 * host element + an options bag. The per-subject routes use
 * this directly.
 */
export class TuathaRealmCanvas {
  private readonly host: HTMLElement;
  private readonly options: TuathaRealmCanvasOptions;
  private handle: TuathaRealmCanvasHandle | null = null;

  constructor(host: HTMLElement, options: TuathaRealmCanvasOptions) {
    this.host = host;
    this.options = options;
  }

  async mount(): Promise<TuathaRealmCanvasHandle> {
    if (this.handle !== null) return this.handle;
    this.handle = await mountTuathaRealmCanvas(this.host, this.options);
    return this.handle;
  }

  get isMounted(): boolean {
    return this.handle !== null;
  }

  get descriptor(): RealmDescriptor | null {
    return this.handle?.descriptor ?? null;
  }

  async destroy(): Promise<void> {
    if (this.handle === null) return;
    await this.handle.destroy();
    this.handle = null;
  }
}

/**
 * Internal helper — draw a placeholder background into the
 * deepest parallax layer (used by the per-subject realm when no
 * background sprite asset is available yet).
 */
export function drawRealmPlaceholder(layer: Container, descriptor: RealmDescriptor): void {
  const backdrop = new Graphics()
    .rect(0, 0, 4096, descriptor.canvasHeight)
    .fill({ color: descriptor.palette.realm });
  layer.addChild(backdrop);
}