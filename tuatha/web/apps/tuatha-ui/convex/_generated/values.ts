/**
 * Convex runtime — the stub for `./_generated/values`.
 *
 * Mirrors the `convex/values` runtime module produced by the
 * Convex CLI. The minimal surface needed by `convex/*.ts` is
 * the `v` validator factory.
 */

export const v: {
  string: () => unknown;
  number: () => unknown;
  boolean: () => unknown;
  id: (table: string) => unknown;
  optional: (validator: unknown) => unknown;
  array: (validator: unknown) => unknown;
  object: (fields: Record<string, unknown>) => unknown;
} = {
  string: () => ({}),
  number: () => ({}),
  boolean: () => ({}),
  id: () => ({}),
  optional: (validator: unknown) => validator,
  array: (validator: unknown) => validator,
  object: (fields: Record<string, unknown>) => fields,
};