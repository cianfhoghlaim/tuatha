# tuatha — the British Isles Formative Assessment MMO

> A **provable, source-anchored** educational MMO for the
> Republic of Ireland (NCCA) and the seven sister jurisdictions
> (England, Scotland, Wales, Northern Ireland, Isle of Man,
> plus the 5 safeguarding bodies). The game's structure is a
> Hades-style rogue-lite: each **run** is a formative session in
> one subject, each **chamber** is one question drawn from a real
> SEC or equivalent past paper, each **boon** is a learning outcome
> from the NCCA syllabus offered by a deity drawn from the
> jurisdiction's mythology. Everything on screen can be **traced
> back to its source** in one click — that is the project's core
> invariant.

This is the canonical implementation of the
[`cianfhoghlaim-educational-mmo`](../../../../dev/cianfhoghlaim/openspec/specs/cianfhoghlaim-educational-mmo/spec.md)
spec. It supersedes the deprecated `tuatha-platform` and
`tuatha-mmo` skills. The legacy themes (Pent-Elemental Cosmology,
Babylon.js 3D, SpacetimeDB v2, Crypteolas financial token, Anam
Cara, Brown Ajah) are hard-archived; the technological choices
(BAML extraction, DLT ingestion, Dagster asset graph, CocoIndex
embedding, LiteLLM gateway, Cognee + Graphiti + LanceDB + Letta
memory, Convex + Hono + TanStack Start + CopilotKit web stack)
are kept.

## The Evidence Ladder — the project's core invariant

**Nothing renders unless it can name its source.** Every visible
artefact carries an unbroken chain back to an official document:

| Rung | Field | Produced by |
|:--|:--|:--|
| **1. Document** | `source_url`, `sha256`, `fetched_at`, `licence`, `rights_holder` | `tuatha/sources/official_doc_fetcher.py` |
| **2. Location** | `page`, `bbox`, `has_text_layer`, `fonts` | `tuatha/sources/pdf_page_metadata.py` |
| **3. Extraction** | `baml_function`, `prompt_version`, `confidence`, `evidence_spans` | BAML + Langfuse-resolved prompts |
| **4. Evaluation** | RAGAS faithfulness / relevancy / recall / precision + `passed_threshold` | `tuatha/eval/ragas_evaluator.py` |
| **5. Anchor** | Merkle root over rungs 1–4 | `tuatha/contracts/CredAnchor.sol` + `tuatha/badges/anchor.py` |

Sub-threshold output is **quarantined, never published**. Badges
mint only when rung 5 is complete.

## Hades / Hades 2 → tuatha

| Game | tuatha | Provenance rung |
|:--|:--|:--|
| A run | one formative session in one subject | — |
| Chamber | one question | SEC paper, page + sha256 |
| Door showing its reward | pick the next chamber by the LO it trains | LO code from the NCCA syllabus |
| Boon from a god | a technique/scaffold tied to that LO, granted by a deity | deity cited to mythology corpus; LO cited to syllabus page |
| Pantheon | per-jurisdiction — Tuatha Dé Danann (IE/NCCA), Mabinogi incl. Gwydion (Wales/WJEC), Ulster Cycle (NI/CCEA), Manannán mac Lir (IoM), Scottish myth (SQA) | Wikipedia + Dúchas + Logainm |
| Heat / Pact of Punishment | difficulty — which marking-scheme band you're targeting, timed, hints off | marking-scheme grade bands |
| Death → the House | end of run → mastery review | RAGAS + score trace |
| Mirror of Night | persistent per-LO mastery across runs | `tuatha_player_progress` |
| Keepsakes | repeat encounters unlock deeper lore *and* deeper subject content | lore ledger |
| The escape attempt | a full past-paper section under exam conditions | SEC paper |
| Prophecies fulfilled | badges minted **only on a complete evidence chain** | `CredAnchor.sol` Merkle anchor |

## Repository layout (this repo only — the build target)

