# Change: Tuatha Multi-Model 2D Graphics + 2.5D Hades-Orthographic Renderer + Educational Earn Pipeline v1

## Why

The Tuatha British Isles Formative Assessment MMO sub-project
(`/Users/cianmacandeisigh/dev/tuatha/`) currently ships:

- A single-model 2D asset pipeline (FIBO only) at
  `tuatha/asset_generation/fibo/`
- The TanStack Start 2D client (text + 2D diagrams only, no
  orthographic 2.5D)
- A partial `SkillTreeBadge` + `AchievementToken` + `CredAnchor`
  surface (the contracts exist, the daily Merkle E2E flow is
  unwired, and the revocation list is missing)

The user's 3 directives (per session 2026-08-26):

1. **Multi-model graphics, not FIBO-only** — wire all 7
   image-gen models (`local/image/{flux2-dev, z-image-turbo,
   qwen-image, fibo, sdxl, diffusiongemma-26b-a4b,
   qwen-image-2512}`) and all 3 VLM analysis models (`molmo2-8b`,
   `qwen3-vl-8b-instruct`, `olmOCR-2-7B-1025`) via Unsloth Studio
   (`unsloth.cianfhoghlaim.ie:8889`) — every call resolves through
   `MODEL_REGISTRY.resolve(family, role)`, zero hardcoded model
   strings.
2. **2D + 2.5D Hades-orthographic, NO 3D** — PixiJS v8 +
   pixi-viewport orthographic camera + layered parallax +
   pixi-particle + pixi-sound. Per-subject realm scene with the
   8 NCCA subjects as the "realms". NO Babylon.js, NO SpacetimeDB,
   NO Rust crates (the 2026-10-06 clean-break ADR stays).
3. **Educational earn + proof-of-learning** — soulbound
   `AchievementToken` (ERC20-shaped, transfers revert) +
   off-chain `SkillTreeBadge` (Convex + FalkorDB + LanceDB) +
   daily Merkle anchor on Base L2 + revocation list for
   academic-misconduct flow.

This change is the **single mega-change** that delivers all 8
prompts (P1–P8) identified in the historic-context research
session. The change validates `openspec validate --strict`
before any code is written.

## What changes

### Layer 1 — Multi-model 2D + 2.5D asset pipeline (P1)

- **NEW** `tuatha/asset_generation/image_gen/` — the multi-model
  router that resolves `MODEL_REGISTRY.resolve("image_gen", role)`
  for each of the 7 image-gen entries (5 local + 2 Unsloth)
- **EXTEND** `tuatha/asset_generation/fibo/` — keep FIBO as the
  canonical 2D diagram generator for syllabus LO diagrams
- **NEW** `tuatha/asset_generation/vlm/` — the VLM analysis layer
  routing `MODEL_REGISTRY.resolve("ocr_vision", role)` for
  `molmo2-8b` (diagram pointing), `qwen3-vl-8b-instruct` (page
  images), `olmOCR-2-7B-1025` (AllenAI specialist)
- **MODIFY** BAML `ExtractSyllabusDiagram` to take a real `image`
  parameter (resolving the 2026-08-12 caveat that detection was
  textual-only) — the BAML client routes through Unsloth Studio
- **MODIFY** `tuatha/asset_generation/invoke.py` to expose the
  new 3-layer facade (image_gen / fibo / vlm) preserving the
  existing 5 FIBO functions
- **NEW** `tuatha/asset_generation/unsloth_client.py` — the
  OpenAI-compatible Unsloth Studio HTTP client (no new env vars;
  uses the existing `UNSLOTH_API_KEY` from the model_registry
  schema)

### Layer 2 — PixiJS 2.5D Hades-orthographic client (P3)

