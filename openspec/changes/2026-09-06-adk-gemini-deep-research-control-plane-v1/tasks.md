# Tasks: tuatha mirror

## Stage 0
- [ ] T0.1 — Confirm parent change is archived (deferred — out of scope; parent repo `cianfhoghlaim` is not writable from this session)

## Stage 1 — Spec delta
- [x] T1.1 — Write `openspec/specs/adk-deep-research-control-plane/spec.md`
- [x] T1.2 — Write the change's spec delta (`openspec/changes/2026-09-06-adk-gemini-deep-research-control-plane-v1/specs/adk-deep-research-control-plane/spec.md`)

## Stage 2 — DLT + BAML
- [x] T2.1 — Copy `dlt_sources/_shared/gemini_deep_research.py` → mirrored at `tuatha/dlt/_shared/gemini_deep_research.py` (path differs because tuatha keeps its DLT sources under `tuatha/dlt/`; the file is a byte-identical mirror of the parent's `dlt_sources/_shared/gemini_deep_research.py`)
- [x] T2.2 — Copy `baml_src/_shared/gemini_deep_research.baml` → mirrored at `tuatha/baml/gemini_deep_research.baml` (already committed in `329c7fa6` as part of the ANAM capture pipeline port)

## Stage 3 — Validation
- [x] T3.1 — Run `openspec validate --strict` → `Change '2026-09-06-adk-gemini-deep-research-control-plane-v1' is valid`
