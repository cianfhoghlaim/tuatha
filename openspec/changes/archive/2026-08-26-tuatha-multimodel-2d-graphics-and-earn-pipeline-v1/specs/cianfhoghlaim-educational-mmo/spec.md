# Spec Delta: cianfhoghlaim-educational-mmo

## MODIFIED Requirements

### Requirement: 2D + 2.5D TanStack Start game client (formerly "2D TanStack Start game client")

The system SHALL provide a TanStack Start game client at
`tuatha/web/apps/tuatha-ui/` on port 3080 with routes for the 8
subject realms, the student badge wallet, the cross-subject
mastery dashboard, the teacher view, the public Merkle anchor
verification page, AND a per-subject 2.5D Hades-orthographic
realm canvas. The client SHALL use BetterAuth (email/password +
SIWE wallet) for authentication, Convex for real-time state,
and CopilotKit AG-UI for streaming agent chat. The client SHALL
be bilingual EN + GA throughout. Subject realm pages SHALL render
quest content fetched from a real Convex query against generated
content — no hardcoded item counts or non-functional buttons.

The 2.5D Hades-orthographic canvas SHALL use PixiJS v8 (WebGL +
WebGPU backend) + pixi-viewport orthographic camera + layered
parallax (sky / midground / gameplay / foreground / HUD) +
pixi-particle + pixi-sound. NO Babylon.js, NO SpacetimeDB, NO
3D worlds.

#### Scenario: Subject realm page renders real quest content + 2.5D background

- **GIVEN** the user navigates to `/realm/mathematics`
- **WHEN** the page loads
- **THEN** the page displays the Mathematics realm header
  (bilingual EN + GA)
- **AND** the page lists ≥1 quest pack fetched via a Convex
  query against the `questPacks` table, not a hardcoded count
- **AND** the "Start" button has a working `onClick` handler that
  begins a quest attempt
- **AND** the page mounts the `TuathaRealmCanvas` (PixiJS v8) with
  the per-subject palette (mathematics = deep blue + parchment +
  Fibonacci spiral particles)

#### Scenario: Student badge wallet renders

- **GIVEN** a student has ≥1 `SkillTreeBadge` in Convex
- **WHEN** the user navigates to `/student/<id>/badges`
- **THEN** the page displays ≥1 badge card with the badge id,
  framework, level, subject, competency code, date earned, and
  on-chain anchor
- **AND** the page links to the public verification page for each
  badge

#### Scenario: Cross-subject mastery dashboard renders

- **GIVEN** a student has badges in ≥2 subjects
- **WHEN** the user navigates to `/student/<id>/mastery`
- **THEN** the page displays a FalkorDB-backed visualisation of
  the student's mastery across the 8 NCCA subjects as an 8-axis
  spider chart
