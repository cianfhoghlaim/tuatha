// tuatha.web.hono-api.types — shared TypeScript types (Phase 4 contracts).
import type { ContentfulStatusCode } from "hono/utils/http-status";

export interface Phase4RungRow {
  subject: string;
  category: "syllabus" | "past_paper" | "marking_scheme" | "formative_item" | "response_score";
  language: "en" | "ga";
  rung: 1 | 2 | 3 | 4 | 5;
  source_url: string;
  source_page: number;
  rung5_root?: string;
  output_json?: string;
  confidence?: number;
}

export interface Phase4Provenance {
  rung1_sha256: string;
  rung5_root: string;
  leaf_count: number;
}

export interface Phase4BadgeRecord {
  student_id: string;
  subject: string;
  level: string;
  rung5_root: string;
  rung1_sha256: string;
  minted_at: string;
}

export interface Phase4ApiResponse<T = unknown> {
  ok: boolean;
  data?: T;
  error?: string;
  status: ContentfulStatusCode;
}

export interface Phase4ScoreRequest {
  item_id: string;
  student_response: string;
  response_format: string;
  time_taken_seconds: number;
  hints_used: number;
  subject: string;
  language: "en" | "ga";
}

export interface Phase4ScoreResponse extends Phase4ApiResponse<{
  grade: number;
  feedback_en: string;
  feedback_ga: string;
  badge_emitted: boolean;
}> {}

export interface Phase4ChatRequest {
  student_id: string;
  subject: string;
  prompt: string;
}

export interface Phase4ChatResponse extends Phase4ApiResponse<{
  reply_en: string;
  reply_ga: string;
  provenance: Phase4Provenance;
}> {}
