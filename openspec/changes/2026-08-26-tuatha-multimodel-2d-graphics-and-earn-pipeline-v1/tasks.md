# Tasks — Tuatha Multi-Model 2D Graphics + 2.5D Hades-Orthographic Renderer + Educational Earn Pipeline v1

## Phase 0 — Preflight (1 step)

- [x] T0.1: Update the stale `kings_college_galway/tuatha/` path references in `tuatha/AGENTS.md` + `tuatha/CONSOLIDATION_PLAN.md` + `tuatha/DEVELOPMENT.md` + `tuatha/tuatha/__init__.py` + `tuatha/openspec/changes/2026-08-25-tuatha-british-isles-mmo-consolidation-v1/{proposal.md,specs/tuatha-british-isles-mmo/spec.md}` to the canonical `/Users/cianmacandeisigh/dev/tuatha/` path.

## Phase 1 — Multi-model asset pipeline + ADK fleet routing (parallel)

### P1 — Multi-model 2D + 2.5D asset pipeline via Unsloth Studio

- [ ] T1.1: Create `tuatha/asset_generation/image_gen/__init__.py` + `tuatha/asset_generation/image_gen/router.py` — the multi-model router that resolves `MODEL_REGISTRY.resolve("image_gen", role)` for each of the 7 image-gen entries (5 local + 2 Unsloth). The router exposes `generate_diagram(prompt, role="default", seed=None, **kwargs)`.
- [ ] T1.2: Create `tuatha/asset_generation/vlm/__init__.py` + `tuatha/asset_generation/vlm/router.py` — the VLM analysis layer routing `MODEL_REGISTRY.resolve("ocr_vision", role)` for `molmo2-8b` (diagram pointing), `qwen3-vl-8b-instruct` (page images), `olmOCR-2-7B-1025` (AllenAI specialist). Exposes `analyse_page_image(image, role="diagram_pointing", **kwargs)`.
- [ ] T1.3: Create `tuatha/asset_generation/unsloth_client.py` — the OpenAI-compatible Unsloth Studio HTTP client (uses `UNSLOTH_API_KEY` from the model_registry schema). The client routes `image_gen` requests to `/v1/images/generations` and `ocr_vision` requests to `/v1/chat/completions` on `unsloth.cianfhoghlaim.ie:8889`.
- [ ] T1.4: Extend `tuatha/asset_generation/fibo/education_fibo.py` to add the 5 NEW subject prompt templates (applied_mathematics + geography + history + english + computer_science) — the existing 3 (mathematics + chemistry + gaeilge) stay. Total: 8 NCCA subjects.
- [ ] T1.5: Modify `tuatha/asset_generation/invoke.py` to expose the new 3-layer facade (image_gen / fibo / vlm) preserving the existing 5 FIBO functions.
- [ ] T1.6: Modify the BAML `ExtractSyllabusDiagram` function in `tuatha/baml/qpack_<subject>.baml` (8 subject files) to take a real `image` parameter (resolving the 2026-08-12 caveat that detection was textual-only) — the BAML client routes through Unsloth Studio.
- [ ] T1.7: Add tests in `tuatha/tests/test_image_gen_router.py` + `tuatha/tests/test_vlm_router.py` — verify the router resolves every role correctly, verify the Unsloth client retries on 5xx, verify the mock Unsloth endpoint works for offline dev.

### P7 — 8-subject ADK fleet routing + Langfuse

- [ ] T7.1: Modify `tuatha/routing.py` to extend the 8-bucket `ROUTING_KEYWORDS` map (math / appm / chem / geog / hist / engl / gael / comp) and verify the `root_agent` dispatch.
- [ ] T7.2: Verify each subject agent in `tuatha/subjects/<subject>.py` exposes ≥5 tools (the canonical 5: syllabus_lookup / past_paper_lookup / marking_scheme_lookup / formative_item_generate / response_score).
- [ ] T7.3: Create `tuatha/observability/langfuse_traces.py` — the `agent.<subject>.extract` Langfuse decorator that wraps every BAML call. Exposes `@trace_agent(subject)` decorator.
- [ ] T7.4: Wire the Langfuse decorator into each subject agent's BAML call sites (8 files).
- [ ] T7.5: Add tests in `tuatha/tests/test_routing.py` + `tuatha/tests/test_langfuse_traces.py`.

