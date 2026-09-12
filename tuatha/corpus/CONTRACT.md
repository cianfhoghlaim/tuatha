# The corpus boundary contract

tuatha and cianfhoghlaim share one Lance namespace but are separate
repositories with separate Python paths. This document defines what
tuatha may touch, and in which direction.

## The two roles

**cianfhoghlaim manufactures content.** It fetches NCCA/SEC/AQA/SQA
documents, runs BAML extraction over them, embeds the results, and
maintains rungs 1–4 of the Evidence Ladder. It owns the education
corpus.

**tuatha consumes content.** It reads that corpus and decides what a
chamber is, which deity offers which boon, what an ANAM particle looks
like, and how a run renders. It owns the game.

A change to how a learning outcome is *extracted* belongs in
cianfhoghlaim. A change to how a learning outcome becomes a *boon*
belongs here.

## The namespace split

Both repos write into the `cianfhoghlaim.*` Lance namespace — that was
a deliberate choice to avoid a migration. The boundary is therefore
enforced by this contract rather than by the namespace, which makes the
rules below load-bearing rather than advisory.

| Namespace | cianfhoghlaim | tuatha |
|:--|:--|:--|
| `cianfhoghlaim.education.*` | read + write | **read only** |
| `cianfhoghlaim.lc.*` | read + write | **read only** |
| `cianfhoghlaim.celtic.*` | read + write | **read only** |
| `cianfhoghlaim.tuatha.*` | — | read + write |

Two rules follow:

1. **tuatha never writes outside `cianfhoghlaim.tuatha.*`.** Every read
   of the education corpus goes through `tuatha.corpus.client`, which
   opens tables read-only. There is no write path in this package, and
   adding one is the thing this document exists to prevent.
2. **cianfhoghlaim never writes into `cianfhoghlaim.tuatha.*`.** Those
   tables are produced by the ANAM capture pipeline, which lives here.

## No cross-repo imports

tuatha must not import `cianfhoghlaim`, `meaisinfhoghlaim`,
`cianchosaint`, `ciandlithe`, or `gemini_hackathon`. Such an import
resolves on a machine where both checkouts happen to be on `sys.path`
and nowhere else. In practice it does not fail loudly — it lands in an
`except ImportError` branch and disables a feature silently, which is
how `FIBO_AVAILABLE` sat permanently `False` and how the media
descriptor agent ran on a stub wiring class for its whole life.

`mise run tuatha:doctor` fails the build on any such import.

Where tuatha needs something cianfhoghlaim owns:

| Need | Do this instead |
|:--|:--|
| Corpus rows | `tuatha.corpus.client` |
| Model selection | `tuatha.models.registry` — declare the role, override by env |
| Agent wiring | `tuatha.routing` |
| Service endpoints | `tuatha.config` — read from the environment |

## The read surface

The education corpus tables tuatha reads, with the schema it relies on.
These are **frozen from tuatha's side**: cianfhoghlaim may add columns,
but removing or renaming one of these breaks the game.

### `cianfhoghlaim.lc.{subject}.{level}_{language}`

Produced by `cocoindex_flows/subjects/lc_subject_embedding.py`. One row
per chunked paragraph of an NCCA syllabus, SEC exam paper, or marking
scheme.

| Column | Type | Notes |
|:--|:--|:--|
| `chunk_id` | str | `{path}#{index}`, unique |
| `subject` | str | subject slug |
| `level` | str | `hl` / `ol` / `fl` |
| `language` | str | `en` / `ga` |
| `filename` | str | the source document; how tuatha tells a syllabus from a paper |
| `chunk_index` | int | ordinal within the document |
| `text` | str | the chunk body |
| `embedding` | vector(1024) | `BAAI/bge-m3`, multilingual |

The embedder matters: `bge-m3` puts Irish and English in one vector
space, so a Gaeilge query can retrieve an English chunk. Any tuatha-side
query vector must come from the same model or the results are noise.

### `cianfhoghlaim.lc.cross_subject.competencies`

The NCCA key competencies, shared across subjects.

## Consequences for the Evidence Ladder

tuatha's core invariant is that nothing renders unless it can name its
source. Rungs 1–4 are produced in cianfhoghlaim; tuatha receives them
already attached to the row. So tuatha must **propagate** provenance
rather than generate it: a boon derived from a chunk carries that
chunk's `chunk_id` and `filename` through to render time.

Dropping those fields in an intermediate transform silently breaks the
G7 provenance gate, and it breaks it in a way that only shows up when
someone clicks through to a source that is no longer named.
