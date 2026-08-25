/**
 * realm_canvas.test.ts — PixiJS v8 smoke test for the realm canvas.
 *
 * Per the spec, the smoke test verifies:
 * - every subject descriptor resolves through `loadRealmDescriptor`
 * - every palette has 7 fields (deep / mid / realm / foreground /
 *   ink / parchment / accent)
 * - every subject maps to ≥1 emitter family
 * - the `TuathaRealmCanvas` class can be instantiated (no PixiJS
 *   boot — just the constructor + `descriptor` accessor)
 * - the `EMITTER_FAMILIES` registry exposes the 8 expected keys
 *
 * The full PixiJS v8 mount is exercised in the live route smoke
 * test (G10 in the openspec quality gates) — the unit tests
 * here focus on the pure-JS contract surface.
 */

import { describe, expect, it } from "vitest";
import {
  ALL_SUBJECT_SLUGS,
  EMITTER_FAMILIES,
  TuathaRealmCanvas,
  iterRealmDescriptors,
  loadRealmDescriptor,
} from "@tuatha/realm-canvas";

describe("realm-canvas · subject registry", () => {
  it("exposes exactly 8 NCCA subjects", () => {
    expect(ALL_SUBJECT_SLUGS.length).toBe(8);
  });

  it("resolves every subject slug to a descriptor", () => {
    for (const slug of ALL_SUBJECT_SLUGS) {
      const descriptor = loadRealmDescriptor(slug);
      expect(descriptor.slug).toBe(slug);
    }
  });

  it("iterRealmDescriptors yields 8 entries", () => {
    let count = 0;
    for (const descriptor of iterRealmDescriptors()) {
      count += 1;
      expect(descriptor.slug).toBeDefined();
    }
    expect(count).toBe(8);
  });
});

describe("realm-canvas · palette contract", () => {
  for (const slug of ALL_SUBJECT_SLUGS) {
    it(`the ${slug} realm declares 7 palette fields`, () => {
      const descriptor = loadRealmDescriptor(slug);
      const fields = ["deep", "mid", "realm", "foreground", "ink", "parchment", "accent"] as const;
      for (const field of fields) {
        expect(typeof descriptor.palette[field]).toBe("number");
        expect(descriptor.palette[field]).toBeGreaterThanOrEqual(0x000000);
        expect(descriptor.palette[field]).toBeLessThanOrEqual(0xffffff);
      }
    });
  }

  it("the mathematics palette is deep blue + parchment", () => {
    const descriptor = loadRealmDescriptor("mathematics");
    expect(descriptor.palette.deep).toBe(0x0b1733);
    expect(descriptor.palette.parchment).toBe(0xf6efd9);
  });

  it("the gaeilge palette is Connemara purple + bog-oak black", () => {
    const descriptor = loadRealmDescriptor("gaeilge");
    expect(descriptor.palette.deep).toBe(0x0d0a18);
    expect(descriptor.palette.accent).toBe(0xa96cd6);
  });

  it("the computer_science palette is cyan + charcoal", () => {
    const descriptor = loadRealmDescriptor("computer_science");
    expect(descriptor.palette.realm).toBe(0x1f3340);
    expect(descriptor.palette.accent).toBe(0x36d6c0);
  });
});

describe("realm-canvas · emitter registry", () => {
  it("exposes the 8 canonical emitter families", () => {
    const families = Object.keys(EMITTER_FAMILIES).sort();
    expect(families).toEqual([
      "bubblingFlasks",
      "circuitTraces",
      "closcríobh",
      "fibonacciSpiral",
      "gearMech",
      "reactionSparks",
      "timeSand",
      "wind",
    ]);
  });

  for (const slug of ALL_SUBJECT_SLUGS) {
    it(`the ${slug} realm declares ≥1 emitter`, () => {
      const descriptor = loadRealmDescriptor(slug);
      expect(descriptor.sprites.emitters.length).toBeGreaterThanOrEqual(1);
    });
  }

  it("mathematics uses the fibonacciSpiral emitter", () => {
    const descriptor = loadRealmDescriptor("mathematics");
    expect(descriptor.sprites.emitters).toContain("fibonacciSpiral");
  });

  it("chemistry uses bubblingFlasks + reactionSparks", () => {
    const descriptor = loadRealmDescriptor("chemistry");
    expect(descriptor.sprites.emitters).toContain("bubblingFlasks");
    expect(descriptor.sprites.emitters).toContain("reactionSparks");
  });

  it("computer_science uses circuitTraces", () => {
    const descriptor = loadRealmDescriptor("computer_science");
    expect(descriptor.sprites.emitters).toContain("circuitTraces");
  });
});

describe("realm-canvas · bilingual labels", () => {
  for (const slug of ALL_SUBJECT_SLUGS) {
    it(`the ${slug} realm has EN + GA title + tagline`, () => {
      const descriptor = loadRealmDescriptor(slug);
      expect(descriptor.title.en).not.toBe("");
      expect(descriptor.title.ga).not.toBe("");
      expect(descriptor.tagline.en).not.toBe("");
      expect(descriptor.tagline.ga).not.toBe("");
    });
  }
});

describe("realm-canvas · TuathaRealmCanvas class", () => {
  it("the class instantiates without booting PixiJS", () => {
    const host = document.createElement("div");
    document.body.appendChild(host);
    const canvas = new TuathaRealmCanvas(host, {
      subject: "mathematics",
      width: 320,
      height: 240,
    });
    expect(canvas.isMounted).toBe(false);
    expect(canvas.descriptor).toBeNull();
  });
});