- **AND** the page renders a per-student emblem (FIBO-rendered,
  keyed to the student's top subject, cached in Convex `files`)

#### Scenario: Public anchor verification page renders

- **GIVEN** a date `2026-07-01` has a published Merkle anchor
- **WHEN** the user navigates to `/anchor/2026-07-01`
- **THEN** the page displays the Merkle root and the Base L2
  tx_hash
- **AND** the page accepts a badge `id + evidence_hash` and
  verifies the Merkle path against the on-chain root
- **AND** the verification result is a clear pass/fail indicator

## ADDED Requirements

### Requirement: Multi-model asset pipeline via Unsloth Studio

The system SHALL route every image-gen and VLM call through the
multi-model asset pipeline at `tuatha/asset_generation/{image_gen,vlm}/`,
which resolves `MODEL_REGISTRY.resolve(family, role)` for each of
the 7 image-gen entries (`local/image/{flux2-dev, z-image-turbo,
qwen-image, fibo, sdxl, diffusiongemma-26b-a4b, qwen-image-2512}`)
and each of the 3 VLM analysis entries (`molmo2-8b`,
`qwen3-vl-8b-instruct`, `olmOCR-2-7B-1025`). The pipeline SHALL
route Unsloth-served models to `unsloth.cianfhoghlaim.ie:8889`
via the `UnslothClient` at `tuatha/asset_generation/unsloth_client.py`.
The pipeline SHALL NOT contain any hardcoded model strings — the
`mise run lint:registry` CI gate enforces this.

#### Scenario: FIBO diagram generated via the multi-model router

- **GIVEN** a Mathematics LO with a `SyllabusDocument` and a
  `SyllabusDiagram` record (extracted by `ExtractSyllabusDiagram`)
- **WHEN** `image_gen_router.generate_diagram(role="fibo", ...)`
  runs
- **THEN** `MODEL_REGISTRY.resolve("image_gen", "fibo")` returns
  `"local/image/fibo"`
- **AND** the UnslothClient routes to `unsloth.cianfhoghlaim.ie:8889`
- **AND** the diagram URI is persisted to the per-subject
  LanceDB `_metadata.diagram_uri` field with `_metadata.source_pdf`,
  `_metadata.source_page`, `_metadata.model_id`, `_metadata.seed`

#### Scenario: VLM analysis of a syllabus PDF page image

- **GIVEN** a Chemistry syllabus PDF page image (PNG bytes)
- **WHEN** `vlm_router.analyse_page_image(role="diagram_pointing", ...)`
  runs
- **THEN** `MODEL_REGISTRY.resolve("ocr_vision", "default")` returns
  `"molmo2-8b"`
- **AND** the UnslothClient routes to `unsloth.cianfhoghlaim.ie:8889/v1/chat/completions`
- **AND** the analysis returns the bounding boxes + verbatim text
  for each detected diagram

### Requirement: 8-subject ADK fleet routing + Langfuse tracing

The system SHALL provide 8 ADK `LlmAgent`s (one per NCCA subject)
plus the `root_agent` updated to route keyword-level traffic to
them via the 8-bucket `ROUTING_KEYWORDS` map. Each subject agent
SHALL expose ≥5 tools (syllabus_lookup, past_paper_lookup,
marking_scheme_lookup, formative_item_generate, response_score).
Every BAML call SHALL be wrapped with the
`@trace_agent(subject)` Langfuse decorator from
`tuatha/observability/langfuse_traces.py`, emitting the
`agent.<subject>.extract` trace. Every response SHALL cite
`source_pdf + source_page` from the per-subject LanceDB table.

#### Scenario: Root agent routes to math_agent

- **GIVEN** the `root_agent` is configured with the 8-bucket
  `ROUTING_KEYWORDS` map
- **WHEN** a user query contains the keyword "differentiation"
- **THEN** the `root_agent` routes the query to `math_agent`
- **AND** the `math_agent` returns a response that references
  Mathematics syllabus content via its `math_syllabus_lookup` tool
- **AND** the Langfuse trace `agent.mathematics.extract` is emitted

### Requirement: Curriculum change detection sensor

The system SHALL provide a Dagster sensor that watches the 6
jurisdiction websites (NCCA + AQA + SQA + WJEC + CCEA + IoM) via
Firecrawl monitors. When a syllabus PDF URL changes, the sensor
SHALL fire the BIEP v3 5-phase re-run (BAML re-extract →
CocoIndex v1 re-embed → Cognee cognify → Graphiti temporal
memory → LanceDB re-index) for the affected subject, then
re-run `Generate<Subject>QuestPack`, diff the new quest-pack
against the prior one, and issue a new `SkillTreeBadge` with
`framework="ncca-lc"` and `version=<new_pdf_hash>`. The new badge
SHALL be included in the next daily Merkle anchor.

#### Scenario: NCCA Mathematics syllabus change detected

- **GIVEN** the NCCA Mathematics syllabus PDF URL changes
  (Firecrawl monitor detects a diff)
- **WHEN** the `curriculum_change_sensor` fires
- **THEN** the BIEP v3 5-phase re-run completes for Mathematics
- **AND** the new quest pack differs from the prior quest pack
- **AND** a new `SkillTreeBadge` is issued with
  `framework="ncca-lc"`, `subject="mathematics"`, and
  `version=<new_pdf_hash>`
- **AND** the next daily Merkle anchor (02:00 UTC) includes the
  new badge