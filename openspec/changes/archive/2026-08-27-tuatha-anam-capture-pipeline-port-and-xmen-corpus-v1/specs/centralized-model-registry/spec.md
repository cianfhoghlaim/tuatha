## MODIFIED Requirements

### Requirement: Usage roles for ANAM capture pipeline

The `MODEL_REGISTRY` at
`meaisinfhoghlaim/models/model_registry.py` SHALL expose 2 NEW
usage roles in the `ocr_vision` family, specifically:

1. `hades_boon` — resolves to `qwen3-vl-8b-hades-boon` (the
   medium-tier Qwen3-VL-8B Unsloth GGUF, env var
   `VISION_MODEL_HADES`). Used by the
   `tuatha/baml/anam_capture.baml::ExtractHadesBoon` function
   and any non-BAML equivalent. The boon icons occupy ~5% of a
   1080p frame and carry dense overlaid text; needs the medium
   tier, not the light one.
2. `xmen_scene` — resolves to `qwen3-vl-8b-xmen-scene` (the
   medium-tier Qwen3-VL-8B Unsloth GGUF, env var
   `VISION_MODEL_XMEN`). Used by the
   `tuatha/baml/anam_xmen.baml::ExtractXmenScene` function and
   any non-BAML equivalent. 2000-2003 cel-shaded animation
   frames with mutant ability VFX; same tier as `hades_boon`
   because frames have similar density.

#### Scenario: hades_boon role resolves through central registry

- **GIVEN** the entry `qwen3-vl-8b-hades-boon` in
  `MODEL_REGISTRY` with `family="ocr_vision"`, `role="hades_boon"`,
  `unsloth_id="unsloth/Qwen3-VL-8B-Instruct-GGUF"`,
  `env_var="VISION_MODEL_HADES"`
- **WHEN** the operator runs
  `python3 -c "from meaisinfhoghlaim.models.registry import MODEL_REGISTRY; print(MODEL_REGISTRY.resolve('ocr_vision', 'hades_boon'))"`
- **THEN** the output is `"qwen3-vl-8b-hades-boon"`
- **AND** overriding the env var `VISION_MODEL_HADES=some/other-model`
  makes `MODEL_REGISTRY.resolve("ocr_vision", "hades_boon")`
  return `"some/other-model"`

#### Scenario: xmen_scene role resolves through central registry

- **GIVEN** the entry `qwen3-vl-8b-xmen-scene` in
  `MODEL_REGISTRY` with `family="ocr_vision"`, `role="xmen_scene"`,
  `unsloth_id="unsloth/Qwen3-VL-8B-Instruct-GGUF"`,
  `env_var="VISION_MODEL_XMEN"`
- **WHEN** the operator runs
  `python3 -c "from meaisinfhoghlaim.models.registry import MODEL_REGISTRY; print(MODEL_REGISTRY.resolve('ocr_vision', 'xmen_scene'))"`
- **THEN** the output is `"qwen3-vl-8b-xmen-scene"`
- **AND** overriding the env var `VISION_MODEL_XMEN=some/other-model`
  makes `MODEL_REGISTRY.resolve("ocr_vision", "xmen_scene")`
  return `"some/other-model"`

#### Scenario: Centralized-registry invariant preserved

- **GIVEN** the 2 NEW entries (`hades_boon`, `xmen_scene`)
  added to `MODEL_REGISTRY`
- **WHEN** `mise run lint:registry` runs
- **THEN** the lint returns 0 hardcoded model strings
- **AND** every consumer routes through
  `MODEL_REGISTRY.resolve(family, role)` per the
  centralized-registry invariant
