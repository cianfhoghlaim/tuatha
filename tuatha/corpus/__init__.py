"""tuatha.corpus — the read-only boundary onto the education corpus.

tuatha consumes the corpus that cianfhoghlaim manufactures. Everything
that crosses that line goes through this package, and nothing in it
writes. See CONTRACT.md for the rules and the reasoning.
"""

from .client import (
    COMPETENCIES_TABLE,
    CORPUS_EMBEDDER,
    CORPUS_EMBEDDING_DIM,
    CorpusClient,
    CorpusUnavailableError,
    corpus,
)
from .contracts import (
    SUBJECTS,
    Competency,
    DocKind,
    SubjectChunk,
    lc_table_name,
)

__all__ = [
    "COMPETENCIES_TABLE",
    "CORPUS_EMBEDDER",
    "CORPUS_EMBEDDING_DIM",
    "SUBJECTS",
    "Competency",
    "CorpusClient",
    "CorpusUnavailableError",
    "DocKind",
    "SubjectChunk",
    "corpus",
    "lc_table_name",
]
