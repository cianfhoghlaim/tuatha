/**
 * realm-canvas — shared types for the Tuatha PixiJS v8 2.5D renderer.
 *
 * The 8 NCCA subject realms each get a `RealmPalette` (deep colours
 * + accent + parchment) and a `RealmSpriteBank` (the procedural
 * sprite keys the per-subject renderer consumes). This is the ONLY
 * place subject-specific constants are declared.
 */

export type SubjectSlug =
  | "mathematics"
  | "applied_mathematics"
  | "chemistry"
  | "geography"
  | "history"
  | "english"
  | "gaeilge"
  | "computer_science";

export const ALL_SUBJECT_SLUGS: readonly SubjectSlug[] = [
  "mathematics",
  "applied_mathematics",
  "chemistry",
  "geography",
  "history",
  "english",
  "gaeilge",
  "computer_science",
] as const;

export interface RealmPalette {
  /** Deep background colour (the "far" parallax layer). */
  readonly deep: number;
  /** Midground colour (the second parallax layer). */
  readonly mid: number;
  /** Gameplay layer colour (the third parallax layer — the realm floor). */
  readonly realm: number;
  /** Foreground colour (the closest parallax layer). */
  readonly foreground: number;
  /** HUD / parchment ink colour. */
  readonly ink: number;
  /** Parchment / paper background colour. */
  readonly parchment: number;
  /** Subject accent (used by sprite banks for highlighting). */
  readonly accent: number;
}

export interface RealmSpriteBank {
  /** Decorative sprite key list (the per-realm ornament families). */
  readonly sprites: readonly string[];
  /** Particle emitter keys (consumed by `particles.ts`). */
  readonly emitters: readonly string[];
  /** Audio cue keys (consumed by `audio.ts`). */
  readonly audioCues: readonly string[];
}

export interface RealmBilingualLabel {
  readonly en: string;
  readonly ga: string;
}

export interface RealmDescriptor {
  readonly slug: SubjectSlug;
  readonly title: RealmBilingualLabel;
  readonly tagline: RealmBilingualLabel;
  readonly palette: RealmPalette;
  readonly sprites: RealmSpriteBank;
  /** The procedural canvas height — the viewport zooms to fit. */
  readonly canvasHeight: number;
  /** The 2.5D tilt angle in radians (the Hades-orthographic lean). */
  readonly tiltRadians: number;
}

export type RealmDescriptorMap = Readonly<Record<SubjectSlug, RealmDescriptor>>;