// tuatha/baml/badge_reissue.baml — the canonical BAML contract for the Math badge re-issuance backfill.
//
// Added 2026-08-27 per the
// `2026-08-27-tuatha-let-ta-id-rotation-v1` change. Phase A rotated
// the badge_id f-string in `tuatha/tools/mathematics_response_score.py`
// from `kcg-mathematics-...` → `cianfhoghlaim-mathematics-...`. The
// badges minted between the 2026-01-01 launch and 2026-08-27 still
// carry the legacy prefix; this BAML function is the backfill that
// re-issues them under the canonical prefix.
//
// INVARIANT — hash-stable Merkle leaf:
// The new badge MUST carry the SAME `evidence_hash` as the legacy
// badge. The Merkle anchor binds the hash, not the human-readable
// ID; re-issuing does NOT create duplicate leaves. Re-issuing is
// therefore idempotent and safe to re-run.
//
// Routes through `MODEL_REGISTRY.resolve("text_llm", "subject_agent")`.
// Cost-floor model — the re-issuance is a deterministic ID rewrite,
// not an extraction; we deliberately use the gpt_4o_mini client
// (the canonical non-critical-path fallback).

client<llm> subject_agent {
  provider "openai-generic"
  base_url env.LITELLM_URL
  api_key  env.LITELLM_API_KEY
  model_name env.TEXT_MODEL_SUBJECT_AGENT
}

// ── Schema ────────────────────────────────────────────────────────────
// The Badge class mirrors `tuatha.badges.schema.SkillTreeBadge` (the
// Pydantic v2 source of truth for off-chain credential records).
// Only the canonical badge_id + evidence_hash + provenance fields
// are surfaced here — the full Pydantic model carries 12 fields,
// most of which are noise for the re-issuance backfill.

class BadgeReissueInput {
  legacy_badge_id   string                                // "kcg-mathematics-<item>-<grade>"
  canonical_prefix  string                                // "cianfhoghlaim-mathematics-"
  item_id           string
  grade             float
  evidence_hash     string                                // 64-hex SHA-256, preserved verbatim
  date_earned       string                                // ISO-8601 UTC, preserved verbatim
  agent_issuer      string                                // "math_agent" (preserved)
}

class Badge {
  badge_id           string                               // NEW canonical ID
  legacy_badge_id    string                               // ORIGINAL ID, kept for audit
  item_id            string
  grade              float
  evidence_hash      string                               // IDENTICAL to legacy — hash-stable Merkle leaf
  date_earned        string
  agent_issuer       string
  reissued_at        string                               // ISO-8601 UTC of the re-issuance batch
  reissue_change_id  string                               // "2026-08-27-tuatha-let-ta-id-rotation-v1"
  hash_preserved     bool                                 // sanity: evidence_hash matches legacy
}


// ── Function ──────────────────────────────────────────────────────────

function ReissueBadge(
  badge_id: string,                                        // legacy "kcg-mathematics-<item>-<grade>"
  new_prefix: string,                                      // canonical "cianfhoghlaim-mathematics-"
) -> Badge {
  client subject_agent
  prompt #"
    You are the canonical Math badge re-issuance backfill for the
    2026-08-27 KCG rename. The legacy badge was minted under the
    `kcg-` prefix; the new badge must be re-issued under the
    `cianfhoghlaim-` prefix WITHOUT changing the `evidence_hash`.

    Legacy badge_id: {{ badge_id }}
    New prefix:      {{ new_prefix }}

    Apply the 4-STEP REWRITE:

    1. STRIP: drop the legacy `kcg-mathematics-` prefix from the
       legacy badge_id, keeping the `<item_id>-<grade>` tail
       (e.g., `kcg-mathematics-LC-MATHS-LO-2.4-0.85` → tail
       `LC-MATHS-LO-2.4-0.85`).

    2. PREFIX: prepend the new canonical prefix to the tail
       (e.g., new badge_id = `cianfhoghlaim-<tail>`).

    3. PRESERVE: the evidence_hash from the legacy record must
       carry over VERBATIM. The Merkle anchor binds the hash,
       not the human-readable ID; re-issuing under a new prefix
       does NOT create a new Merkle leaf.

    4. ANNOTATE: stamp `reissued_at` (ISO-8601 UTC) +
       `reissue_change_id` (`2026-08-27-tuatha-let-ta-id-rotation-v1`)
       + `hash_preserved=true`.

    LANGUAGE: English only (no bilingual output — the badge_id is
    a machine-readable identifier; the bilingual metadata lives
    in the `competency_text` field of the full SkillTreeBadge
    row, which this backfill does not touch).

    Return a Badge matching the schema.
  "#
}


test reissue_badge_math_lc_2_4 {
  functions [ReissueBadge]
  input {
    badge_id   "kcg-mathematics-LC-MATHS-LO-2.4-0.85"
    new_prefix "cianfhoghlaim-mathematics-"
  }
  output {
    badge_id       "cianfhoghlaim-mathematics-LC-MATHS-LO-2.4-0.85"
    legacy_badge_id "kcg-mathematics-LC-MATHS-LO-2.4-0.85"
    item_id        "LC-MATHS-LO-2.4"
    grade          0.85
    hash_preserved true
  }
}
