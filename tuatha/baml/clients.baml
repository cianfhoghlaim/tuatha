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

// The 4 model clients + the abstract "primary" alt are all that's needed
// for the current Phase 2 surface. Phase 4 (visual lore) will add the
// cocoindex/console gem as a separate client.