```
tuatha/                              # GitHub: github.com/cianfhoghlaim/tuatha
├── README.md                        # this file
├── LICENSE.md                       # BUSL-1.1 (CIANCHOSAINT edition)
├── AGENTS.md                        # developer quick-reference
├── DEVELOPMENT.md                   # how-to-add-a-subject
├── pyproject.toml                   # uv-managed
├── mise.toml                        # task namespace
├── .gitignore .devcontainer/ .github/workflows/ci.yml
├── sources/                         # the official corpus spine (Phase 1)
│   ├── corpus/                      # 148 NCCA PDFs (path-only, content local)
│   ├── official_doc_fetcher.py      # rung 1 — 8 jurisdictions + 5 safeguarding bodies
│   ├── pdf_page_metadata.py         # rung 2 — sha256 + page + bbox + fonts
│   ├── registry.py                  # operator-facing per-source catalogue
│   ├── policy_index.py              # per-source context-aware policy view
│   └── mythology/
│       └── celtic_mythology.py      # 467-line lancedb + pydantic (the real tool, not the stub)
├── tuatha/
│   ├── subjects/                    # the 8 NCCA subject agents
│   ├── tools/                       # 40 per-subject tools
│   ├── agents/
│   │   ├── media_intel/             # the 10-tool descriptor
│   │   ├── educational/             # the 3 educational agents
│   │   ├── hackathon/               # the 4 BIEP hackathon features
│   │   ├── adk/                     # un-archived ADK layer (tuatha_root_agent, mythology_narrator_agent, celtic_tutor_agent, curriculum_comparison_agent)
│   │   │                            # + 2 tools (mythology_query, player_progress) + 2 API routes (game_state, mythology)
│   │   └── api/routes/              # Hono API surface
│   ├── baml/                        # the BAML contracts (re-extracted from cianfhoghlaim)
│   │   ├── celtic_mythology.baml    # the real Gwydion/Mabinogi/LO/Dúchas contract
│   │   ├── lc_extraction_ie.baml     # the real NCCA LC extraction
│   │   ├── clients.baml
│   │   └── .baml_client/             # auto-generated stubs (regen via baml-cli when available)
│   ├── dlt/                         # 8 sources × 5 categories = 40 DLT sources (Ireland-first depth)
│   ├── dagster/                     # 3 asset groups (per_subject + educational + hackathon)
│   ├── cocoindex/                   # 4 BGE-M3 embedder apps
│   ├── notebooks/                   # marimo operator proofs
│   ├── badges/                      # Merkle-anchored credential ledger
│   ├── contracts/                   # CredAnchor.sol + AchievementToken.sol + foundry + tests
│   ├── asset_generation/            # the 6 real Python files (un-archived from cianfhoghlaim)
│   ├── geospatial/                  # the 9 real files (LSOA / Data Zones / SOA / Small Areas)
│   ├── callbacks/                   # citation + audit callbacks
│   ├── mcp_server/                  # MCP server surface
│   ├── ci/                          # Dagger pipeline
│   ├── docs/                        # ARCHITECTURE + AGENT_REGISTRY + THEMING + BIOGRAPHY
│   └── tests/                       # 4 test files (pytest)
├── openspec/
│   ├── changes/2026-08-25-tuatha-british-isles-mmo-consolidation-v1/
│   └── specs/tuatha-british-isles-mmo/
├── docs/                            # ARCHITECTURE + AGENT_REGISTRY + THEMING + BIOGRAPHY
├── tests/                           # 4 test files
├── .venv/                           # the resolved environment
└── old/                             # the hard-archive (preserved, read-only)
    ├── prior_top_level_tuasha/      # the 12-item pre-skeleton
    ├── scattered_agents_tuasha/     # the 61-file scattered state
    └── legacy_theming/              # Babylon.js / SpacetimeDB / Pent-Elemental
```

## 218 real files (counted 2026-08-24)

