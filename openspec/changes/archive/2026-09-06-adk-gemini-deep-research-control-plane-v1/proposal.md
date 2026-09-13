# Change: ADK + Gemini Deep Research Mirror (tuatha)

## Why

This is the tuatha-side mirror of the parent change
`2026-09-06-adk-gemini-deep-research-control-plane-v1` in
`cianfhoghlaim/openspec/changes/`. Tuatha is the British Isles
Formative Assessment MMO with 14 NCCA subjects × 5 safeguarding
bodies. The `gemini_deep_research` tool is the natural fit for
the **media-intel pipeline** (10-tool ADK agent) and the
**curriculum_change_sensor** (Dagster sensor watching NCCA + AQA +
SQA + WJEC + CCEA + IoM).

## What changes

- **DLT source mirror**: copy `dlt_sources/_shared/gemini_deep_research.py`
  from the parent.
- **BAML schema mirror**: copy `baml_src/_shared/gemini_deep_research.baml`
  from the parent.
- **Evidence ladder integration**: extend the 5-rung evidence
  chain in `tuatha/badges/` to include Gemini Deep Research output
  (the per-step `interactions` field becomes rung-3 evidence).

## Out of scope

- Merkle badge minting changes (deferred — needs Foundry test coverage).

## Dependencies

```markdown
## Dependencies

`Blocked by: cianfhoghlaim/openspec/changes/2026-09-06-adk-gemini-deep-research-control-plane-v1`

`Affected repos: tuatha`
```
