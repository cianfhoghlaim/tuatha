# Spec Delta: tuatha-british-isles-mmo

## Purpose

`tuatha-british-isles-mmo` is the canonical capability for the
**Tuatha** project — the British Isles Formative Assessment MMO.
The implementation lives at the new top-level `tuatha/` dir
at `/Users/cianmacandeisigh/dev/tuatha/`
(the independent GitHub repo at `github.com/cianfhoghlaim/tuatha`).

The capability is the implementation surface for the
`openspec/specs/cianfhoghlaim-educational-mmo/spec.md` spec.
The Tuatha project implements the British Isles Formative
Assessment MMO theming (the 8 NCCA Leaving Certificate subjects
+ the 3 educational agents + the 4 BIEP hackathon features + the
1 media_intel pipeline).

This capability was created by the
`2026-08-25-tuatha-british-isles-mmo-consolidation-v1` change,
which consolidates the prior scattered `agents/tuatha/` state +
the prior top-level `tuatha/` skeleton + the
`agents/meaisinfhoghlaim/media_intel/` module into the new
single coherent Tuatha project.

## ADDED Requirements

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
3. `celtic_morphology_agent` — the Celtic morphology specialist
   (verb conjugation + noun declension + adjective agreement)

### Requirement: 4 BIEP hackathon features

The system SHALL provide 4 BIEP hackathon features under
`tuatha/agents/hackathon/` (per the
`2026-08-21-biiep-hackathon-agentic-educational-system-v1/`):

1. `marking_grader` — the Adaptive Marking Grader
2. `adaptive_tutor` — the Adaptive Tutor Chat
3. `equivalency_generator` — the Cross-Jurisdiction Equivalency
4. `curriculum_change_sensor` — the Curriculum Change Detection Sensor

### Requirement: 1 media_intel pipeline

The system SHALL provide the media_intel pipeline (moved from
`agents/meaisinfhoghlaim/media_intel/`) under
`tuatha/agents/media_intel/`. The 10-tool ADK
`media_descriptor_agent` orchestrates the 5 per-medium BAML
extractor functions (comic / prose / animation / gameplay /
official_document) + the 5 corpus introspection tools
(list_sources / list_descriptors_by_class / summarise_corpus /
compare_class_consistency / search_descriptors).

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