- 148 NCCA / SEC PDFs (path-only, content local — not in the repo)
- 11 badge-ledger Python files
- 4 Solidity contracts + Foundry.toml + tests
- 6 asset-generation Python files
- 9 geospatial-boundary Python files
- 22 ADK agent Python files
- 13 BAML contract files + 3 BAML client stubs
- 4 test files + 4 doc files + 2 CI files + 3 dev-container files

## Where the real code came from (the audit trail)

This repository was assembled from real (not stub) code:

- `sources/official_doc_fetcher.py` + `pdf_page_metadata.py` ← from `gemini_hackathon` (the live public repo)
- `sources/mythology/celtic_mythology.py` ← the real 467-line lancedb + pydantic tool
- `tuatha/agents/adk/*.py` ← the real ADK layer in `cianfhoghlaim/agents/adk/`
- `tuatha/asset_generation/fibo/` + `invoke.py` ← the real files buried as legacy theming
- `tuatha/geospatial/` ← the real LSOA / Data Zones / SOA / Small Areas boundaries
- `tuatha/badges/` + `tuatha/contracts/` ← the real Merkle-anchored credential layer
- The 148 NCCA / SEC PDFs ← the real corpus at `cianfhoghlaim/leaving_certificate/`

The previous session's "288 file scaffolding" with 40 inert DLT
sources + stub BAML contracts + 36 stub tools has been **replaced**
with this real-code foundation. The DLT sources are being rewritten
in Phase 1 against the real document spine (rung 1) and the real
PDF metadata (rung 2).

## The 5 provability gates (W1 → W8 will be checked against these)

| Gate | Check |
|:--|:--|
| **G7 provenance** | no published row lacking `source_url` + `sha256` + `page` |
| **G8 eval** | RAGAS faithfulness ≥ threshold on a golden set, else build fails |
| **G9 no-inert** | no DLT resource yields empty; no Dagster asset is a no-op |
| **G10 theming** | every palette carries a provenance block resolving to a fetched document |
| **G11 lore** | every lore artefact has ≥1 citation resolving to a real source row |
| **G12 licence** | no source PDF committed; derived metadata only (public repo) |

## The workstreams (sequenced)

| Phase | Work | Exit condition |
|:--|:--|:--|
| **0** | Relocate, de-dup, relicense (BUSL-1.1), un-archive the buried real files | **this commit** |
| **1** | W1 spine + kill the 40 inert sources | **G9 goes green**; real NCCA/SEC rows |
| **2** | W2 eval/prompts + W3 theming | G7/G10 green |
| **3** | W5 assessment + W4 lore | one subject end-to-end through all 5 rungs; G8/G11 green |
| **4** | W6 assets + W7 web + W8 fleet/credentials | a playable run where every element is inspectable |
| **5** | openspec specs, gate wiring, docs | docs describe only what exists |

## Cross-repo surface

- The monorepo `cianfhoghlaim` is at `~/dev/cianfhoghlaim/`
  (branch `token-plan-lc-pipeline-2026-08`); the
  `tuatha-british-isles-mmo-consolidation-v1` change lives
  there and references this repo as the implementation surface.
- The sibling `gemini_hackathon` (at `~/dev/gemini_hackathon/`)
  is **NOT cross-referenced** per the user's decision; this repo
  independently implements the theming + asset-gen + fleet
  patterns it was modelled on.
- The sibling `cianchosaint` + `ciandlithe` provide the
  `ragas-eval-pipeline` + `langfuse-prompt-management` reference
  design patterns that the W2 provable-extraction work will port.

## Licence

This repository is licensed under the **Business Source License
1.1 (CIANCHOSAINT edition)**, matching `cianchosaint` and
`ciandlithe`. The Change Date is 2029-08-25; on that date the
licence converts to the permissive Apache-2.0 form. No source
PDFs are committed to the repository; only derived metadata
(sha256, page references, learning outcome codes) per G12.

---

**Last updated**: 2026-08-24.
**Owner**: Build agent (the British Isles Formative Assessment MMO project).
