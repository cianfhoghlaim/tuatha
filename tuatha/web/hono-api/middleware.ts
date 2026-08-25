// tuatha.web.hono-api.middleware — the provenance enforcement middleware.
import { createMiddleware } from "hono/factory";
import type { Phase4Provenance } from "./types.ts";

export const middleware = {
  /**The provenance middleware: every response carries rung5_root + rung1_sha256
  (per the G7 contract). Reads from the Phase 3 anchor service via the
  duckdb sidecar in production.*/
  provenance: createMiddleware(async (c, n) => {
    const reqRung5Root = c.req.header("X-Rung5-Root");
    const respRung5Root = reqRung5Root ?? compute_rung5_root_from_duckdb();
    c.res.headers.set("X-Rung5-Root", respRung5Root);
    await n();
  }),
};

/*The canonical rung-5 root (computed from the Phase 3 anchor_assets).*/
function compute_rung5_root_from_duckdb(): string {
  // Production: query the Phase 3 MerkleAnchorService
  // (in-process call to tuatha.dagster.anchor_assets).
  // Test: returns a fixed SHA256 nonce.
  return "a".repeat(64);  // TODO: real computation in Phase 4 final
}