- **NEW** `tuatha/web/packages/realm-canvas/` — the PixiJS v8
  renderer package:
  - `src/index.ts` — the `TuathaRealmCanvas` class (WebGL +
    WebGPU backend, layered parallax, orthographic camera)
  - `src/viewport.ts` — pixi-viewport integration with 2.5D tilt
  - `src/particles.ts` — pixi-particle system (Fibonacci spirals,
    reaction sparks, wind, time-sand, clóscríobh, circuit traces)
  - `src/audio.ts` — pixi-sound integration (Web Audio reactive)
  - `src/subjects/` — the 8 per-subject realm palettes + sprite
    banks (mathematics / applied_mathematics / chemistry /
    geography / history / english / gaeilge / computer_science)
- **NEW** `tuatha/web/apps/tuatha-ui/src/routes/realm/<subject>.tsx`
  — the per-subject realm page (Convex quest query +
  LanceDB diagram join + PixiJS canvas + CopilotKit AG-UI chat)
- **MODIFY** `tuatha/web/apps/tuatha-ui/src/router.tsx` — register
  the 8 new realm routes + the PixiJS canvas mount point
- **MODIFY** `tuatha/web/apps/tuatha-ui/package.json` — add
  `pixi.js@^8`, `pixi-viewport@^6`, `pixi-particle@^5`,
  `pixi-sound@^4`

### Layer 3 — Cross-subject mastery dashboard + FIBO emblems (P4)

- **NEW** `tuatha/web/apps/tuatha-ui/src/routes/student/<id>/mastery.tsx`
  — the 2D radar chart + per-student FIBO emblem renderer
- **NEW** `tuatha/web/packages/mastery-chart/` — the radar chart
  component (Recharts + D3 hybrid, 8-axis spider)
- **MODIFY** `tuatha/web/apps/tuatha-ui/src/lib/emblem.ts` — the
  emblem cache (Convex `files` table, keyed by
  `top_subject + student_id + seed`)
- **MODIFY** Convex `convex/emblem.ts` (NEW) — the emblem upload
  + retrieval functions

### Layer 4 — Soulbound `AchievementToken` end-to-end (P2)

- **MODIFY** `tuatha/badges/ledger.py::issue_badge()` — wire the
  full E2E flow (badge row → FalkorDB edges → daily Merkle batch)
- **NEW** `tuatha/dagster/anchor_assets.py` — the `daily_credential_anchor`
  Dagster asset (02:00 UTC, computes Merkle root, calls
  `CredAnchor.publish(root, batchId)` on Base L2)
- **MODIFY** `tuatha/badges/anchor_contract.py` — the Base L2
  `CredAnchor.sol` Python binding (existing scaffold)
- **MODIFY** `tuatha/badges/achievement_token_client.py` — the
  `AchievementToken.sol` Python binding
- **MODIFY** `tuatha/badges/storage.py` — persist the
  `on_chain_anchor` tx_hash back into each badge row

### Layer 5 — Public Merkle anchor verification (P5)

- **NEW** `tuatha/web/apps/tuatha-ui/src/routes/anchor/<date>.tsx`
  — the public verification route
- **NEW** `tuatha/web/apps/tuatha-ui/src/lib/merkle_verify.ts` —
  the Merkle path recompute (server-side, in Convex function)
- **MODIFY** Convex `convex/anchor.ts` (NEW) — the public anchor
  query function
- **NEW** `tuatha/notebooks/38_merkle_verifier.py` — marimo
  notebook for off-chain verification demo

### Layer 6 — `AchievementToken` revocation list (P8)

- **NEW** `tuatha/contracts/RevocationList.sol` — companion contract
  (idempotent revocation keyed by `evidenceHash`, batched into the
  daily Merkle root exclusion list)
- **MODIFY** `tuatha/contracts/AchievementToken.sol` — extend the
  base contract with `_isRevoked(bytes32 evidenceHash)` modifier on
  `balanceOf`
- **MODIFY** `tuatha/badges/ledger.py` — add the
  `revoke_badge(badge_id, reason)` flow (Convex + on-chain +
  daily Merkle batch picks it up)
- **NEW** `tuatha/docs/REVOCATION_POLICY.md` — the 24h propagation
  guarantee policy doc

### Layer 7 — 8-subject ADK fleet routing + Langfuse (P7)

