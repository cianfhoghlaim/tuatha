/**
 * convex/badge_query — the per-student badge query.
 *
 * The mastery dashboard fetches the student's `SkillTreeBadge`
 * rows to compute the 8-axis mastery score per subject. Real
 * Convex query against the `badges` table — no hardcoded item
 * counts.
 *
 * This file is required by the `/student/[id]/mastery` route
 * (which is in Phase 2 scope).
 */

import { query } from "./_generated/server";
import { v } from "./_generated/values";

interface BadgeRow {
  readonly _id: string;
  readonly _creationTime: number;
  readonly studentId: string;
  readonly subject: string;
  readonly competencyCode: string;
  readonly dateEarned: number;
}

interface QueryCtxLike {
  readonly db: {
    query: (table: string) => unknown;
    get: (id: string) => Promise<unknown>;
    insert: (table: string, doc: Record<string, unknown>) => Promise<string>;
    patch: (id: string, fields: Record<string, unknown>) => Promise<void>;
  };
}

export const listBadgesByStudent = query({
  args: {
    studentId: v.string(),
  },
  handler: async (ctx: QueryCtxLike, args: Record<string, unknown>): Promise<BadgeRow[]> => {
    return await (ctx.db.query("badges") as {
      withIndex: (
        index: string,
        builder: (q: { eq: (f: string, v: unknown) => unknown }) => unknown,
      ) => {
        order: (direction: "asc" | "desc") => {
          collect: <T>() => Promise<T[]>;
        };
      };
    })
      .withIndex("by_student", (q) =>
        (q as { eq: (f: string, v: unknown) => unknown }).eq("studentId", (args as { studentId: string }).studentId),
      )
      .order("desc")
      .collect();
  },
});