# Change: Tuatha ANAM Capture Pipeline Port + 3-Corpus Expansion (Hades Boons + X-Men Powers + Avatar Elemental Bending) + Educational Prompt Rewrite v1

## Why

The `tuatha/` canonical sub-project (the British Isles Formative
Assessment MMO) is missing the **ANAM capture pipeline** that
was fully wired in `tuatha-clean/` before the
`2026-08-25-tuatha-british-isles-mmo-consolidation-v1`
consolidation stripped it out. The pipeline extracts graphics
from 3 corpora — **Hades boons** (game), **X-Men powers**
(animation), and **Avatar elemental bending** (animation) —
converts them to typed descriptions via a VLM (qwen3-vl-8b for
games, molmo2-8b for animation), and maps them to a Celtic-deity
particle palette for the 2.5D client.

Additionally:

1. The 14 NCCA + adjacent subject agents + 3 educational
   agents + 4 BIEP hackathon agents all use **trivial BAML
   prompts** (the 4-line "You are the X specialist. Generate
   the canonical response." stub). They produce no useful
   output because they carry no rubric reference, no LO
   numbering, no bilingual EN+GA invariant (except gaeilge),
   no difficulty calibration, and no jurisdiction routing.
2. The evaluation surface is RAGAS-only with 1 check
   (`ragas_anam_color_anchor`). The user wants to pivot to
   **Google ADK observation evals** (`TrajectoryEvaluator`)
   which can score the *trajectory* the agent takes (the right
   BAML function, the right embedder, the right cross-source
   join) — not just the final output.
3. Two VLMs need to be promoted to the **centralized model
   registry** as usage roles: `hades_boon` and `xmen_scene`.
4. The Swift capture daemon in
   `tuatha-clean/tuatha/capture/macos/` is a Phase-1 stub with
   critical drift between the README and code (every-frame
   JPEG writer, not the "1fps + on-change burst HEVC" the
   README advertises). We drop it in favour of a Hermes Agent
   computer-use stub for the Phase-2 capture path.

## What changes

### Layer 0 — Preflight bugfixes (Phase 0)

- **FIX** silent-coercion bug in
  `tuatha/subjects/<subject>.py` (14 files) +
  `tuatha/agents/hackathon/{marking_grader,adaptive_tutor,equivalency_generator,curriculum_change_sensor}.py`
  — the `LiteLlmConfig.resolve_model` 2-arg signature silently
  coerces unknown roles to `default`. Use the canonical
  `resolve_model("text_llm", "subject_agent")` pattern.
- **STANDARDIZE** the 6-jurisdiction list to
  `{NCCA, AQA, SQA, WJEC, CCEA, IoM}` across all hackathon
  agent descriptions, `curriculum_change_sensor.py`, and new
  BAML enums.
- **ADD** English-only language guard to every BAML function
  prompt + every ADK agent instruction (gaeilge exempt; it
  keeps bilingual EN + GA per the AGENTS.md invariant).
- **DROP** the Swift capture daemon path; write
  `tuatha/capture/macos/DEPRECATED.md` documenting the
  drift + the deprecation rationale.
- **NEW** `tuatha/capture/hermes_client.py` — Hermes Agent
  computer-use HTTP client stub (Phase-2 placeholder).

### Layer 1 — ANAM capture pipeline port from tuatha-clean

- **PORT** `tuatha/baml/anam_capture.baml` (344 LOC) from
  `tuatha-clean/tuatha/baml/anam_capture.baml` — defines
  `HadesBoon`, `ComicParticleFrame`, `GbaMagicSystem`,
  `AnamParticle` classes + 11 enums (`GodName`, `BoonTier`,
  `CelticDeity`, `BiasMode`, etc.) + 7 BAML functions
  (`ExtractHadesBoon`, `ExtractComicParticle`,
  `ExtractGbaMagic`, `MapToAnamParticle`,
  `ExtractCrossLinguisticAnamDescription`) + 4 clients
  (`HadesBoonClient`, `ComicParticleClient`, `GbaMagicClient`,
  `AnamMapClient` reading `env.LLAMASWAP_URL` /
  `env.LITELLM_URL`) + 3 test cases.
- **PORT** 4 CocoIndex v1 Apps from
  `tuatha-clean/tuatha/cocoindex/anam/{hades_boons,
  comic_particles, gba_magic, anam_particles}.py` — the
  apps write the 4 Lance tables
  `cianfhoghlaim.tuatha.{hades.boons, comic.particles,
  gba.magic, anam.particles}`.
- **PORT** `tuatha/dagster/anam.py` (407 LOC) from
  `tuatha-clean/tuatha/dagster/anam.py` — the 4 asset
  groups (`tuatha_capture` / `tuatha_embed` / `tuatha_join` /
  `tuatha_quality`) + the `@asset_check
  ragas_anam_color_anchor` (ΔE CIE76 ≤ 8, score ≥ 0.85).
- **PORT** `tuatha/dagster/anam_observability.py` (127 LOC)
  from `tuatha-clean/tuatha/dagster/anam_observability.py` —
  the Langfuse v3 SDK fix + MLflow logger + structlog setup
  + RAGAS metric envelope.
- **PORT** 3 source manifests
  `tuatha/sources/anam/{hades,comic,gba}/source.yaml` from
  `tuatha-clean/tuatha/sources/anam/`.
- **PORT** `tuatha/models/registry.py` (188 LOC) from
  `tuatha-clean/tuatha/models/registry.py` — the 7-role
  `ModelRole` dataclass + `ROLES` dict + `resolve()` +
  `vision_env()`.
- **PORT** `tuatha/tools/corpus_tools.py` (258 LOC) +
  `tuatha/corpus/{__init__.py, client.py, CONTRACT.md}`
  (~200 LOC) from `tuatha-clean/` — the corpus binding
  helper that closes over the subject.
- **REFACTOR** `tuatha/subjects/<subject>.py` (14 files) to
  use `bind_subject_tools(<subject>)` instead of the 5 stub
  tools per subject pattern.
- **DELETE** the 40 `tuatha/tools/<subject>_<tool>.py` stub
  modules (5 stubs × 8 NCCA subjects, but 6 for gaeilge's
  extra `gael_gramadach_review` tool).
- **PORT** `tuatha/tests/test_anam_pipeline.py` (336 LOC)
  from `tuatha-clean/tests/` — namespace ownership +
  shippable invariant + CocoIndex App registration tests.
- **PORT** 5 marimo notebooks
  `tuatha/notebooks/anam/{anam_dashboard,cross_subject,
  hackathon,media_intel,per_subject}.py` from
  `tuatha-clean/tuatha/notebooks/anam/`.

### Layer 2 — X-Men: Evolution corpus (NEW — 3rd ANAM source)

- **NEW** `tuatha/sources/anam/xmen_evolution/source.yaml` —
  source manifest for the X-Men: Evolution (2000-2003,
  Marvel Animation) animation corpus. `display_name:
  "X-Men: Evolution (2000-2003, Marvel Animation / ABC Kids'
  WB)"`, `rights_holder: "Marvel Animation / Disney+"`,
  `vision_model: ${VISION_MODEL_XMEN}`, `baml_function:
  ExtractXmenScene`, `shippable: false`, plus
  `legal_notes`.
- **NEW** `tuatha/baml/anam_xmen.baml` — defines
  `XmenScene`, `XmenPowerUsage`, `XmenCharacter` classes +
  3 enums (`XmenPowerClass { Alpha, Beta, Omega, Unknown }`,
  `XmenTeam { XMen, Brotherhood, XFactor, Independents,
  Humans, Unknown }`, `XmenParticleMotion`) + the
  `ExtractXmenScene(image: image)` BAML function with the
  full 30+ character roster (Cyclops, Jean Grey, Wolverine,
  Storm, Rogue, Beast, Shadowcat, Nightcrawler, Spyke,
  Mystique, Toad, Avalanche, Blob, Pyro, Magneto,
  Sabretooth, Multiple Man, Polaris, Wolfsbane, Forge,
  Professor X, Gambit, Scarlet Witch cameo, Quicksilver
  cameo) + 3 test cases (`xmen_cyclops_optic_blast`,
  `xmen_storm_weather_control`, `xmen_jean_grey_telepathy`).
  VLM default = `molmo2-8b` (the animation specialist,
  multi-image reasoning + diagram pointing + grounding).
- **NEW** `tuatha/cocoindex/anam/xmen_scenes.py` — CocoIndex
  v1 App watching
  `s3://cianfhoghlaim-tuatha-raw/xmen/<episode>/{keyframes}/`,
  downsampling to 1024px JPEG, calling
  `b.ExtractXmenScene(image=thumb)`, BGE-M3 embedding,
  appending to the Lance table
  `cianfhoghlaim.tuatha.xmen.scenes`.
- **UPDATE** `tuatha/cocoindex/anam/anam_particles.py` —
  add `cianfhoghlaim.tuatha.xmen.scenes` to the source
  tables list (now 4 sources: hades + comic + gba + xmen)
  + add `bias_mode="balanced"` for xmen.scenes.
- **UPDATE** `tuatha/dagster/anam.py` — add 2 new assets:
  `xmen_raw_scenes` (group `tuatha_capture`) +
  `xmen_scenes_embedded` (group `tuatha_embed`).
- **UPDATE** `tuatha/agents/media_intel/media_descriptor_agent.py` —
  add the 6th extractor tool `extract_xmen_descriptor_tool`
  (Class F animation) + register it in the `TOOLS` list +
  update the agent instruction to name Class F.
- **UPDATE** `tuatha/baml/media_descriptor.baml` — add the
  `ExtractXmenDescriptor` BAML function + the
  `XmenDescriptor` class (extends `MediaDescriptor` with
  `character_name`, `character_team`, `power_class`,
  `ability_name`).
- **NEW** `tuatha/notebooks/anam/tabs/xmen_scenes.py` —
  marimo notebook tab showing side-by-side Source colour
  vs ANAM colour + Celtic-deity mapping for X-Men powers
  (parallel to the existing `boons.py` tab).
- **NEW** `tuatha/tests/test_xmen_extraction.py` — tests
  the `ExtractXmenScene` BAML schema + the Lance table
  namespace + the shippable invariant + the cross-source
  join with the ANAM Celtic-deity mapping.

### Layer 3 — Educational assessment prompt rewrite

- **REWRITE** `tuatha/baml/marking_grader.baml` — adds
  the `RubricBand` (HL1-HL8 + OL1-OL8 grade bands) +
  `MarkingCriterion` (criterion_id, lo_code, marks,
  band_description) + `GradingResult` (with per_criterion
  breakdown + flagged_for_review + confidence) classes +
  the `MarkGrade` function with a 4-step
  CITE → BAND → SUMMARISE → FEEDBACK loop.
- **REWRITE** `tuatha/baml/adaptive_tutor.baml` — adds the
  `TutorState` (mastery EMA + blocked_lo + recent_attempts)
  + `TutorAction` (6 action types: explain_concept /
  give_example / drill_problem / review_past_paper /
  summarise / switch_jurisdiction) + the `Adapttutor`
  function with a 5-step CLASSIFY → DIAGNOSE → ADAPT →
  GENERATE → CITE loop.
- **REWRITE** `tuatha/baml/equivalency_generator.baml` —
  adds the `EquivalencyRow` + `EquivalencyTable` (with
  `gaps` + `notes_en` + `notes_ga` + `confidence`) classes
  + the `Equivgen` function with a 3-step ALIGN →
  CLASSIFY → FLAG-GAPS loop.
- **REWRITE** 14 `tuatha/baml/qpack_<subject>.baml` files
  (math + appm + chem + geog + hist + engl + gael + comp +
  accounting + biology + business + french + irish +
  physics) — the `Generate<Subject>Syllabus` +
  `Generate<Subject>FormativeItem` +
  `Score<Subject>FormativeResponse` functions all get the
  same canonical prompt template with: NCCA LO numbering
  scheme (e.g. `LC-MATHS-LO-<strand>.<index>`) + bilingual
  invariant (gaeilge only) + difficulty 1-5 calibration +
  evidence_pdfs citation + English-only default.
- **REWRITE** 8 NCCA subject ADK agent instructions in
  `tuatha/subjects/<subject>.py` — adds the Tool decision
  matrix (when to use each of the 5 tools) + the Evidence
  Ladder G7 contract (no response without provenance) +
  the bilingual invariant (gaeilge only) + the difficulty
  calibration guide + the NCCA LO numbering reference +
  the English-only default.

### Layer 4 — Google ADK observation eval surface

- **NEW** `tuatha/dagster/observation/__init__.py` — the
  observation eval package re-exporting the
  `TrajectoryEvaluator` subclasses + the `AgentEvaluator`
  runner + the Dagster `@asset_check` wrappers.
- **NEW** `tuatha/dagster/observation/eval_runner.py` —
  wraps `google.adk.evaluation.AgentEvaluator.run_eval(...)`
  with a graceful-degradation fallback (the no-op
  `@wraps(func)` decorator pattern when `google-adk` not
  installed).
- **NEW** `tuatha/dagster/observation/eval_metrics.py` —
  the 7 `TrajectoryEvaluator` subclasses
  (`AnamColorAnchorTrajectoryEvaluator` /
  `MarkingAccuracyTrajectoryEvaluator` /
  `FeedbackQualityTrajectoryEvaluator` /
  `FormativeItemUniquenessTrajectoryEvaluator` /
  `AdaptiveTutorRelevanceTrajectoryEvaluator` /
  `EquivalencyConsistencyTrajectoryEvaluator` /
  `SyllabusCoverageTrajectoryEvaluator`).
- **NEW** `tuatha/dagster/observation/eval_sets/anam.yaml`
  — 3 eval cases (1 per ANAM source: hades_boons,
  xmen_powers, avatar_elemental_bending), each with
  `ground_truth` for the colour anchor + Celtic-deity map
  + max_delta_e threshold.
- **NEW** `tuatha/dagster/observation/eval_sets/marking.yaml`
  — 5 eval cases for the marking grader (one per NCCA
  subject band: HL1, HL3, HL5, OL3, OL7).
- **NEW** `tuatha/dagster/observation/eval_sets/tutor.yaml`
  — 5 eval cases for the adaptive tutor (one per state
  transition: explain_concept / drill_problem / summarise
  / review_past_paper / switch_jurisdiction).
- **NEW** `tuatha/dagster/observation/otel_langfuse_bridge.py`
  — the bridge that sends the ADK OTEL spans to the
  Langfuse backend (`langfuse.cianfhoghlaim.ie`) so the
  eval trajectories appear in the Langfuse UI.
- **DELETE** the 8 RAGAS asset check stubs (no longer
  needed; ADK observation eval replaces them).

### Layer 5 — Centralized model registry

- **MODIFY** `meaisinfhoghlaim/models/model_registry.py` —
  add 2 new `ModelRegistryEntry` entries:
  `qwen3-vl-8b-hades-boon` (family=`ocr_vision`,
  role=`hades_boon`, default=`unsloth/Qwen3-VL-8B-Instruct-GGUF`)
  + `qwen3-vl-8b-xmen-scene` (family=`ocr_vision`,
  role=`xmen_scene`, default=`unsloth/Qwen3-VL-8B-Instruct-GGUF`).
- **MODIFY** `tuatha/tuatha/baml/clients.baml` — add the
  `hades_boon` client + the `xmen_scene` client + the
  `HadesBoonClient` + `XmenSceneClient` (mirrors
  `tuatha-clean/tuatha/baml/anam_capture.baml`).

## Out of scope

- The 2.5D PixiJS client + the FIBO diagram generator +
  the AchievementToken E2E flow + the Merkle anchor — all
  covered by the in-flight
  `2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1`
  change.
- The Swift capture daemon — dropped in favour of the
  Hermes Agent computer-use Phase-2 path.
- The remaining 5 `tuatha.models.registry.ROLES` promotions
  (`comic_particle`, `gba_magic`, `subject_agent`,
  `educational_agent`, `hackathon_agent`, `anam_map`) —
  deferred to a fast-follow change.

## Dependencies

- **Blocked by** (soft):
  - `2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`
    (every model string MUST route through `MODEL_REGISTRY`)
  - `2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1`
    (the Unsloth Studio endpoint at
    `unsloth.cianfhoghlaim.ie:8889` + the Hermes Agent
    computer-use stub)
  - `2026-08-25-tuatha-british-isles-mmo-consolidation-v1`
    (the consolidated `/Users/cianmacandeisigh/dev/tuatha/`
    sub-project — already shipped)
  - `2026-08-21-biiep-hackathon-agentic-educational-system-v1`
    (the 4 BIEP hackathon features + the 13-agent ADK
    fleet)
  - `2026-08-26-tuatha-subject-expansion-to-14-v1` (the 14
    subject agents)

- **Affects**: tuatha (single repo) + the parent
  `cianfhoghlaim/meaisinfhoghlaim/models/model_registry.py`
  (the 2 usage role entries).

- **Affected specs** (4 MODIFIED + 0 NEW):
  - `openspec/specs/cianfhoghlaim-educational-mmo/spec.md`
    (MODIFIED: add 2 Requirements — ANAM capture pipeline;
    educational observation eval coverage)
  - `openspec/specs/tuatha-british-isles-mmo/spec.md`
    (MODIFIED: add 1 Requirement — 3-corpus ANAM
    extraction with Celtic-deity mapping)
  - `openspec/specs/celtic-asset-generation/spec.md`
    (MODIFIED: add 1 Requirement — 3-source ANAM
    cross-source join with ΔE CIE76 ≤ 8 colour anchor)
  - `openspec/specs/centralized-model-registry/spec.md`
    (MODIFIED: add 1 Requirement — usage roles
    (`hades_boon`, `xmen_scene`) with env_var + why
    field)

## Impact

- **17 new files** + **72 updated files** + **48 deleted
  files** (the 40 stub tools + 8 RAGAS asset checks).
- **0 breaking changes** — every consumer routes through
  `MODEL_REGISTRY.resolve(family, role)` per the
  centralized-registry invariant.
- **No copyright violations** — the `shippable: false`
  invariant is preserved (the descriptor is
  description-only; the original panel / frame / screenshot
  is never stored in the shippable asset output).
- **English-only default** per the AGENTS.md invariant;
  gaeilge subject keeps bilingual EN+GA per the AGENTS.md
  "BILINGUAL EN/GA" invariant.

## 4 execution phases

### Phase 0 — Preflight bugfixes (~20 file changes)

- T0.1: Fix silent-coercion bug in 18 agent files
- T0.2: Standardize 6-jurisdiction list
- T0.3: Add English-only language guard
- T0.4: Drop Swift daemon path
- T0.5: Add Hermes Agent computer-use stub

### Phase 1 — ANAM port + X-Men addition (~75 file changes)

- T1.1–T1.9: Port 5 BAML files + 4 CocoIndex Apps + 3
  Dagster asset files + 3 source manifests + models
  registry + corpus tools + 8 subject agent refactors +
  tests + marimo notebooks (from tuatha-clean)
- T1.10–T1.18: Add 9 new files for X-Men: Evolution
  (source manifest + BAML schema + CocoIndex App +
  Dagster assets + media descriptor extraction +
  notebook tab + tests)

### Phase 2 — Educational prompt rewrite (~24 file changes)

- T2.1–T2.5: Rewrite 4 BAML files (marking_grader +
  adaptive_tutor + equivalency_generator + 14× qpack_<subject>)
  + 8 NCCA subject ADK agent instructions

### Phase 3 — ADK observation eval surface (~10 file changes)

- T3.1–T3.6: Implement the observation package + the 7
  TrajectoryEvaluator subclasses + the 3 eval sets + the
  OTEL-Langfuse bridge + delete the 8 RAGAS stubs

### Phase 4 — Centralized registry + verification (~3 file changes + 5 gates)

- T4.1: Add `hades_boon` + `xmen_scene` to
  `meaisinfhoghlaim/models/model_registry.py`
- T4.2–T4.5: `mise run lint:registry` +
  `mise run ml:registry:audit` + `mise run lint:skills` +
  `openspec validate --all --strict` + `uv run pytest`

## Quality gates (G1–G13)

- G1: `openspec validate --strict` passes
- G2: `openspec validate --all --strict` passes
- G3: `mise run lint:registry` returns 0 hardcoded model
  strings
- G4: `mise run lint:skills` returns 166+ skills pass
- G5: `mise run lint:drift-docs` returns all number claims
  valid
- G6: `ruff check` passes
- G7: `ast.parse` returns N/N passed
- G8: Python import returns no circular import
- G9: `mise run ml:registry:audit` returns all 24
  ocr_vision + 7 image_gen entries live on HF Hub
- G10: PixiJS v8 smoke test 3/3 routes render (out of
  scope; this change does not touch PixiJS)
- G11: `baml-cli test` for `ExtractHadesBoon`,
  `ExtractXmenScene`, `MarkGrade`, `Adapttutor`, `Equivgen`,
  all 14 `Generate<Subject>*` functions
- G12: 7 ADK `TrajectoryEvaluator` asset checks pass
  thresholds (ΔE CIE76 ≤ 8 for ANAM colour anchor,
  criterion citation accuracy ≥ 0.7 for marking grader,
  etc.)
- G13: `subject_router_smoke` 14/14 subjects route
  correctly

## Cross-references

- `openspec/specs/tuatha-british-isles-mmo/spec.md` — the
  parent MMO spec
- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` —
  the parent educational MMO spec
- `openspec/specs/celtic-asset-generation/spec.md` — the
  Celtic asset generation spec
- `openspec/specs/centralized-model-registry/spec.md` —
  the centralized model registry spec
- `tuatha-clean/tuatha/baml/anam_capture.baml` — the
  source of the Hades boon extractor BAML schema
- `tuatha-clean/tuatha/cocoindex/anam/hades_boons.py` —
  the source of the Hades CocoIndex App
- `tuatha-clean/tuatha/dagster/anam.py` — the source of
  the ANAM Dagster asset graph
- `meaisinfhoghlaim/meaisinfhoghlaim/evaluation/ragas_metrics.py`
  — the current RAGAS-only evaluation surface (to be
  partially replaced by ADK observation eval)
- `tuatha/tuatha/observability/langfuse_traces.py` — the
  Langfuse v3 OTEL decorator (to be extended with the
  ADK OTEL-Langfuse bridge)