- **MODIFY** `tuatha/routing.py` — extend the 8-bucket
  `ROUTING_KEYWORDS` map with the canonical dispatch (math / appm
  / chem / geog / hist / engl / gael / comp)
- **MODIFY** `tuatha/subjects/<subject>.py` — verify each subject
  agent exposes ≥5 tools (the canonical 5: syllabus_lookup /
  past_paper_lookup / marking_scheme_lookup / formative_item_generate
  / response_score)
- **NEW** `tuatha/observability/langfuse_traces.py` — the
  `agent.<subject>.extract` Langfuse decorator that wraps every
  BAML call

### Layer 8 — Curriculum change detection sensor (P6)

- **MODIFY** `tuatha/agents/hackathon/curriculum_change_sensor.py`
  — wire the Firecrawl monitors over NCCA + AQA + SQA + WJEC +
  CCEA + IoM (6 jurisdiction sites) → BIEP v3 5-phase re-run →
  diff against the prior quest pack → new `SkillTreeBadge` with
  `version=<new_pdf_hash>` → re-anchor

## Out of scope

- ❌ Babylon.js 3D (retired 2026-10-06, NOT reversed)
- ❌ SpacetimeDB v2 (Rust crates archived 2026-10-06)
- ❌ Pent-Elemental Cosmology / Crypteolas financial token /
  Anam Cara / Brown Ajah theming (HARD-ARCHIVED)
- ❌ The Celtic MMO design (which elements, what boons, the
  4+1 element binding) — deferred to a downstream theming change
- ❌ The 3D roadmap ADR — explicitly skipped per user Q5 =5
- ❌ iOS delivery vehicle — deferred
- ❌ The 60-subject agent surface per `per-subject-agents` spec —
  deferred

## Dependencies

```markdown
## Dependencies

`Blocked by: none`

`Blocked by (soft): 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`
(every model string MUST route through MODEL_REGISTRY; every
BAML function MUST codegen to Pydantic + Zod + Convex + DuckLake
DDL — already enforced)

`Blocked by (soft): 2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1`
(the Unsloth Studio endpoint at unsloth.cianfhoghlaim.ie:8889 +
the `UNSLOTH_API_KEY` env var + the `litellm_alias="local/unsloth/..."`
pattern — already wired)

`Blocked by (soft): 2026-08-25-tuatha-british-isles-mmo-consolidation-v1`
(the consolidated `/Users/cianmacandeisigh/dev/tuatha/` sub-project —
already shipped)

`Blocked by (soft): 2026-08-21-biiep-hackathon-agentic-educational-system-v1`
(the 4 BIEP hackathon features + the 13-agent ADK fleet — already
shipped)

`Affected repos: tuatha (single repo)`
```

## Impact

Affected specs (4 MODIFIED + 0 NEW):

| Spec | Action | ADDED / MODIFIED Requirements |
|:--|:--|:--|
| `cianfhoghlaim-educational-mmo` | **MODIFIED** | 1 MODIFIED Requirement (2.5D Hades-orthographic rendering + multi-model asset pipeline) + 4 ADDED Requirements (mastery dashboard, anchor verification, 8-subject ADK routing, curriculum change sensor) |
| `celtic-asset-generation` | **MODIFIED** | 1 MODIFIED Requirement (the FIBO-only description → multi-model) + 1 ADDED Requirement (VLM analysis via Unsloth Studio) |
| `learn-to-earn-token-credential` | **MODIFIED** | 1 ADDED Requirement (E2E AchievementToken flow + revocation list) |
| `tuatha-british-isles-mmo` | **MODIFIED** | 1 MODIFIED Requirement (the 2D-only theming → 2D + 2.5D) + 1 ADDED Requirement (multi-model asset pipeline) |

Affected code (executed in this change):

