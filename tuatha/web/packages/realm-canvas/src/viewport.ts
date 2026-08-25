/**
 * viewport — pixi-viewport integration with 2.5D tilt.
 *
 * The orthographic camera applies a small tilt
 * (`descriptor.tiltRadians`, ~0.15 rad) by scaling the Y axis
 * post-projection. The 5-layer parallax (sky / midground /
 * gameplay / foreground / HUD) is exposed via `viewport.world`
 * so the particle system + sprite banks can drop sprites into
 * the correct layer.
 */

import { Application, Container } from "pixi.js";
import { Viewport } from "pixi-viewport";
import type { RealmDescriptor } from "./types.js";

export interface TiltedViewport {
  readonly viewport: Viewport;
  readonly world: Container;
  readonly layers: {
    readonly sky: Container;
    readonly midground: Container;
    readonly gameplay: Container;
    readonly foreground: Container;
    readonly hud: Container;
  };
  destroy(options?: { children?: boolean }): void;
}

/**
 * The 5 canonical parallax layers, in draw order. Sprites added
 * to a higher-index layer render on top of lower-index layers.
 */
function createParallaxLayers(world: Container): TiltedViewport["layers"] {
  const sky = new Container({ label: "parallax.sky", isRenderGroup: true });
  const midground = new Container({ label: "parallax.midground", isRenderGroup: true });
  const gameplay = new Container({ label: "parallax.gameplay", isRenderGroup: true });
  const foreground = new Container({ label: "parallax.foreground", isRenderGroup: true });
  const hud = new Container({ label: "parallax.hud", isRenderGroup: true });
  world.addChild(sky, midground, gameplay, foreground, hud);
  return { sky, midground, gameplay, foreground, hud };
}

/**
 * Apply the 2.5D tilt by scaling the world container along the
 * Y axis. The scaling factor comes from
 * `Math.cos(descriptor.tiltRadians)` — a 0.15 rad tilt gives a
 * ~1.01 scale (subtle).
 */
function applyTilt(world: Container, tiltRadians: number): void {
  const yScale = 1 / Math.max(Math.cos(tiltRadians), 0.0001);
  world.scale.y = yScale;
  world.pivot.y = 0;
}

export function createRealmViewport(
  app: Application,
  descriptor: RealmDescriptor,
): TiltedViewport {
  const world = new Container({ label: "realm.world", isRenderGroup: true });
  const layers = createParallaxLayers(world);

  const viewport = new Viewport({
    screenWidth: app.renderer.width,
    screenHeight: app.renderer.height,
    worldWidth: 4096,
    worldHeight: descriptor.canvasHeight,
    events: app.renderer.events,
  });

  viewport
    .drag({ mouseButtons: "left" })
    .pinch()
    .wheel({ smooth: 5 })
    .decelerate({ friction: 0.92 })
    .clampZoom({ minScale: 0.5, maxScale: 2.0 })
    .clamp({ direction: "all" });

  app.stage.addChild(world);
  app.stage.addChild(viewport);
  world.addChild(viewport);
  viewport.addChild(world);

  applyTilt(world, descriptor.tiltRadians);

  return {
    viewport,
    world,
    layers,
    destroy(options) {
      viewport.destroy(options);
      world.destroy(options);
    },
  };
}