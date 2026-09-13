# Spec Delta: celtic-asset-generation

## MODIFIED Requirements

### Requirement: Multi-model asset pipeline (formerly "Five-stage Celtic asset generation pipeline" — extended)

The `celtic-asset-generation` skill SHALL orchestrate a 5-stage
pipeline for every Celtic language asset, AND SHALL route every
image-gen call through the multi-model asset pipeline at
`tuatha/asset_generation/image_gen/` (resolves
`MODEL_REGISTRY.resolve("image_gen", role)` for each of the 7
image-gen entries: `local/image/{flux2-dev, z-image-turbo,
qwen-image, fibo, sdxl, diffusiongemma-26b-a4b, qwen-image-2512}`).
The pipeline SHALL route Unsloth-served models to
`unsloth.cianfhoghlaim.ie:8889` via the `UnslothClient` at
`tuatha/asset_generation/unsloth_client.py`. The pipeline SHALL
NOT contain any hardcoded model strings.

Each asset (a NCCA specification, an SEC exam paper, a Dúchas
handwriting sample, a Tuatha quest NPC, etc.) flows through the
5 stages:

1. **BAML extraction** — schema-validated LLM extraction
   of typed records (`MarkingPoint`, `LearningOutcome`,
   `CircularMetadata`, `SiteAnalysis`, etc.)
2. **CocoIndex v1 embedding** — incremental embedding with
   `@coco.fn(memo=True)` + BGE-large-en-v1.5 in 100+
   batches
3. **Cognee cognify** — knowledge graph construction with
   8 canonical relationship types
4. **Graphiti temporal memory** — bi-temporal KG
   (Graphiti + FalkorDB)
5. **LanceDB vector** — IVF_HNSW + FTS indexes for
   semantic search

The 5-stage pipeline runs in
`tuatha/asset_generation/{image_gen,fibo,vlm}/` and is exposed
via the FastAPI `tuatha/api/` endpoints.

#### Scenario: A new NCCA specification lands

- **GIVEN** a new NCCA primary mathematics specification
  PDF is uploaded to `stedding/ingest_queue/`
- **WHEN** the `celtic_assets_primary_maths` Dagster asset
  materialises
- **THEN** the DLT source ingests the PDF and the BAML
  extraction calls `ExtractLearningOutcome` (BGE + GLM-4.6
  fallback) to extract typed outcomes
- **AND** the CocoIndex v1 flow embeds each outcome in
  the `cianfhoghlaim.education.ie.primary.maths.outcomes`
  LanceDB table
- **AND** the Cognee cognify call builds the knowledge
  graph nodes
- **AND** the Graphiti episode is appended to the temporal
  KG
- **AND** the marimo dashboard at
  `https://cianfhoghlaim.cianfhoghlaim.ie/dashboards/
  primary-maths` shows the new outcomes
- **AND** every image-gen call routes through
  `MODEL_REGISTRY.resolve("image_gen", role)` (no hardcoded
  model strings)

## ADDED Requirements

### Requirement: VLM backbone via Unsloth Studio

The `celtic-asset-generation` skill SHALL use the **Molmo2** +
**Qwen3-VL** + **olmOCR** vision-language models as the canonical
VLM backbone for document extraction. The VLM backbone SHALL
resolve via `MODEL_REGISTRY.resolve("ocr_vision", role)` and
route through the `UnslothClient` to `unsloth.cianfhoghlaim.ie:8889`.
For on-device Apple Silicon inference, the **Qwen3-VL** family
(MLX-quantised) is the fallback.

The VLM backbone is responsible for:
- **Diagram pointing** (bounding boxes + verbatim text) — `molmo2-8b`
- **Page image analysis** (full-page text + structure) — `qwen3-vl-8b-instruct`
- **AllenAI specialist** (the OCR specialist) — `olmOCR-2-7B-1025`

The 3 canonical VLM papers are kept as long-form references in
the skill at `.agents/skills/celtic-asset-generation/references/`.

#### Scenario: A new document is ingested

- **GIVEN** a new PDF (NCCA, SEC, Dúchas, etc.) needs
  extraction
- **WHEN** the BAML extraction calls
  `ExtractCurriculumSpecification(pdf_text, pdf_images)`
- **THEN** the VLM backbone processes the document via the
  multi-model router:
  - `molmo2-8b` for diagram pointing (transformers backend)
  - `qwen3-vl-8b-instruct` for full-page image analysis
    (Unsloth backend)
  - `olmOCR-2-7B-1025` for OCR specialist (transformers backend)
- **AND** the typed extraction is returned to the BAML client

#### Scenario: FIBO diagram rendered via the multi-model router

- **GIVEN** a Mathematics LO with a `SyllabusDocument` and
  `SyllabusDiagram` records
- **WHEN** `fibo_configs_from_syllabus_diagrams` runs for
  that subject
- **THEN** the FIBO config's `_metadata` carries
  `diagram_id`, `source_pdf`, `page_number`,
  `model_id="local/image/fibo"`, `seed=<int>` — traceable
  back to the real PDF page, not fabricated

### Requirement: Real image parameter on ExtractSyllabusDiagram

The BAML `ExtractSyllabusDiagram` function SHALL take a real
`image: image` parameter (resolving the 2026-08-12 caveat that
detection was textual-only) — the BAML client routes through
Unsloth Studio via the multi-model VLM router. The function
SHALL return bounding boxes + verbatim text + the figure caption
for each detected diagram.

#### Scenario: Bounded diagram detection on a Chemistry page image

- **GIVEN** a Chemistry syllabus PDF page image (PNG bytes)
- **WHEN** `ExtractSyllabusDiagram(image=<page_image>, subject="chemistry")`
  runs
- **THEN** the VLM router resolves `molmo2-8b` via the
  `MODEL_REGISTRY`
- **AND** the returned `SyllabusDiagram` records carry
  `bounding_box`, `verbatim_text`, `figure_caption`,
  `source_pdf`, `page_number`
- **AND** no detection is fabricated (only textually-mentioned
  figures are included)