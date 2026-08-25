/**
 * Convex runtime types — the stub for `./_generated/server`.
 *
 * The real Convex CLI generates this file via `npx convex dev`.
 * For offline typecheck (and for CI without a running Convex
 * deployment) we provide a minimal stub that matches the
 * public API surface used by `convex/*.ts`.
 *
 * Replace this stub by running `npx convex codegen` once the
 * deployment is provisioned.
 */

export interface QueryCtx {
  readonly db: {
    query: (table: string) => {
      withIndex: (
        index: string,
        builder: (q: IndexQueryBuilder) => IndexQueryBuilder,
      ) => {
        order: (direction: "asc" | "desc") => {
          collect: <T>() => Promise<T[]>;
          first: <T>() => Promise<T | null>;
        };
        collect: <T>() => Promise<T[]>;
        first: <T>() => Promise<T | null>;
      };
      order: (direction: "asc" | "desc") => {
        collect: <T>() => Promise<T[]>;
        first: <T>() => Promise<T | null>;
      };
      collect: <T>() => Promise<T[]>;
      first: <T>() => Promise<T | null>;
    };
    get: <T>(id: string) => Promise<T | null>;
    insert: (table: string, doc: Record<string, unknown>) => Promise<string>;
    patch: (id: string, fields: Record<string, unknown>) => Promise<void>;
  };
}

export interface IndexQueryBuilder {
  eq: (field: string, value: unknown) => IndexQueryBuilder;
}

export interface MutationCtx extends QueryCtx {}

export function query(args: {
  args: Record<string, unknown>;
  handler: (ctx: QueryCtx, args: Record<string, unknown>) => Promise<unknown>;
}): unknown {
  return args;
}

export function mutation(args: {
  args: Record<string, unknown>;
  handler: (ctx: MutationCtx, args: Record<string, unknown>) => Promise<unknown>;
}): unknown {
  return args;
}