/**
 * Convex runtime API — the stub for `./_generated/api`.
 *
 * Mirrors the structure produced by `npx convex codegen`. Each
 * query / mutation defined in `convex/*.ts` is re-exported here
 * for client-side `useQuery` / `useMutation` calls.
 */

export const api = {
  quest_query: {
    listQuestPacksBySubject: {
      _type: "query" as const,
    },
  },
  badge_query: {
    listBadgesByStudent: {
      _type: "query" as const,
    },
  },
  emblem: {
    getEmblem: {
      _type: "query" as const,
    },
    upsertEmblem: {
      _type: "mutation" as const,
    },
    ensureEmblem: {
      _type: "mutation" as const,
    },
  },
} as const;

export type Api = typeof api;