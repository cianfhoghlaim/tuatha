"""The shared CocoIndex lifespan + LanceDB connection for the ANAM ingestors.

Conformance per the cocoindex-v1 R1-R4 contract:

- R1: exports ``shared_lifespan``, which every child module imports
- R2: owns the canonical ContextKeys
- R3: module-scope ``coco.App`` in every child module
- R4: at least one ``@coco.fn`` decorator in every child module

The connection targets the shared Lance namespace. The ANAM Apps write
only ``cianfhoghlaim.tuatha.*``; see ``tuatha/corpus/CONTRACT.md``.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import lancedb
from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder
from lancedb import AsyncConnection

import cocoindex as coco

# Canonical embedder: BAAI/bge-m3 (1024-d, multilingual). This must match
# the model the education corpus was embedded with, or ANAM vectors and
# corpus vectors will not be comparable.
EMBED_MODEL = "BAAI/bge-m3"

#: Local fallback when TUATHA_LANCE_URI is unset, for first-run dev.
DEFAULT_LANCE_URI = "./data/tuatha_lance"

# The ContextKeys shared by the four ANAM Apps.
LANCE_DB = coco.ContextKey[AsyncConnection]("tuatha.anam.lance_db", detect_change=True)
EMBEDDER = coco.ContextKey[SentenceTransformerEmbedder](
    "tuatha.anam.embedder", detect_change=True
)
S3_LANCE_URI = coco.ContextKey[str]("tuatha.anam.s3_lance_uri", detect_change=True)


@coco.lifespan
async def shared_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    """Open the Lance connection and load the embedder exactly once.

    The URI comes from ``TUATHA_LANCE_URI`` (hydrated from Infisical via
    the Locket sidecar in deployment), falling back to a local directory.

    The connection is opened with ``lancedb.connect_async``. This
    previously called ``Connection.connect_async`` on a name imported as
    ``from lancedb import Connection``, which does not exist — the
    correct names are ``AsyncConnection`` and the module-level
    ``connect_async``. The module therefore could not be imported at all.
    """
    lance_uri = os.environ.get("TUATHA_LANCE_URI", DEFAULT_LANCE_URI)
    lance = await lancedb.connect_async(lance_uri)
    builder.provide(S3_LANCE_URI, lance_uri)
    builder.provide(LANCE_DB, lance)
    builder.provide(
        EMBEDDER,
        SentenceTransformerEmbedder(
            model_name=EMBED_MODEL,
            # M-series native; falls back to cpu transparently.
            device=os.environ.get("TUATHA_EMBED_DEVICE", "mps"),
        ),
    )
    yield
