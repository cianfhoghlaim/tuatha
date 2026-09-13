## MODIFIED Requirements

### Requirement: Tuatha ANAM extraction across 3 corpora

The `tuatha/agents/media_intel/media_descriptor_agent.py` SHALL
provide 6 extractor tools covering 5 media classes + the
Class F animation (X-Men: Evolution), specifically:

| Tool | Class | Medium | Default VLM | Source corpus |
|:--|:--|:--|:--|:--|
| `extract_comic_descriptor_tool` | A | comic | `qwen3-vl-8b` | Hickman Marvel run |
| `extract_prose_descriptor_tool` | B | prose | `qwen3.6-27b-mtp` | Wheel of Time |
| `extract_animation_descriptor_tool` | C | animation | `molmo2-8b` | ATLA + Korra + Aang-film |
| `extract_gameplay_descriptor_tool` | D | game | `qwen3-vl-8b` | Hades + WoW + Golden Sun + Pokémon |
| `extract_official_document_descriptor_tool` | E | document | `olmocr-2-7b-1025` | NCCA + SEC + UK/IE governments |
| `extract_xmen_descriptor_tool` (NEW 2026-08-27) | F | animation | `molmo2-8b` | X-Men: Evolution (2000-2003, Marvel Animation) |

Each extractor SHALL route through `MODEL_REGISTRY.resolve(family,
role)` (never a hardcoded model string).

#### Scenario: X-Men extractor routes through central registry

- **GIVEN** an X-Men: Evolution episode still passed to
  `extract_xmen_descriptor_tool(image)`
- **WHEN** the tool calls the BAML function
  `ExtractXmenDescriptor(image)`
- **THEN** the BAML function resolves the VLM via
  `MODEL_REGISTRY.resolve("ocr_vision", "xmen_scene")` (which
  returns the `qwen3-vl-8b-xmen-scene` entry per the 2026-08-27
  centralized-model-registry delta)
- **AND** the call emits a `agent.xmen_evolution.extract` Langfuse
  trace (via the `@trace_agent(subject)` decorator pattern)
- **AND** the resulting descriptor carries `character_name`,
  `character_team`, `power_class`, `ability_name` fields in
  addition to the standard 7-axis schema
