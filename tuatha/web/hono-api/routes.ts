// tuatha.web.hono-api.routes — the 5 canonical Phase 4 routes.
import { Hono } from "hono";
import { db } from "./db.ts";
import type {
  Phase4ScoreRequest, Phase4ScoreResponse,
  Phase4ChatRequest, Phase4ChatResponse,
  Phase4RungRow, Phase4Provenance, Phase4BadgeRecord,
} from "./types.ts";

export const routes = new Hono()
  // GET /api/badges/:student_id
  .get("/api/badges/:student_id", async (c) => {
    const id = c.req.param("student_id");
    const rows = await db.query<Phase4BadgeRecord>(
      "SELECT student_id, subject, level, rung5_root, rung1_sha256, "
      "minted_at FROM badges WHERE student_id = ?", [id]);
    return c.json({ ok: true, data: rows, status: 200 });
  })

  // GET /api/curriculum/:jurisdiction
  .get("/api/curriculum/:jurisdiction", async (c) => {
    const j = c.req.param("jurisdiction");
    const rows = await db.query<Phase4RungRow>(
      "SELECT subject, category, language, rung, source_url, source_page "
      "FROM rung1_documents WHERE jurisdiction = ?", [j]);
    return c.json({ ok: true, data: rows, status: 200 });
  })

  // POST /api/score
  .post("/api/score", async (c) => {
    const body = await c.req.json<Phase4ScoreRequest>();
    // Production: invoke the Phase 2 BAML ScoreSubjectFormativeResponse
    return c.json<Phase4ScoreResponse>({
      ok: true, status: 200,
      data: { grade: 0.85, feedback_en: "Good work.",
              feedback_ga: "Obair mhaith.", badge_emitted: true },
    });
  })

  // POST /api/agent/chat
  .post("/api/agent/chat", async (c) => {
    const body = await c.req.json<Phase4ChatRequest>();
    return c.json<Phase4ChatResponse>({
      ok: true, status: 200,
      data: {
        reply_en: "[subject agent answer]",
        reply_ga: "[freagra an ghníomhaire]",
        provenance: {
          rung1_sha256: "(read from baml_extractions)",
          rung5_root: "(read from anchor_assets)",
          leaf_count: 0,
        },
      },
    });
  })

  // GET /api/rung5/root
  .get("/api/rung5/root", async (c) => {
    const row = await db.query<{ rung5_root: string }>(
      "SELECT rung5_root FROM anchor_metadata ORDER BY computed_at DESC LIMIT 1");
    const root = row[0]?.rung5_root ?? "0".repeat(64);
    return c.json({ ok: true, data: { rung5_root: root }, status: 200 });
  });
