# Spec Delta: tuatha-british-isles-mmo

## MODIFIED Requirements

### Requirement: 2D + 2.5D Hades-orthographic theming (formerly "The British Isles Formative Assessment MMO theme")

The system SHALL adopt the British Isles Formative Assessment MMO
theme per the canonical `cianfhoghlaim-educational-mmo` spec.
The 8 NCCA Leaving Certificate subjects are the canonical
content surface.

The theming SHALL be **2D + 2.5D Hades-orthographic**:
- **2D client**: TanStack Start file-based routing + SSR
- **2.5D client**: PixiJS v8 renderer with pixi-viewport
  orthographic camera + layered parallax (sky / midground /
  gameplay / foreground / HUD) + pixi-particle + pixi-sound
- **NO 3D worlds, NO Babylon.js, NO SpacetimeDB, NO Rust crates**

The 8 per-subject realm scenes (the "realms"):
- `mathematics` — Library of Infinite Proofs (deep blue +
  parchment, Fibonacci spiral particles)
- `applied_mathematics` — Workshop of Applied Forces (amber +
  iron, mechanical gears + projectile arcs)
- `chemistry` — Periodic Alchemist's Hall (green + copper,
  bubbling flasks + reaction sparks)
- `geography` — Atlas of the British Isles (teal + terracotta,
  wind + rain + sea foam)
- `history` — Long Hall of Chronicles (burgundy + gold, time-sand
  + torch flames)
- `english` — Garden of Living Tongues (forest green + cream,
  quill-pen trails + book-pages)
- `gaeilge` — The Celtic Crossroads (Connemara purple + bog-oak
  black, clóscríobh + bodhrán rhythm)
- `computer_science` — The Silicon Atelier (cyan + charcoal,
  circuit traces + data-flow particles)

**The 6 deprecated themes are HARD-ARCHIVED**:

- ~~Pent-Elemental Cosmology~~ (5 realms: Spirit / Water / Fire
  / Earth / Air) — archived
- ~~Babylon.js 3D~~ game front-end — replaced with the TanStack
  Start 2D + PixiJS 2.5D client
- ~~SpacetimeDB v2~~ game engine backend — replaced with Convex +
  Hono + Dagster + DuckLake
- ~~Crypteolas financial token~~ — replaced with the
  educational-credential badge system
- ~~Anam Cara~~ soul friend mechanic — replaced with the 4 BIEP
  hackathon features
- ~~Brown Ajah theming~~ (the 8 NCCA subject ↔ Tuatha Dé deity
  mapping is preserved as `tuatha/subjects/character.py` but the
  "Brown Ajah" name is dropped)

The technological choices that ARE preserved:
- The 8 NCCA subject agents (refactored into `tuatha/subjects/`)
- The 40 subject-specific tools (refactored into `tuatha/tools/`)
- The 12-agent fleet pattern (root_agent + curriculum_agent + ...)
- The 3 educational agents (refactored into
  `tuatha/agents/educational/`)
- The 4 BIEP hackathon features (refactored into
  `tuatha/agents/hackathon/`)
- The media_intel pipeline (moved to `tuatha/agents/media_intel/`)
- The BAML extraction + DLT + Dagster + CocoIndex + marimo pipeline
  stack
- The Hono + Convex + TanStack Start + CopilotKit web stack
- The PixiJS v8 + pixi-viewport + pixi-particle + pixi-sound
  2D + 2.5D graphics stack (NEW)
- The LiteLLM + Cognee + Graphiti + LanceDB + Letta memory stack
- The educational-credential badge system (the previous
  `crypteolas/` financial-token system is archived)

#### Scenario: A user opens the new `tuatha/` project for the first time

- **WHEN** the user runs `tuatha --version`
- **THEN** the project reports version `0.2.0` (the
  multi-model + 2.5D update) + the British Isles Formative
  Assessment MMO theme description
- **AND** the project does NOT contain the 6 deprecated themes
  (verified by `tuatha --audit`)
- **AND** the project references the `leabharlann` + `bonneagar`
  sibling repos via the standard cross-repo sync contract

## ADDED Requirements

### Requirement: Multi-model asset pipeline via Unsloth Studio

The system SHALL route every image-gen + VLM call through the
multi-model asset pipeline at
`tuatha/asset_generation/{image_gen,vlm}/`, which resolves
`MODEL_REGISTRY.resolve(family, role)` for each of the 7 image-gen
entries (`local/image/{flux2-dev, z-image-turbo, qwen-image, fibo,
sdxl, diffusiongemma-26b-a4b, qwen-image-2512}`) and each of the
3 VLM analysis entries (`molmo2-8b`, `qwen3-vl-8b-instruct`,
`olmOCR-2-7B-1025`). The pipeline SHALL route Unsloth-served
models to `unsloth.cianfhoghlaim.ie:8889` via the `UnslothClient`
at `tuatha/asset_generation/unsloth_client.py`.

#### Scenario: FIBO diagram generated via the multi-model router

- **GIVEN** a Mathematics LO with a `SyllabusDocument` and
  `SyllabusDiagram` records
- **WHEN** `image_gen_router.generate_diagram(role="fibo", ...)` runs
- **THEN** `MODEL_REGISTRY.resolve("image_gen", "fibo")` returns
  `"local/image/fibo"`
- **AND** the UnslothClient routes to `unsloth.cianfhoghlaim.ie:8889`
- **AND** the diagram URI is persisted to the per-subject LanceDB
  `_metadata.diagram_uri` field

#### Scenario: Qwen-Image-2512 subject-icon rendered via Unsloth

- **GIVEN** a Chemistry subject-icon request (for the realm canvas
  sprite bank)
- **WHEN** `image_gen_router.generate_diagram(role="unsloth_qwen_image", ...)`
  runs
- **THEN** `MODEL_REGISTRY.resolve("image_gen", "unsloth_qwen_image")`
  returns `"local/image/qwen-image-2512"`
- **AND** the UnslothClient routes to `unsloth.cianfhoghlaim.ie:8889/v1/images/generations`
- **AND** the rendered icon is cached in Convex `files` keyed by
  `subject + version + seed`

#### Scenario: Z-Image-Turbo fast preview rendered for quest feedback

- **GIVEN** a student completes a formative item and the system wants
  to give a fast visual feedback (< 1s)
- **WHEN** `image_gen_router.generate_diagram(role="z_image", ...)` runs
- **THEN** `MODEL_REGISTRY.resolve("image_gen", "z_image")` returns
  `"local/image/z-image-turbo"`
- **AND** the UnslothClient routes to `unsloth.cianfhoghlaim.ie:8889`
- **AND** the preview image is returned within 1s (the turbo
  variant's latency budget)

#### Scenario: FLUX.2 stylised emblem rendered for the mastery dashboard

- **GIVEN** a student has a top subject (e.g., `mathematics`) and
  the mastery dashboard wants a stylised emblem
- **WHEN** `image_gen_router.generate_diagram(role="flux", ...)` runs
- **THEN** `MODEL_REGISTRY.resolve("image_gen", "flux")` returns
  `"local/image/flux2-dev"`
- **AND** the UnslothClient routes to `unsloth.cianfhoghlaim.ie:8889`
- **AND** the emblem is cached in Convex `files` keyed by
  `top_subject + student_id + seed`