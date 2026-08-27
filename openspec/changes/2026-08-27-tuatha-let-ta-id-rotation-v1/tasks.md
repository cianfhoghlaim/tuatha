# Tasks — Tuatha Letta Agent ID Rotation v1

## Phase A — Code rotation (already shipped in `2026-08-27-kcg-rename-v1`)

### A.1 — Letta agent ID literals

- [x] T1.1: Rotate `letta_agent_id` in `tuatha/config.py`
  (the `agent_id_pattern` dataclass field + the docstring +
  the LiteLLM fallback stubs + a `# 2026-08-27 KCG rename`
  header comment).
- [x] T1.2: Rotate the 15 `letta_agent_id` literals in
  `tuatha/routing.py` (8 SUBJECT_WIRING_REGISTRY entries +
  3 EDUCATIONAL_WIRING_REGISTRY entries + 4 HACKATHON_WIRING_REGISTRY
  entries).
- [x] T1.3: Rotate the `letta_agent_id` literal in the 8 subject
  agent files under `tuatha/subjects/<subject>.py`.
- [x] T1.4: Rotate the `letta_agent_id` literal in the 3
  educational agent files under
  `tuatha/agents/educational/<agent>.py`.
- [x] T1.5: Rotate the `letta_agent_id` literal in the 4
  hackathon agent files under
  `tuatha/agents/hackathon/<feature>.py`.

### A.2 — Badge credential prefix rotation

- [x] T2.1: Rotate the `badge_id` f-string in
  `tuatha/tools/mathematics_response_score.py` from
  `kcg-mathematics-...` → `cianfhoghlaim-mathematics-...`.

### A.3 — Test assertion rotation

- [x] T3.1: Rotate the docstring + `startswith("kcg-")` assertion
  in `tuatha/tests/test_routing.py:test_each_wire_has_letta_agent_id`.

### A.4 — Path / doc rotation (non-code)

- [x] T4.1: Rotate `kings_college_galway` → `cianfhoghlaim` in
  `CONSOLIDATION_PLAN.md` (4 occurrences).
- [x] T4.2: Rotate `kings_college_galway` → `cianfhoghlaim` in
  `DEVELOPMENT.md` (3 occurrences).

## Phase B — Letta state migration (operator task — NEW)

### B.1 — Spin up the 15 new agents

- [ ] T5.1: Run the Letta admin task that creates the 15 new
  `cianfhoghlaim-<subject>-agent` records against
  `http://letta.cianfhoghlaim.ie:8283`. The agent creation
  payload reuses the `system_prompt` + the 5 tool definitions
  from the old `kcg-<subject>-agent` records (verified via
  `letta.agents.get(kcg-<subject>-agent)` prior to archival).
- [ ] T5.2: Verify the 15 new agent records are queryable via
  `letta.agents.list(filter={"prefix": "cianfhoghlaim-"})`.
  Expected count: 15 (8 NCCA subjects + 3 educational + 4 hackathon).

### B.2 — Migrate persisted memory blocks (best-effort)

- [ ] T6.1: Export the memory blocks from each
  `kcg-<subject>-agent` via `letta.agents.blocks.list(agent_id=...)`.
  Save the JSON Lines dump to
  `tuatha/old/scattered_agents_tuasha/letta_migration_2026-08-27/`.
- [ ] T6.2: Re-import the blocks under the new
  `cianfhoghlaim-<subject>-agent` IDs via
  `letta.agents.blocks.upsert(agent_id=<new>, blocks=...)`.
- [ ] T6.3: Spot-check 3 of the 15 agents — verify a known
  memory block (e.g., the Adaptive Tutor's "current student"
  block) survived the migration.

### B.3 — Archive the old IDs (after 1 release cycle)

- [ ] T7.1: 14 days after the rotation ships, archive the 15
  old `kcg-<subject>-agent` records (set `archived=true` via
  the Letta admin API). Do NOT delete — the Letta admin panel
  surfaces archived records under "Recently archived".
- [ ] T7.2: Update the parent monorepo's Letta registry table
  (`agents/meaisinfhoghlaim/letta_registry.py`) to drop the
  15 `kcg-` entries (the parent ships the canonical list).

## Phase C — Badge credential re-issuance (operator task — NEW)

### C.1 — Inventory the old badges

- [ ] T8.1: Run a Cognee query against the `oideachais_lc_mathematics`
  dataset: `SELECT badge_id FROM skill_tree_badges WHERE badge_id LIKE 'kcg-mathematics-%'`.
  Expected: N records (the cumulative Math formative-response
  badges since the 2026-01-01 launch).
- [ ] T8.2: Save the inventory to
  `tuatha/old/scattered_agents_tuasha/badge_migration_2026-08-27/inventory.json`.

### C.2 — Re-issue under the new prefix

- [ ] T9.1: Run the backfill BAML job (`baml_client.b.ReissueBadge`)
  that takes the old `badge_id` + the original `(item_id, grade,
  evidence_hash)` tuple and emits a new badge under the
  `cianfhoghlaim-mathematics-...` prefix. The new badge MUST
  carry the same `evidence_hash` (the Merkle leaf is
  hash-stable; only the human-readable ID changes).
- [ ] T9.2: Verify the new badge IDs are visible in Cognee.

### C.3 — Daily Merkle anchor notice

- [ ] T10.1: Add a one-line notice to the daily Merkle anchor
  dashboard: "Badge IDs minted between 2026-01-01 and 2026-08-27
  carry the legacy `kcg-` prefix; re-issued under `cianfhoghlaim-`
  prefix on 2026-08-27. See openspec/changes/2026-08-27-tuatha-let-ta-id-rotation-v1/."
- [ ] T10.2: Verify the next daily anchor (2026-08-28) includes
  the re-issued badges as separate Merkle leaves (not as new
  badges — same `evidence_hash`, different `badge_id`).

## Phase D — Documentation + drift checks (operator task — NEW)

### D.1 — Update the public-facing credential verifier

- [ ] T11.1: The public credential verifier at
  `tuatha/web/apps/tuatha-ui/src/routes/credential/[badge_id].tsx`
  must accept both `kcg-` and `cianfhoghlaim-` prefixes during
  the transition window. Add a prefix-rewrite helper that maps
  `kcg-` → `cianfhoghlaim-` for lookup, returning the badge
  regardless of which prefix the URL carries.
- [ ] T11.2: After 90 days (2026-11-25), drop the `kcg-` prefix
  rewrite — only the canonical `cianfhoghlaim-` prefix is
  accepted.

### D.2 — Drift check vs. sister-repo

- [ ] T12.1: Compare this change against the sister change in
  the parent monorepo
  (`cianfhoghlaim/openspec/changes/2026-08-27-cianfhoghlaim-let-ta-id-rotation-v1/`).
  Verify the 15 Letta IDs match; verify the badge prefix matches.
- [ ] T12.2: If drift detected, file a new openspec change
  `2026-09-XX-tuatha-let-ta-id-drift-fix-v1` to reconcile.