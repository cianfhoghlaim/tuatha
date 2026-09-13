# Mirror: tuatha ADK + Gemini Deep Research

Per the parent openspec change
`2026-09-06-adk-gemini-deep-research-control-plane-v1`. Adds
cross-jurisdiction Deep Research to the 14-subject formative
assessment surface.

## Requirements

### Requirement: Per-jurisdiction Deep Research queries
The `dlt_sources/_shared/gemini_deep_research.py` mirror SHALL
accept queries keyed by the 5 safeguarding bodies + 9 jurisdictions
(Ireland, England, NI, Scotland, Wales, IoM, Jersey, Guernsey, NCCE).

#### Scenario: Cross-jurisdiction comparison
- **WHEN** a query like `"Compare the Junior Cycle Mathematics syllabus in Ireland, Wales, and Northern Ireland"` is submitted
- **THEN** the DLT source MUST yield one row per jurisdiction
- **AND** each row MUST be tagged with `jurisdiction` and `safeguarding_body`

### Requirement: Evidence ladder rung-3 integration
The Gemini Deep Research `interactions` field MUST be treated as
rung-3 evidence in the 5-rung evidence ladder. Each `interaction`
adds one `baml_function` entry with `prompt_version` + `confidence`.

#### Scenario: Rung-3 evidence row
- **WHEN** a Deep Research invocation completes
- **THEN** each `interaction` MUST produce one rung-3 evidence row
- **AND** the rung-5 Merkle root MUST include the interaction hash
