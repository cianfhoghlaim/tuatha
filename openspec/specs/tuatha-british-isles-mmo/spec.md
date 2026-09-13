# tuatha-british-isles-mmo Specification

## Purpose

`tuatha-british-isles-mmo` is the standalone implementation
target for the British Isles Formative Assessment MMO. The
canonical GitHub repo is `github.com/cianfhoghlaim/tuatha`
(a sibling sub-app of the Cianfhoghlaim main repo). The
capability implements the canonical
`cianfhoghlaim-educational-mmo` spec for the standalone
deployment context.

## Background

The British Isles Formative Assessment MMO is the
educational platform for the NCCA Leaving Certificate
(Republic of Ireland) + the 7 sister jurisdictions (AQA,
OCR, Pearson, SQA, WJEC, CCEA, Isle of Man Education). The
canonical spec (`cianfhoghlaim-educational-mmo`) covers the
8 NCCA subjects; the standalone `tuatha/` repo implements
those 8 + the 6 NCCA-adjacent subjects (accounting, biology,
business, french, irish T2, physics) per the
`2026-08-26-tuatha-subject-expansion-to-14-v1` change.

The standalone deployment differs from the main
Cianfhoghlaim deployment in three ways:
1. It is independently deployable (no parent monorepo
   dependency at runtime — it consumes the TIER 1 packages
   via `depends_on_tier_1` in `subapp_manifest.yaml`)
2. It is paced per-openspec-change (the main Cianfhoghlaim
   platform is daily)
3. It uses a per-app `mise.toml` + `pyproject.toml` +
   `LICENSE` + `AGENTS.md` — no parent-monorepo coupling

## Requirements

### Requirement: 14-subject coverage (8 NCCA + 6 adjacent)

The standalone `tuatha/` SHALL cover exactly **14** subjects:
the 8 NCCA Leaving Certificate subjects (Mathematics +
Applied Mathematics + Chemistry + Geography + History +
English + Gaeilge + Computer Science) + the 6 NCCA-adjacent
subjects (Accounting + Biology + Business + French + Irish T2
+ Physics).

#### Scenario: Each subject has a complete per-subject stack

- **GIVEN** the post-expansion `tuatha/` repo
- **WHEN** the agent verifies the subject coverage
- **THEN** each of the 14 subjects SHALL have:
  - 1 `tuatha/subjects/<subject>.py` ADK LlmAgent
  - 5 `tuatha/tools/<subject>_<tool>.py` per-subject tools
  - 1 `tuatha/baml/qpack_<subject>.baml` BAML contract
  - 1 `tuatha/dlt/{syllabus,past_paper,marking_scheme,formative_item,response_score}/<subject>.py` DLT source
  - 1 `tuatha/web/apps/tuatha-ui/src/routes/realm/<subject>.tsx` PixiJS realm route
  - 1 `tuatha/web/packages/realm-canvas/src/subjects/<subject>.ts` sprite bank

### Requirement: Single MMO client

The standalone `tuatha/` SHALL ship a single MMO client
(PixiJS v8 2.5D Hades-orthographic renderer at
`tuatha/web/packages/realm-canvas/`) with the canonical
TanStack Start 2D surface at `tuatha/web/apps/tuatha-ui/`.

#### Scenario: The PixiJS canvas mounts on every /realm/<subject> route

- **GIVEN** the post-expansion `tuatha/` repo
- **WHEN** the agent navigates to `/realm/<subject>` for any
  of the 14 subjects
- **THEN** the page SHALL render the `RealmPage` component
  with the per-subject sprite bank + the Convex quest query
  + the CopilotKit AG-UI chat panel

### Requirement: Per-subject SUBJECT_WIRING_REGISTRY entries

Every subject SHALL be registered in
`tuatha/routing.py:SUBJECT_WIRING_REGISTRY` with the
canonical 8-field `SubjectAgentWiring` (ncca_subject /
module_slug / display_name / baml_prefix /
langfuse_trace_name / cognee_dataset / letta_agent_id /
litellm_routing_key).

#### Scenario: The 14-subject registry dispatches all 14 buckets

- **GIVEN** the post-expansion `tuatha/routing.py`
- **WHEN** the agent invokes `route_message()` with a
  keyword from any of the 14 `ROUTING_KEYWORDS` buckets
  (math / appm / chem / geog / hist / engl / gael / comp +
  acct / biol / bus / fren / iris / phys)