- `tuatha/asset_generation/image_gen/` (NEW)
- `tuatha/asset_generation/vlm/` (NEW)
- `tuatha/asset_generation/unsloth_client.py` (NEW)
- `tuatha/web/packages/realm-canvas/` (NEW — PixiJS v8 renderer)
- `tuatha/web/packages/mastery-chart/` (NEW — radar chart)
- `tuatha/web/apps/tuatha-ui/src/routes/realm/<subject>.tsx` (NEW × 8)
- `tuatha/web/apps/tuatha-ui/src/routes/student/<id>/mastery.tsx` (NEW)
- `tuatha/web/apps/tuatha-ui/src/routes/anchor/<date>.tsx` (NEW)
- `tuatha/dagster/anchor_assets.py` (NEW)
- `tuatha/notebooks/38_merkle_verifier.py` (NEW)
- `tuatha/contracts/RevocationList.sol` (NEW)
- `tuatha/docs/REVOCATION_POLICY.md` (NEW)
- `tuatha/observability/langfuse_traces.py` (NEW)
- `tuatha/convex/` — 4 NEW Convex functions (emblem, anchor, quest_query, badge_query)
- Modifications to: `tuatha/badges/ledger.py`, `tuatha/badges/storage.py`,
  `tuatha/badges/anchor_contract.py`, `tuatha/badges/achievement_token_client.py`,
  `tuatha/contracts/AchievementToken.sol`, `tuatha/routing.py`,
  `tuatha/asset_generation/invoke.py`, `tuatha/agents/hackathon/curriculum_change_sensor.py`,
  `tuatha/web/apps/tuatha-ui/src/router.tsx`,
  `tuatha/web/apps/tuatha-ui/package.json`

## The 4 internal phases

| Phase | Layers | Prompts | Why this order |
|:--|:--|:--|:--|
| **Phase 0** (preflight) | — | path correction | repo hygiene first |
| **Phase 1** (parallel) | L1, L7 | P1 + P7 | foundation: image-gen + VLM + ADK routing must work first |
| **Phase 2** (parallel) | L2, L3 | P3 + P4 | consume Phase 1 assets in the 2D + 2.5D client |
| **Phase 3** (parallel) | L4, L5, L6 | P2 + P5 + P8 | crypto layer (depends on Phase 1 schema, independent of Phase 2 UI) |
| **Phase 4** (parallel) | L8 | P6 | depends on Phase 3 Merkle anchor for the diff badge issuance |

## The 10 quality gates

```
G1: openspec validate 2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1 --strict   PASS
G2: openspec validate --all --strict                                                          145+/147 (or better)
G3: mise run lint:registry                                                                     0 hardcoded model strings (24 ocr_vision + 7 image_gen wired)
G4: mise run lint:skills all 166 skills pass
G5: mise run lint:drift-docs                                                                   all AGENTS.md number claims valid
G6: ruff check                                                                                 all checks passed
G7: ast.parse                    N/N passed
G8: Python import tuatha.* (no circular import)                                                IMPORTED OK
G9: mise run ml:registry:audit                                                                 all 24 ocr_vision + 7 image_gen entries live on HF Hub
G10: pixi.js v8 smoke test on /realm/mathematics + /student/<id>/mastery + /anchor/<date>      3/3 routes render
```

## Cross-references

- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` — the canonical spec the new tuatha implements
- `openspec/specs/celtic-asset-generation/spec.md` — the asset pipeline spec (FIBO 2D educational diagram generation)
- `openspec/specs/learn-to-earn-token-credential/spec.md` — the AchievementToken spec
- `openspec/specs/tuatha-british-isles-mmo/spec.md` — the canonical British Isles MMO spec
- `openspec/specs/centralized-model-registry/spec.md` — the 52-entry MODEL_REGISTRY
- `openspec/changes/2026-08-25-tuatha-british-isles-mmo-consolidation-v1/` — the consolidation change
- `openspec/changes/2026-08-21-biiep-hackathon-agentic-educational-system-v1/` — the 4 BIEP hackathon features
- `tuatha/CONSOLIDATION_PLAN.md` — the high-level consolidation plan
- `tuatha/BUILD_PLAN.md` — the per-step execution plan
- `../../AGENTS.md` — the platform root
- `../../../AGENTS.md` — the monorepo root
- `../../../meaisinfhoghlaim/models/README.md` — the model registry docs