## Phase 2 — 2.5D Hades-orthographic client + mastery dashboard (parallel)

### P3 — Subject realm page with embedded diagrams + 2.5D background

- [ ] T3.1: Create `tuatha/web/packages/realm-canvas/package.json` + `tuatha/web/packages/realm-canvas/tsconfig.json` — the PixiJS v8 renderer package.
- [ ] T3.2: Create `tuatha/web/packages/realm-canvas/src/index.ts` — the `TuathaRealmCanvas` class (WebGL + WebGPU backend, layered parallax, orthographic camera).
- [ ] T3.3: Create `tuatha/web/packages/realm-canvas/src/viewport.ts` — pixi-viewport integration with 2.5D tilt.
- [ ] T3.4: Create `tuatha/web/packages/realm-canvas/src/particles.ts` — pixi-particle system (Fibonacci spirals, reaction sparks, wind, time-sand, clóscríobh, circuit traces).
- [ ] T3.5: Create `tuatha/web/packages/realm-canvas/src/audio.ts` — pixi-sound integration (Web Audio reactive).
- [ ] T3.6: Create `tuatha/web/packages/realm-canvas/src/subjects/{mathematics,applied_mathematics,chemistry,geography,history,english,gaeilge,computer_science}.ts` — the 8 per-subject realm palettes + sprite banks.
- [ ] T3.7: Create `tuatha/web/apps/tuatha-ui/src/routes/realm/<subject>.tsx` (8 files) — the per-subject realm page (Convex quest query + LanceDB diagram join + PixiJS canvas + CopilotKit AG-UI chat).
- [ ] T3.8: Modify `tuatha/web/apps/tuatha-ui/src/router.tsx` — register the 8 new realm routes + the PixiJS canvas mount point.
- [ ] T3.9: Modify `tuatha/web/apps/tuatha-ui/package.json` — add `pixi.js@^8`, `pixi-viewport@^6`, `pixi-particle@^5`, `pixi-sound@^4`.
- [ ] T3.10: Add a PixiJS smoke test in `tuatha/web/apps/tuatha-ui/tests/realm_canvas.test.ts`.

### P4 — Cross-subject mastery dashboard with FIBO-rendered emblems

- [ ] T4.1: Create `tuatha/web/packages/mastery-chart/package.json` + `tuatha/web/packages/mastery-chart/tsconfig.json` — the radar chart component (Recharts + D3 hybrid, 8-axis spider).
- [ ] T4.2: Create `tuatha/web/packages/mastery-chart/src/index.tsx` — the 8-axis spider chart.
- [ ] T4.3: Create `tuatha/web/apps/tuatha-ui/src/routes/student/<id>/mastery.tsx` — the dashboard route.
- [ ] T4.4: Modify `tuatha/web/apps/tuatha-ui/src/lib/emblem.ts` — the emblem cache (Convex `files` table, keyed by `top_subject + student_id + seed`).
- [ ] T4.5: Create `tuatha/web/apps/tuatha-ui/convex/emblem.ts` — the emblem upload + retrieval functions.
- [ ] T4.6: Add tests in `tuatha/web/apps/tuatha-ui/tests/mastery_dashboard.test.tsx`.

## Phase 3 — Crypto layer (parallel)

### P2 — Soulbound `AchievementToken` end-to-end

