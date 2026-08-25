// tuatha.web.hono-api.server — the Hono backend entry point.
//
// All API routes for the British Isles MMO app. Reads from the
// Phase 1 DuckDB (rung 1 + 2), the Phase 2 BAML extractions
// (rung 3 + 4), and the Phase 3 Dagster asset graph (rung 5).
//
// Runs on:
//   bun run --hot web/hono-api/server.ts
//
// Routes:
//   GET  /api/badges/:student_id        -> the student's badge ledger
//   GET  /api/curriculum/:jurisdiction   -> the canonical curriculum
//   POST /api/score                     -> score a response (Phase 2 BAML)
//   POST /api/agent/chat               -> chat with a Phase 1 subject agent
//   GET  /api/rung5/root               -> the rung-5 Merkle root
//
// All responses are provenance-complete (G7): every record carries
// rung-1 sha256 + rung-2 page + rung-3 BAML function name.
import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import { routes } from "./routes.ts";
import { middleware } from "./middleware.ts";
import { types } from "./types.ts";

const app = new Hono();
app.use("*", logger());
app.use("*", cors());
app.use("*", middleware.provenance);
app.route("/", routes);

export default app;
export type AppType = typeof app;
