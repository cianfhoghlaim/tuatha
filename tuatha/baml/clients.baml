// tuatha/baml/clients.baml — the canonical BAML client registry.
//
// 4 model families (per the model registry + the G10 contract: no
// hardcoded model strings anywhere; per-resolution via MODEL_REGISTRY):
//   - minimax-3     → the canonical primary fallback (per the parent monorepo)
//   - qwen3-vl-8b   → the per-medium extractor for visual sources (comic + animation + gameplay)
//   - olmocr-2-7b  → the per-medium extractor for PDF sources (prose + official)
//   - gpt-4o-mini   → the canonical cost-floor fallback for non-critical paths
//
// Operator overrides: set LITELLM_API_KEY + LITELLM_API_BASE in the
// Locket-injected secrets surface. Local dev defaults to the parent's
// litellm.cianfhoghlaim.ie proxy.

client<llm> minimax {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key  "LITELLM_API_KEY"
    model   "minimax-3"
    max_input_tokens 32000
    max_output_tokens 4096
  }
}

client<llm> qwen3_vl_8b {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key  "LITELLM_API_KEY"
    model   "qwen3-vl-8b"
    max_input_tokens 32768
    max_output_tokens 4096
  }
}

client<llm> olmocr_2_7b {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key  "LITELLM_API_KEY"
    model   "olmocr-2-7b"
    max_input_tokens 32768
    max_output_tokens 8192
  }
}

client<llm> gpt_4o_mini {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key  "LITELLM_API_KEY"
    model   "gpt-4o-mini"
    max_input_tokens 16384
    max_output_tokens 4096
  }
}

client<llm> primary { provider "anthropic-generic" options { base_url "https://litellm.cianfhoghlaim.ie/v1" api_key "LITELLM_API_KEY" model "claude-haiku-4-5-20251001" max_input_tokens 200000 max_output_tokens 8192 } }

// NEW 2026-08-27 — 2 ANAM capture clients (hades_boon + xmen_scene).
// Routes through MODEL_REGISTRY via the env-var override.
client<llm> hades_boon {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key  "LITELLM_API_KEY"
    model   "qwen3-vl-8b-hades-boon"
    max_input_tokens 32768
    max_output_tokens 4096
  }
}

client<llm> xmen_scene {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key  "LITELLM_API_KEY"
    model   "qwen3-vl-8b-xmen-scene"
    max_input_tokens 32768
    max_output_tokens 4096
  }
}

// NEW 2026-08-27 — Hackathon agent client (marking_grader +
// adaptive_tutor + equivalency_generator + curriculum_change_sensor).
// All 4 BIEP hackathon features route through one canonical
// hackathon_agent role.
client<llm> hackathon_agent {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key  "LITELLM_API_KEY"
    model   "minimax-m3"
    max_input_tokens 32768
    max_output_tokens 4096
  }
}

// NEW 2026-08-27 — Subject agent client (the 8 NCCA subject
// agents: math + appm + chem + geog + hist + engl + gael + comp).
// All 8 route through one canonical subject_agent role.
client<llm> subject_agent {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key  "LITELLM_API_KEY"
    model   "minimax-m3"
    max_input_tokens 32768
    max_output_tokens 4096
  }
}

// NEW 2026-08-27 — Educational agent client (academic_history
// + celtic_grammar + celtic_morphology). Routes through the
// educational_agent role.
client<llm> educational_agent {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key  "LITELLM_API_KEY"
    model   "minimax-m3"
    max_input_tokens 32768
    max_output_tokens 4096
  }
}

// NEW 2026-08-27 — Media descriptor client (the 10-tool
// media_descriptor_agent). Routes through the media_descriptor
// role (the only one that stays in ocr_vision family — it
// actually needs a vision model).
client<llm> media_descriptor {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key  "LITELLM_API_KEY"
    model   "molmo2-8b"
    max_input_tokens 32768
    max_output_tokens 4096
  }
}

// The 4 model clients + the abstract "primary" alt + 4 NEW
// ANAM / agent clients are all that's needed for the current
// Phase 3 surface.
