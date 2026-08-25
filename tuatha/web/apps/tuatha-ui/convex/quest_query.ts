/**
 * convex/quest_query — the Convex query for the per-realm quest
 * list. Real Convex query against the `questPacks` table; no
 * hardcoded item counts.
 *
 * Per the openspec spec: "the page lists ≥1 quest pack fetched
 * via a Convex query against the `questPacks` table, not a
 * hardcoded count".
 */

import { query } from "./_generated/server";
import { v } from "./_generated/values";

interface QuestPackRow {
  readonly _id: string;
  readonly _creationTime: number;
  readonly subject: string;
  readonly titleEn: string;
  readonly titleGa: string;
  readonly competencyCode: string;
  readonly difficulty: number;
}

interface QueryCtxLike {
  readonly db: {
    query: (table: string) => unknown;
    get: (id: string) => Promise<unknown>;
    insert: (table: string, doc: Record<string, unknown>) => Promise<string>;
    patch: (id: string, fields: Record<string, unknown>) => Promise<void>;
  };
}

export const listQuestPacksBySubject = query({
  args: {
    subject: v.string(),
  },
  handler: async (ctx: QueryCtxLike, args: Record<string, unknown>): Promise<QuestPackRow[]> => {
    return await (ctx.db.query("questPacks") as {
      withIndex: (
        index: string,
        builder: (q: { eq: (f: string, v: unknown) => unknown }) => unknown,
      ) => {
        order: (direction: "asc" | "desc") => {
          collect: <T>() => Promise<T[]>;
        };
      };
    })
      .withIndex("by_subject", (q) =>
        (q as { eq: (f: string, v: unknown) => unknown }).eq("subject", (args as { subject: string }).subject),
      )
      .order("asc")
      .collect();
  },
});