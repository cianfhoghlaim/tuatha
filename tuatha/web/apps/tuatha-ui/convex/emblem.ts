/**
 * convex/emblem — the emblem upload + retrieval functions.
 *
 * The emblem cache is keyed by `top_subject + student_id + seed`.
 * Phase 1 wires the real FIBO image-gen call. Phase 2 stub
 * generates a deterministic placeholder URL from the same key,
 * so the cache contract is end-to-end testable today.
 */

import { mutation, query } from "./_generated/server";
import { v } from "./_generated/values";

interface EmblemRow {
  readonly _id: string;
  readonly _creationTime: number;
  readonly studentId: string;
  readonly topSubject: string;
  readonly seed: number;
  readonly imageUrl: string;
  readonly modelId: string;
  readonly modelVersion: string;
}

interface QueryCtxLike {
  readonly db: {
    query: (table: string) => unknown;
    get: (id: string) => Promise<unknown>;
    insert: (table: string, doc: Record<string, unknown>) => Promise<string>;
    patch: (id: string, fields: Record<string, unknown>) => Promise<void>;
  };
}

/**
 * Stub: deterministic placeholder URL. Phase 1 replaces this
 * with the real `MODEL_REGISTRY.resolve("image_gen", "fibo")`
 * call + the FIBO upload step.
 */
export function placeholderEmblemUrl(topSubject: string, studentId: string, seed: number): string {
  const hash = hashKey(`${topSubject}|${studentId}|${seed}`);
  return `https://emblems.tuatha.ie/placeholder/${topSubject}/${hash}.svg`;
}

function hashKey(input: string): string {
  let hash = 0;
  for (let i = 0; i < input.length; i += 1) {
    hash = (hash * 31 + input.charCodeAt(i)) | 0;
  }
  return Math.abs(hash).toString(36).padStart(8, "0");
}

export const getEmblem = query({
  args: {
    studentId: v.string(),
    topSubject: v.string(),
    seed: v.number(),
  },
  handler: async (ctx: QueryCtxLike, args: Record<string, unknown>): Promise<EmblemRow | null> => {
    const row = await (ctx.db.query("emblems") as {
      withIndex: (
        index: string,
        builder: (q: { eq: (f: string, v: unknown) => unknown }) => unknown,
      ) => {
        first: <T>() => Promise<T | null>;
      };
    })
      .withIndex("by_student_subject_seed", (q) =>
        (q as { eq: (f: string, v: unknown) => unknown }).eq("studentId", (args as { studentId: string }).studentId),
      )
      .first();
    return (row as EmblemRow | null) ?? null;
  },
});

export const upsertEmblem = mutation({
  args: {
    studentId: v.string(),
    topSubject: v.string(),
    seed: v.number(),
    imageUrl: v.string(),
    modelId: v.string(),
    modelVersion: v.string(),
  },
  handler: async (ctx: QueryCtxLike, args: Record<string, unknown>): Promise<EmblemRow> => {
    const a = args as {
      studentId: string;
      topSubject: string;
      seed: number;
      imageUrl: string;
      modelId: string;
      modelVersion: string;
    };
    const existing = await (ctx.db.query("emblems") as {
      withIndex: (
        index: string,
        builder: (q: { eq: (f: string, v: unknown) => unknown }) => unknown,
      ) => {
        first: <T>() => Promise<T | null>;
      };
    })
      .withIndex("by_student_subject_seed", (q) =>
        (q as { eq: (f: string, v: unknown) => unknown }).eq("studentId", a.studentId),
      )
      .first();

    if (existing !== null && existing !== undefined) {
      const id = (existing as EmblemRow)._id;
      await ctx.db.patch(id, {
        imageUrl: a.imageUrl,
        modelId: a.modelId,
        modelVersion: a.modelVersion,
      });
      const refreshed = await ctx.db.get(id);
      if (refreshed === null) {
        throw new Error("Emblem row disappeared during upsert");
      }
      return refreshed as EmblemRow;
    }

    const newId = await ctx.db.insert("emblems", {
      studentId: a.studentId,
      topSubject: a.topSubject,
      seed: a.seed,
      imageUrl: a.imageUrl,
      modelId: a.modelId,
      modelVersion: a.modelVersion,
    });
    return {
      _id: newId,
      _creationTime: Date.now(),
      studentId: a.studentId,
      topSubject: a.topSubject,
      seed: a.seed,
      imageUrl: a.imageUrl,
      modelId: a.modelId,
      modelVersion: a.modelVersion,
    };
  },
});

/**
 * Generate the deterministic placeholder + upsert. The Phase 1
 * implementation will call the FIBO router before this and pass
 * the real `imageUrl` + `modelId` + `modelVersion`.
 */
export const ensureEmblem = mutation({
  args: {
    studentId: v.string(),
    topSubject: v.string(),
    seed: v.number(),
  },
  handler: async (ctx: QueryCtxLike, args: Record<string, unknown>): Promise<EmblemRow> => {
    const a = args as { studentId: string; topSubject: string; seed: number };
    const cached = await (ctx.db.query("emblems") as {
      withIndex: (
        index: string,
        builder: (q: { eq: (f: string, v: unknown) => unknown }) => unknown,
      ) => {
        first: <T>() => Promise<T | null>;
      };
    })
      .withIndex("by_student_subject_seed", (q) =>
        (q as { eq: (f: string, v: unknown) => unknown }).eq("studentId", a.studentId),
      )
      .first();

    const imageUrl = placeholderEmblemUrl(a.topSubject, a.studentId, a.seed);
    const modelId = "placeholder-stub";
    const modelVersion = "v0";

    if (cached !== null && cached !== undefined) {
      const id = (cached as EmblemRow)._id;
      await ctx.db.patch(id, { imageUrl, modelId, modelVersion });
      const refreshed = await ctx.db.get(id);
      if (refreshed === null) {
        throw new Error("Emblem row disappeared during ensure");
      }
      return refreshed as EmblemRow;
    }

    const newId = await ctx.db.insert("emblems", {
      studentId: a.studentId,
      topSubject: a.topSubject,
      seed: a.seed,
      imageUrl,
      modelId,
      modelVersion,
    });
    return {
      _id: newId,
      _creationTime: Date.now(),
      studentId: a.studentId,
      topSubject: a.topSubject,
      seed: a.seed,
      imageUrl,
      modelId,
      modelVersion,
    };
  },
});