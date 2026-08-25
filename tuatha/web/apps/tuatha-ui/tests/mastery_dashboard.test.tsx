/**
 * mastery_dashboard.test.tsx — unit tests for the mastery chart
 * + emblem cache helper.
 *
 * Per the spec, the mastery dashboard exposes:
 * - the 8-axis radar chart (one axis per NCCA subject)
 * - the per-student emblem (cached by `topSubject + studentId + seed`)
 *
 * The test asserts:
 * - `topSubject(series)` returns the axis with the highest score
 * - `buildEmblemKey` / `defaultEmblemSeed` produce stable keys
 * - `isEmblemCacheFresh` correctly distinguishes cache hits/misses
 * - the `SUBJECT_AXES` registry exposes 8 axes in the canonical order
 */

import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import {
  MasteryChart,
  SUBJECT_AXES,
  topSubject,
  type MasterySeries,
} from "@tuatha/mastery-chart";
import {
  buildEmblemKey,
  defaultEmblemSeed,
  isEmblemCacheFresh,
} from "../src/lib/emblem";

describe("mastery-chart · axis registry", () => {
  it("exposes 8 axes in the canonical NCCA order", () => {
    expect(SUBJECT_AXES.length).toBe(8);
    expect(SUBJECT_AXES.map((a) => a.key)).toEqual([
      "mathematics",
      "applied_mathematics",
      "chemistry",
      "geography",
      "history",
      "english",
      "gaeilge",
      "computer_science",
    ]);
  });

  it("every axis has both EN and GA labels", () => {
    for (const axis of SUBJECT_AXES) {
      expect(axis.en).not.toBe("");
      expect(axis.ga).not.toBe("");
    }
  });
});

describe("mastery-chart · topSubject helper", () => {
  it("returns the axis with the highest mastery score", () => {
    const series: MasterySeries = {
      studentId: "stud-1",
      language: "en",
      points: [
        { subject: "mathematics", score: 80 },
        { subject: "chemistry", score: 90 },
        { subject: "gaeilge", score: 60 },
      ],
    };
    expect(topSubject(series)).toBe("chemistry");
  });

  it("breaks ties using the canonical axis order", () => {
    const series: MasterySeries = {
      studentId: "stud-2",
      language: "en",
      points: [
        { subject: "computer_science", score: 50 },
        { subject: "mathematics", score: 50 },
      ],
    };
    expect(topSubject(series)).toBe("mathematics");
  });
});

describe("mastery-chart · MasteryChart render", () => {
  it("renders an svg with the student id in the aria-label", () => {
    const series: MasterySeries = {
      studentId: "stud-3",
      language: "en",
      points: SUBJECT_AXES.map((axis) => ({ subject: axis.key, score: 60 })),
    };
    render(<MasteryChart series={series} />);
    const img = screen.getByRole("img");
    expect(img.getAttribute("aria-label")).toBe("Mastery chart for student stud-3");
    expect(img.getAttribute("data-student-id")).toBe("stud-3");
    expect(img.getAttribute("data-language")).toBe("en");
  });

  it("renders the GA labels when the language is ga", () => {
    const series: MasterySeries = {
      studentId: "stud-4",
      language: "ga",
      points: SUBJECT_AXES.map((axis) => ({ subject: axis.key, score: 60 })),
    };
    const { container } = render(<MasteryChart series={series} />);
    expect(container.querySelector('[data-language="ga"]')).not.toBeNull();
  });
});

describe("lib/emblem · cache helpers", () => {
  it("buildEmblemKey produces the canonical key tuple", () => {
    const key = buildEmblemKey("stud-5", "gaeilge", 42);
    expect(key).toEqual({ studentId: "stud-5", topSubject: "gaeilge", seed: 42 });
  });

  it("defaultEmblemSeed is stable across calls for the same student", () => {
    const first = defaultEmblemSeed("stud-6");
    const second = defaultEmblemSeed("stud-6");
    expect(first).toBe(second);
    expect(first).toBeGreaterThan(0);
  });

  it("defaultEmblemSeed differs for different students", () => {
    const a = defaultEmblemSeed("stud-7a");
    const b = defaultEmblemSeed("stud-7b");
    expect(a).not.toBe(b);
  });

  it("isEmblemCacheFresh reports false for a null cache entry", () => {
    const key = buildEmblemKey("stud-8", "history", 99);
    expect(isEmblemCacheFresh(null, key)).toBe(false);
  });

  it("isEmblemCacheFresh reports true for a matching, populated entry", () => {
    const key = buildEmblemKey("stud-9", "chemistry", 11);
    const entry = {
      studentId: "stud-9",
      topSubject: "chemistry" as const,
      seed: 11,
      imageUrl: "https://emblems.tuatha.ie/test.svg",
      modelId: "local/image/fibo",
      modelVersion: "v0",
    };
    expect(isEmblemCacheFresh(entry, key)).toBe(true);
  });

  it("isEmblemCacheFresh reports false for a key mismatch", () => {
    const key = buildEmblemKey("stud-10", "chemistry", 11);
    const entry = {
      studentId: "stud-10",
      topSubject: "mathematics" as const,
      seed: 11,
      imageUrl: "https://emblems.tuatha.ie/test.svg",
      modelId: "local/image/fibo",
      modelVersion: "v0",
    };
    expect(isEmblemCacheFresh(entry, key)).toBe(false);
  });
});