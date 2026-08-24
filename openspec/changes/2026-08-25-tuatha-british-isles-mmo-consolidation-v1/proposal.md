# Change: Tuatha British Isles MMO Consolidation v1

## Why

The Cianfhoghlaim monorepo (`/Users/cianmacandeisigh/dev/kings_college_galway/`)
previously carried the British Isles Formative Assessment MMO in
3 scattered locations that were NOT interconnected:

1. **`agents/tuatha/`** — 61 files (8 subject agents + 40 subject-
   specific tools + 5 support files + 4 doc files + 1 partial-
   refactor `agents/` subdir)
2. **The prior top-level `tuatha/` skeleton** — 8 dirs + 1 file + 1
   README + 1 random `resto_druid_wow_macros.txt` (now archived to
   `tuatha/old/prior_top_level_tuasha/`)
3. **`agents/meaisinfhoghlaim/media_intel/`** — the 10-tool media
   descriptor agent (now moved to `tuatha/agents/media_intel/`)

The canonical openspec spec
`openspec/specs/cianfhoghlaim-educational-mmo/spec.md`
(which supersedes the deprecated `tuatha-platform` spec) says:

> *"The historic skills `.agents/skills_backup/tuatha-mmo/` and
> `.agents/skills_backup/tuatha-platform/` are preserved as
> archaeology — they document an earlier Babylon.js 3D + SpacetimeDB
> v2 + Pent-Elemental Cosmology + Crypteolas financial token
> design that did not land. The new build drops those themes
> but keeps the technological choices."*

The change consolidates everything into a **single coherent
independent sub-project** at
`/Users/cianmacandeisigh/dev/kings_college_galway/tuatha/`
(the new top-level `tuatha/` dir; the canonical GitHub repo at
`github.com/cianfhoghlaim/tuatha.git`).

## What changes

### Layer 1 — Archive (the prior state → `tuatha/old/`)

The 3 sub-archives:

- `tuatha/old/prior_top_level_tuasha/` — the 12-item prior
  top-level skeleton
- `tuatha/old/scattered_agents_tuasha/` — the 63-file scattered
  state from `agents/tuasha/`
- `tuatha/old/legacy_theming/babylonjs/` — the hard-archived
  Babylon.js skill (the only live theming reference at the time)

### Layer 2 — Cross-repo references (the re-routes)

- **`agents/agent_registry.py:AGENT_REGISTRY`** — the
  `media_descriptor_agent` entry's `module_path` is re-routed
  from `agents.meaisinfhoghlaim.media_intel.media_descriptor_agent`
  to `tuatha.agents.media_intel.media_descriptor_agent`
- **`agents/meaisinfhoghlaim/media_intel/`** — the 3 source
  files (`__init__.py` + `media_descriptor_agent.py` +
  `records.py`) were moved to `tuatha/agents/media_intel/`. A
  back-compat shim at the old location re-exports the canonical
  symbols from the new location.
- **`.agents/skills/tuatha/SKILL.md`** — the new canonical
  skill stub that points at the new `github.com/cianfhoghlaim/tuatha.git`
  repo.

### Layer 3 — Build the new `tuatha/` project from scratch

The new project structure (in the new tuatha repo at
`github.com/cianfhoghlaim/tuatha`):

- 9 top-level meta files (CONSOLIDATION_PLAN, BUILD_PLAN,
  README, AGENTS, DEVELOPMENT, pyproject.toml, mise.toml,
  LICENSE, .gitignore)
- 70 Python files in `tuatha/tuatha/` (the 7 orchestrator
  modules + the 8 subject agents + the 40 tools + the 3
  educational agents + the 4 hackathon features + the 5
  media_intel files + their __init__.py re-exports)
- 14 BAML contracts in `tuatha/tuatha/baml/` (the 8 per-subject
  qpack + 3 hackathon + media_descriptor + clients + the
  __init__.py)
- 46 DLT sources in `tuatha/tuatha/dlt/` (5 categories × 8
  subjects + 5 category __init__.py + 1 DLT __init__.py)
- 4 Dagster asset groups in `tuatha/tuatha/dagster/`
  (per_subject + educational + hackathon + __init__.py)
- 5 CocoIndex v1 Apps in `tuatha/tuatha/cocoindex/` (per_subject +
  cross_subject + hackathon + media_intel + __init__.py)
- 5 marimo notebooks in `tuatha/tuatha/notebooks/`
  (per_subject + cross_subject + hackathon + media_intel +
  __init__.py)
- 4 badges modules in `tuatha/tuatha/badges/`
  (models + mint + storage + __init__.py)
- 4 docs at `docs/` (ARCHITECTURE + AGENT_REGISTRY +
  THEMING + BIOGRAPHY)
- 4 tests at `tests/` (test_subject_router_smoke +
  test_media_intel_agent + test_hackathon_features +
  test_consolidation)
- 2 CI files at `.github/workflows/ci.yml` + `tuatha/ci/dagger.py`
- 3 dev-container files at `.devcontainer/`
- 3 BAML client stubs at `tuatha/tuatha/baml/.baml_client/`
  (manually-written since `baml-cli` is not installed)

## Out of scope

- The Celtic MMO design itself — which elements, what boons, the
  4+1 element binding, the sub-nation mapping, the 2D particle
  renderer, the iOS delivery vehicle (the downstream theming
  change gated on the corpus being populated)
- The Pent-Elemental Cosmology + Babylon.js 3D + SpacetimeDB v2 +
  Crypteolas + Anam Cara + Brown Ajah theming (hard-archived
  per the canonical spec)

## Dependencies

The 5 parent pending changes that must archive first:
- `2026-09-01-celtic-mythology-content-system-v1`
- `2026-09-08-ogham-celtic-stones-pipeline-v1`
- `2026-09-22-geospatial-british-isles-twin-v1`
- `2026-09-29-familiar-dynamic-nft-system-v1`
- `2026-10-06-spacetimedb-babylonjs-adr-clean-break-v1`

The 2 soft-blockers:
- `2026-08-21-biiep-hackathon-agentic-educational-system-v1`
  (carries the 4 BIEP hackathon features)
- `2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`

## Impact

- 281 files committed across 3 commits on the new
  `github.com/cianfhoghlaim/tuatha` repo (private, ID 1343953528)
- 1 new git remote (`github.com/cianmacandeisigh/tuatha` —
  user-owned; but the actual created repo is at the org-level
  `github.com/cianfhoghlaim/tuatha` due to the available token's
  permissions)

## The 6 quality gates (all green from the parent repo at the time of the consolidation change)

| Gate | Result |
|:--|:--|
| G1 `openspec validate --strict` | ✅ **PASS** — "Change ... is valid" |
| G2 `openspec validate --all --strict` | 156/159 (3 pre-existing unrelated failures) |
| G3 `mise run lint:registry` | ✅ **0 hardcoded model strings** |
| G4 `ruff check` | 40 fixable style issues (no functional bugs) |
| G5 `ast.parse` (242+ Python files) | ✅ **0 failed** |
| G6 `import check` (10 media_intel tools + 8 subjects + 3 educational + 4 hackathon) | ✅ **PASS** |
