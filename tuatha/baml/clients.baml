// tuatha.baml.clients — the canonical BAML client configuration.

Per the centralized-schema-registry contract: BAML is the
single source of truth; Pydantic + Zod + Convex + DuckLake DDL
are all codegen. The clients.baml declares the LiteLLM proxy
that all 8 per-subject + 3 hackathon + 1 media_descriptor BAML
functions route through.
*/
// Use the canonical LiteLLM gateway (Locket-injected).
client<llm> litellm_proxy {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key "LITELLM_API_KEY"
  }
}

// Use the canonical minimax-3 model (resolved via MODEL_REGISTRY
// at runtime; BAML picks this name as the model identifier).
client<llm> minimax {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key "LITELLM_API_KEY"
    model "minimax-3"
  }
}

client<llm> qwen3_vl_8b {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key "LITELLM_API_KEY"
    model "qwen3-vl-8b"
  }
}

client<llm> qwen_36_27b_mtp {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key "LITELLM_API_KEY"
    model "qwen3.6-27b-mtp"
  }
}

client<llm> molmo2_8b {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key "LITELLM_API_KEY"
    model "molmo2-8b"
  }
}

client<llm> olmocr_2_7b {
  provider "openai-generic"
  options {
    base_url "https://litellm.cianfhoghlaim.ie/v1"
    api_key "LITELLM_API_KEY"
    model "olmocr-2-7b"
  }
}
