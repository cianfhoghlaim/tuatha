/**
 * audio — pixi-sound / @pixi/sound integration for the 8 realm
 * scenes.
 *
 * The audio controller defers actual audio loading to the
 * consuming app (the realm routes pre-load the cue URIs and
 * pass them in via `audioCues`). On the first user gesture the
 * controller unlocks the Web Audio context (browser autoplay
 * policy) and starts playing ambient realm cues.
 *
 * NO Babylon.js, NO SpacetimeDB. Web Audio + pixi-sound.
 */

import type { RealmDescriptor } from "./types.js";

export interface RealmAudioController {
  /** Unlock the Web Audio context (call inside a user gesture). */
  unlock(): Promise<void>;
  /** Play a one-shot cue by key (or default realm cue if no key). */
  playCue(cueKey?: string): void;
  /** Mute / unmute. */
  setMuted(muted: boolean): void;
  /** Tear down all sound instances. Safe to call repeatedly. */
  destroy(): void;
  readonly isUnlocked: boolean;
  readonly isMuted: boolean;
}

export interface RealmAudioOptions {
  /** Disable the audio system entirely (e.g. in tests). */
  readonly enabled?: boolean;
  /** Initial muted state (defaults to false). */
  readonly muted?: boolean;
}

/**
 * Stub implementation — the consuming route pre-loads real
 * @pixi/sound instances and overrides the `playCue` method.
 * The default implementation logs to `console.debug` so smoke
 * tests can verify the cue flow without booting real audio.
 */
export function createRealmAudio(
  descriptor: RealmDescriptor,
  options: RealmAudioOptions = {},
): RealmAudioController {
  const enabled = options.enabled ?? true;
  const played: string[] = [];
  let unlocked = !enabled;
  let muted = options.muted ?? false;

  return {
    get isUnlocked() {
      return unlocked;
    },
    get isMuted() {
      return muted;
    },
    async unlock() {
      unlocked = true;
    },
    playCue(cueKey) {
      const key = cueKey ?? descriptor.sprites.audioCues[0] ?? "ambient";
      played.push(key);
      if (enabled) {
        // eslint-disable-next-line no-console
        console.debug(`[realm-canvas:${descriptor.slug}] playCue(${key})`);
      }
    },
    setMuted(next) {
      muted = next;
    },
    destroy() {
      played.length = 0;
    },
  };
}