- **THEN** the dispatch SHALL return the correct module_slug
- **AND** `route_message_to_wire()` SHALL return the
  canonical `SubjectAgentWiring` for the matching subject

### Requirement: Independent deployable sibling subapp

The standalone `tuatha/` SHALL be deployable as an
independent TIER 3 subapp per the
`web-frontend-3-tier` architecture. The
`subapp_manifest.yaml` at the repo root declares the
`depends_on_tier_1` packages (model-registry, fleet,
theming, agui-bridge, observability, dlt-common, auth,
baml-helpers, ui-kit) + the pace_layer
(per_openspec_change) + the deployment_target (parent).

#### Scenario: The subapp_manifest.yaml is valid

- **GIVEN** the post-expansion `tuatha/` repo
- **WHEN** the parent's `sync_subapps.py` reads
  `tuatha/subapp_manifest.yaml`
- **THEN** the parser SHALL validate the manifest against
  the canonical `subapp_manifest.template.yaml` schema
- **AND** the manifest SHALL list all 9 TIER 1 packages
  in `depends_on_tier_1`

### Requirement: 8 NCCA Leaving Certificate subject agents

The system SHALL provide end-to-end per-subject agents for the
8 NCCA Leaving Certificate subjects: mathematics,
applied_mathematics, chemistry, geography, history, english,
gaeilge, computer_science. Each subject SHALL have a
`<subject>_agent.py` ADK agent in the new `tuatha/subjects/`
directory + 5 per-subject tools (syllabus_lookup +
past_paper_lookup + marking_scheme_lookup +
formative_item_generate + response_score) in the new
`tuatha/tools/` directory.

#### Scenario: A student asks the Mathematics agent a syllabus question

- **GIVEN** the user is authenticated in the new `tuatha/`
  project
- **AND** the `tuatha/subjects/mathematics.py` agent is
  available via the `tuatha.agents.media_intel.media_descriptor_agent`
  re-routing (or directly)
- **WHEN** the user asks "what is the NCCA LC Mathematics Higher
  Level syllabus on complex numbers"
- **THEN** the agent calls the `tuatha/tools/mathematics_syllabus_lookup`
  tool
- **AND** returns the BAML-extracted syllabus topic with the
  `ncca_code` + `excerpt_en` + `source_page` from the
  `qpack_mathematics.baml` extractor
- **AND** the response carries a citation linking back to the
  `leaving_certificate/mathematics/en/SCSEC25_Maths_syllabus_examination-2015_English.pdf`
  PDF (the canonical NCCA Mathematics syllabus)

### Requirement: 3 educational agents

The system SHALL provide 3 educational agents under
`tuatha/agents/educational/`:

1. `academic_history_agent` — the cross-archive academic history
   (research paper retrieval + citation extraction)
2. `celtic_grammar_agent` — the Celtic grammar specialist
   (Irish + Welsh + Scottish Gaelic + Breton + Cornish + Manx)
3. `celtic_morphology_agent` — the Celtic morphology
   specialist (verb conjugation + noun declension +
   adjective agreement)

#### Scenario: A Gaeilge teacher asks the Celtic grammar agent about dialectical forms

- **GIVEN** the user is authenticated in the new `tuatha/`
  project
- **WHEN** the user asks "what is the difference between the
  Connacht and Ulster dialectical forms of the verb 'bí'"
- **THEN** the `celtic_grammar_agent` routes to the
  `qpack_gaeilge.baml` extractor's grammar sub-function
- **AND** returns the 2 dialectical forms side-by-side with the
  relevant excerpts from the CELT corpus

### Requirement: 4 BIEP hackathon features
The system SHALL provide 4 BIEP hackathon features under
`tuatha/agents/hackathon/` (per the
`2026-08-21-biiep-hackathon-agentic-educational-system-v1/`):

1. `marking_grader` — the Adaptive Marking Grader
2. `adaptive_tutor` — the Adaptive Tutor Chat
3. `equivalency_generator` — the Cross-Jurisdiction Equivalency Generator
4. `curriculum_change_sensor` — the Curriculum Change Detection Sensor

#### Scenario: A teacher uses the Adaptive Marking Grader

