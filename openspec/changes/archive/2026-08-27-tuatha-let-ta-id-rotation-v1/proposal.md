# Change: Tuatha Letta Agent ID Rotation v1

## Why

Per the 2026-08-27 KCG rename refactor (Phase 3c in this repo),
all `kcg-` prefixed identifiers were rotated to `cianfhoghlaim-`.
For the standalone `tuatha/` project this affects **two production
surfaces**:

1. **Letta agent IDs** — the 15 canonical Letta memory IDs that
   every per-subject / per-educational / per-hackathon agent
   carries. Pre-rename: `kcg-<subject>-agent`. Post-rename:
   `cianfhoghlaim-<subject>-agent`.
2. **Badge credential prefixes** — the `badge_id` emitted by
   `tuatha/tools/mathematics_response_score.py` is the canonical
   Math formative-response credential ID. Pre-rename:
   `kcg-mathematics-<item_id>-<grade>`. Post-rename:
   `cianfhoghlaim-mathematics-<item_id>-<grade>`.

The rotation is a **breaking change** for any persisted state:

- Any Letta memory blocks stored against the old
  `kcg-<subject>-agent` IDs are orphaned — they remain in the
  Letta server but the new `tuatha` build will not see them.
- Any `SkillTreeBadge` already minted with a `kcg-mathematics-...`
  `badge_id` is still cryptographically valid (the badge
  content is hashed, not the ID), but downstream consumers
  (the daily Merkle anchor, the public credential verifier)
  need to be aware of the new prefix going forward.

This change formalises the rotation, the migration plan, and
the archival timeline.

## What changes

### Layer 1 — Letta agent ID rotation (already shipped in this branch)

- **MODIFIED** `tuatha/config.py` — `agent_id_pattern` rotated
  from `kcg-{subject}-agent` → `cianfhoghlaim-{subject}-agent`;
  the LiteLLM fallback also rotated; a `# 2026-08-27 KCG rename`
  comment added at the top of the docstring.
- **MODIFIED** `tuatha/routing.py` — all 15 `letta_agent_id`
  string literals rotated (8 NCCA subjects + 3 educational + 4
  hackathon).
- **MODIFIED** `tuatha/subjects/<subject>.py` — 8 files (one per
  NCCA subject); the `letta_agent_id` string literal rotated.
- **MODIFIED** `tuatha/agents/educational/<agent>.py` — 3 files
  (academic_history + celtic_grammar + celtic_morphology); the
  `letta_agent_id` string literal rotated.
- **MODIFIED** `tuatha/agents/hackathon/<feature>.py` — 4 files
  (adaptive_tutor + curriculum_change_sensor + equivalency_generator
  + marking_grader); the `letta_agent_id` string literal rotated.

### Layer 2 — Badge credential prefix rotation (already shipped)

- **MODIFIED** `tuatha/tools/mathematics_response_score.py` —
  the `badge_id` f-string rotated from `kcg-mathematics-...` →
  `cianfhoghlaim-mathematics-...`.

### Layer 3 — Test assertion rotation (already shipped)

- **MODIFIED** `tuatha/tests/test_routing.py` — the
  `test_each_wire_has_letta_agent_id` docstring + the
  `startswith("kcg-")` assertion rotated to the new prefix.

### Layer 4 — Letta state migration (NEW work — tracked below)

- **NEW** One Letta server admin task that creates 15 new
  `cianfhoghlaim-<subject>-agent` records under the new IDs.
- **NEW** (Optional) Letta memory-block export-then-import job
  that copies any persisted blocks from `kcg-<subject>-agent`
  → `cianfhoghlaim-<subject>-agent` (best-effort — Letta's
  export format is JSON Lines via the `agents.list` + memory
  block dump API; the import is `agents.upsert` with the new
  IDs).
- **NEW** Operator checklist: after 1 release cycle (~14 days),
  archive the 15 old `kcg-<subject>-agent` records so they
  don't accumulate in the Letta admin panel.

### Layer 5 — Badge credential re-issuance (NEW work — tracked below)

- **NEW** A backfill BAML job that re-issues any
  `SkillTreeBadge` minted under the `kcg-mathematics-...`
  prefix to the new `cianfhoghlaim-mathematics-...` prefix.
  The backfill is idempotent: the new badge carries the same
  `evidence_hash` (which is what the Merkle anchor binds), so
  re-issuing does NOT create duplicate Merkle leaves.
- **NEW** Operator checklist: publish a notice in the daily
  Merkle anchor dashboard that badge IDs minted between
  `2026-01-01` and `2026-08-27` carry the old prefix and have
  been re-anchored under the new prefix.

## Out of scope

- The Letta **server URL** (`letta.cianfhoghlaim.ie:8283`) is
  unchanged — only the agent IDs rotate.
- The Letta **memory block schema** is unchanged — only the
  parent agent ID rotates.
- The `tuatha/old/` legacy directory is unchanged (legacy
  `kcg-` references are preserved by design per the 2026-08-25
  consolidation change).

## Dependencies

- **Blocked by (soft)**: the 2026-08-27 KCG rename refactor
  (Phase 3c in this repo, branch `2026-08-27-kcg-rename-v1`).
  The 26 file rewrites are committed as part of that branch;
  this openspec change tracks the *follow-up* Letta-state +
  badge-credential migration that must happen on the operator
  side after the code ships.

- **Mirrors**: `2026-08-27-cianfhoghlaim-let-ta-id-rotation-v1`
  in the `cianfhoghlaim` monorepo (the upstream sister-repo
  change). The two changes must be deployed together to avoid
  drift between the standalone `tuatha` build and the parent
  monorepo's Letta registry.

## Impact

Affected production state (2 surfaces):

| Surface | Pre-rename | Post-rename | Migration effort |
|:--|:--|:--|:--|
| 15 Letta agent records | `kcg-<subject>-agent` | `cianfhoghlaim-<subject>-agent` | 1 admin task + optional block copy |
| ~N `SkillTreeBadge` credentials (Math only, post-0.8 grade) | `kcg-mathematics-<item>-<grade>` | `cianfhoghlaim-mathematics-<item>-<grade>` | 1 BAML backfill job + Merkle re-anchor notice |

Affected code (already shipped in this branch):

- 1 config file + 1 routing file + 8 subject files + 3
  educational agent files + 4 hackathon agent files + 1 tool
  file + 1 test file = **19 MODIFIED** (rotated).

## Quality gates

- [ ] G1: `openspec validate 2026-08-27-tuatha-let-ta-id-rotation-v1 --strict` PASS
- [ ] G2: `ruff check tuatha/` all checks passed
- [ ] G3: `python3 -c "from tuatha.routing import SUBJECT_WIRING_REGISTRY; assert all(w.letta_agent_id.startswith('cianfhoghlaim-') for w in SUBJECT_WIRING_REGISTRY.values())"` OK
- [ ] G4: `python3 -m pytest tuatha/tests/test_routing.py -k letta_agent_id` PASS
- [ ] G5: Letta server admin shows 15 new `cianfhoghlaim-<subject>-agent` records
- [ ] G6: Daily Merkle anchor dashboard shows badge ID prefix = `cianfhoghlaim-`