- [ ] T2.1: Modify `tuatha/badges/ledger.py::issue_badge()` — wire the full E2E flow (badge row → FalkorDB edges → daily Merkle batch).
- [ ] T2.2: Create `tuatha/dagster/anchor_assets.py` — the `daily_credential_anchor` Dagster asset (02:00 UTC, computes Merkle root, calls `CredAnchor.publish(root, batchId)` on Base L2).
- [ ] T2.3: Modify `tuatha/badges/anchor_contract.py` — the Base L2 `CredAnchor.sol` Python binding.
- [ ] T2.4: Modify `tuatha/badges/achievement_token_client.py` — the `AchievementToken.sol` Python binding.
- [ ] T2.5: Modify `tuatha/badges/storage.py` — persist the `on_chain_anchor` tx_hash back into each badge row.
- [ ] T2.6: Add tests in `tuatha/tests/test_achievement_token_e2e.py`.

### P5 — Public Merkle anchor verification

- [ ] T5.1: Create `tuatha/web/apps/tuatha-ui/src/routes/anchor/<date>.tsx` — the public verification route.
- [ ] T5.2: Create `tuatha/web/apps/tuatha-ui/src/lib/merkle_verify.ts` — the Merkle path recompute (server-side, in Convex function).
- [ ] T5.3: Create `tuatha/web/apps/tuatha-ui/convex/anchor.ts` — the public anchor query function.
- [ ] T5.4: Create `tuatha/notebooks/38_merkle_verifier.py` — marimo notebook for off-chain verification demo.
- [ ] T5.5: Add tests in `tuatha/web/apps/tuatha-ui/tests/anchor_verify.test.tsx`.

### P8 — `AchievementToken` revocation list

- [ ] T8.1: Create `tuatha/contracts/RevocationList.sol` — companion contract (idempotent revocation keyed by `evidenceHash`, batched into the daily Merkle root exclusion list).
- [ ] T8.2: Modify `tuatha/contracts/AchievementToken.sol` — extend the base contract with `_isRevoked(bytes32 evidenceHash)` modifier on `balanceOf`.
- [ ] T8.3: Modify `tuatha/badges/ledger.py` — add the `revoke_badge(badge_id, reason)` flow.
- [ ] T8.4: Create `tuatha/docs/REVOCATION_POLICY.md` — the 24h propagation guarantee policy doc.
- [ ] T8.5: Add Foundry tests in `tuatha/contracts/test/RevocationList.t.sol`.

## Phase 4 — Curriculum change detection sensor

- [ ] T6.1: Modify `tuatha/agents/hackathon/curriculum_change_sensor.py` — wire the Firecrawl monitors over NCCA + AQA + SQA + WJEC + CCEA + IoM (6 jurisdiction sites).
- [ ] T6.2: Wire the BIEP v3 5-phase re-run (BAML re-extract → CocoIndex v1 re-embed → Cognee cognify → Graphiti temporal memory → LanceDB re-index) into the sensor.
- [ ] T6.3: Add the diff against the prior quest pack + new `SkillTreeBadge` with `version=<new_pdf_hash>` + re-anchor.
- [ ] T6.4: Add tests in `tuatha/tests/test_curriculum_change_sensor.py`.

## Quality gates

- [ ] G1: `openspec validate 2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1 --strict` PASS
- [ ] G2: `openspec validate --all --strict` 145+/147 (or better)
- [ ] G3: `mise run lint:registry` 0 hardcoded model strings
- [ ] G4: `mise run lint:skills` all 166 skills pass
- [ ] G5: `mise run lint:drift-docs` all AGENTS.md number claims valid
- [ ] G6: `ruff check` all checks passed
- [ ] G7: `ast.parse` N/N passed
- [ ] G8: Python import `tuatha.*` (no circular import) IMPORTED OK
- [ ] G9: `mise run ml:registry:audit` all 24 ocr_vision + 7 image_gen entries live on HF Hub
- [ ] G10: PixiJS v8 smoke test on `/realm/mathematics` + `/student/<id>/mastery` + `/anchor/<date>` 3/3 routes render

## Final

- [ ] Final: `openspec archive 2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1 --yes` after deploy