- **GIVEN** the teacher uploads a student's PDF answer + the
  official NCCA marking scheme
- **WHEN** the `marking_grader` workflow runs
- **THEN** the `tuatha/baml/marking_grader.baml` extractor
  matches the answer against the marking scheme
- **AND** returns a grade + personalised feedback in plain English

### Requirement: 1 media_intel pipeline

The system SHALL provide the media_intel pipeline (moved from
`agents/meaisinfhoghlaim/media_intel/`) under
`tuatha/agents/media_intel/`. The 10-tool ADK
`media_descriptor_agent` orchestrates the 5 per-medium BAML
extractor functions (comic / prose / animation / gameplay /
official_document) + the 5 corpus introspection tools
(list_sources / list_descriptors_by_class / summarise_corpus /
compare_class_consistency / search_descriptors).

#### Scenario: A research user asks the media_descriptor_agent for cross-medium consistency

- **GIVEN** the media_intel corpus has 100+ rows per class
- **WHEN** the user calls `compare_class_consistency("fire")`
- **THEN** the agent returns the per-medium cosine similarity
  scores + the consistency score (inverse of variance)
- **AND** the response identifies the most consistently
  described source class for the `fire` element

### Requirement: The British Isles Formative Assessment MMO theme

The system SHALL adopt the British Isles Formative Assessment MMO
theme per the canonical `cianfhoghlaim-educational-mmo` spec.
The 8 NCCA Leaving Certificate subjects are the canonical
content surface.

**The 3 deprecated themes are HARD-ARCHIVED** (per the
`CONSOLIDATION_PLAN.md`):
- ~~Pent-Elemental Cosmology~~ (5 realms)
- ~~Babylon.js 3D~~ game front-end
- ~~SpacetimeDB v2~~ game engine backend
- ~~Crypteolas financial token~~
- ~~Anam Cara soul friend mechanic~~
- ~~Brown Ajah theming~~

The technological choices that ARE preserved:
- The 8 NCCA subject agents (in `tuatha/subjects/`)
- The 40 subject-specific tools (in `tuatha/tools/`)
- The 12-agent fleet pattern (root_agent + curriculum_agent + ...)
- The 3 educational agents (in `tuatha/agents/educational/`)
- The 4 BIEP hackathon features (in `tuatha/agents/hackathon/`)
- The media_intel pipeline (in `tuatha/agents/media_intel/`)
- The BAML extraction + DLT + Dagster + CocoIndex + marimo
  pipeline stack
- The Hono + Convex + TanStack Start + CopilotKit web stack
- The LiteLLM + Cognee + Graphiti + LanceDB + Letta memory stack
- The educational-credential badge system (the `badges/` subdir;
  the previous `crypteolas/` financial-token system is archived)

#### Scenario: A user opens the new `tuatha/` project for the first time

- **WHEN** the user runs `tuatha --version`
- **THEN** the project reports version `0.1.0` (the initial
  build) + the British Isles Formative Assessment MMO theme
  description
- **AND** the project does NOT contain the 3 deprecated themes
  (verified by `tuatha --audit`)
- **AND** the project references the `leabharlann` + `bonneagar`
  sibling repos via the standard cross-repo sync contract

## Out of scope

- The 8 NCCA + 6 adjacent expansion is the ONLY spec
  extension this file owns. The 8 NCCA subjects continue
  to be governed by the canonical
  `cianfhoghlaim-educational-mmo` spec in the main repo.
- The on-chain AchievementToken credential is governed by
  the `learn-to-earn-token-credential` spec (cross-repo
  reference; mirrored in `tuatha/openspec/specs/`).
- The 2D + 2.5D asset pipeline is governed by the
  `celtic-asset-generation` spec (cross-repo reference).

## See also

- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` —
  the canonical spec the standalone tuatha implements
- `openspec/specs/celtic-asset-generation/spec.md` — the
  asset pipeline spec (FIBO + Unsloth Studio image gen)
- `openspec/specs/learn-to-earn-token-credential/spec.md`
  — the on-chain credential spec
- `openspec/changes/2026-08-26-tuatha-subject-expansion-to-14-v1/`
  — the openspec change that authored this spec
- `../../subapp_manifest.yaml` — the TIER 3 subapp
  declaration
