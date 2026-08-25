"""tuatha.corpus.client — the read-only client over the education corpus.

This is the *only* place tuatha touches cianfhoghlaim-owned data. See
CONTRACT.md for the boundary it enforces.

There is no write path in this module, deliberately. Adding one is the
specific thing the contract exists to prevent.

Two design choices worth stating:

* **Missing tables raise.** A subject with no corpus coverage yet is a
  real condition the caller must handle; returning an empty list makes
  it indistinguishable from "the syllabus has no matching content",
  which is how a silently empty game world happens.
* **Vector search needs a caller-supplied vector.** The corpus is
  embedded with ``BAAI/bge-m3``. tuatha does not host that model, so it
  will not silently embed a query with something else and return
  plausible nonsense. Text search works with no model at all.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from functools import lru_cache
from typing import Any

from .contracts import SUBJECTS, Competency, DocKind, SubjectChunk, lc_table_name

__all__ = [
    "COMPETENCIES_TABLE",
    "CorpusClient",
    "CorpusUnavailableError",
    "corpus",
]

#: The cross-subject competencies table.
COMPETENCIES_TABLE = "cianfhoghlaim.lc.cross_subject.competencies"

#: The embedder the corpus was built with. A query vector from any
#: other model is not comparable to these embeddings.
CORPUS_EMBEDDER = "BAAI/bge-m3"
CORPUS_EMBEDDING_DIM = 1024


class CorpusUnavailableError(RuntimeError):
    """Raised when the corpus cannot be reached or a table is absent."""


class CorpusClient:
    """Read-only access to the shared education corpus.

    Args:
        uri: the Lance namespace root. Defaults to ``TUATHA_LANCE_URI``.
    """

    def __init__(self, uri: str | None = None) -> None:
        self._uri = uri or os.environ.get("TUATHA_LANCE_URI") or ""
        self._db: Any = None

    # -- connection ----------------------------------------------------

    @property
    def uri(self) -> str:
        if not self._uri:
            raise CorpusUnavailableError(
                "TUATHA_LANCE_URI is not set. Point it at the Lance "
                "namespace root — a local path for development, or the "
                "s3:// URI of the shared lakehouse. See "
                "tuatha/corpus/CONTRACT.md."
            )
        return self._uri

    def _connect(self) -> Any:
        if self._db is None:
            try:
                import lancedb
            except ImportError as exc:  # pragma: no cover - dependency guard
                raise CorpusUnavailableError(
                    "lancedb is not installed; run `mise run tuatha:install`."
                ) from exc
            self._db = lancedb.connect(self.uri)
        return self._db

    def _open(self, table_name: str) -> Any:
        """Open a table, or explain precisely which one was missing."""
        db = self._connect()
        try:
            return db.open_table(table_name)
        except Exception as exc:
            raise CorpusUnavailableError(
                f"Corpus table {table_name!r} is not present at {self.uri!r}. "
                "The education corpus is produced by cianfhoghlaim; tuatha "
                "only reads it. Materialise it there first."
            ) from exc

    def table_exists(self, subject: str, level: str = "hl", language: str = "en") -> bool:
        """Return whether a subject has corpus coverage, without raising."""
        if subject not in SUBJECTS:
            return False
        try:
            db = self._connect()
        except CorpusUnavailableError:
            return False
        # `table_names()` is deprecated in favour of `list_tables()`;
        # keep the old call as a fallback for older lancedb releases.
        lister = getattr(db, "list_tables", None) or db.table_names
        return lc_table_name(subject, level, language) in lister()

    # -- reads ---------------------------------------------------------

    def chunks(
        self,
        subject: str,
        *,
        level: str = "hl",
        language: str = "en",
        doc_kind: str | None = None,
        limit: int = 50,
    ) -> list[SubjectChunk]:
        """Return chunks for a subject, newest-arbitrary order.

        Args:
            doc_kind: optionally keep only one of
                :class:`~tuatha.corpus.contracts.DocKind`. Filtering
                happens after the scan because the corpus has no
                ``doc_kind`` column — it is inferred from ``filename``.
        """
        table = self._open(lc_table_name(subject, level, language))
        # Over-fetch when filtering, since the filter is applied here
        # rather than pushed down into the scan.
        scan_limit = limit * 5 if doc_kind else limit
        rows = table.search().limit(scan_limit).to_list()
        return self._to_chunks(rows, doc_kind=doc_kind, limit=limit)

    def search_text(
        self,
        subject: str,
        query: str,
        *,
        level: str = "hl",
        language: str = "en",
        doc_kind: str | None = None,
        limit: int = 10,
    ) -> list[SubjectChunk]:
        """Full-text search within one subject's corpus.

        Requires an FTS index on ``text``. Falls back to a substring
        scan when no index exists, so development against a fresh local
        namespace still returns something useful.
        """
        table = self._open(lc_table_name(subject, level, language))
        scan_limit = limit * 5 if doc_kind else limit
        try:
            rows = table.search(query, query_type="fts").limit(scan_limit).to_list()
        except Exception:
            rows = self._substring_scan(table, query, scan_limit)
        return self._to_chunks(rows, doc_kind=doc_kind, limit=limit)

    def search_vector(
        self,
        subject: str,
        query_vector: Sequence[float],
        *,
        level: str = "hl",
        language: str = "en",
        doc_kind: str | None = None,
        limit: int = 10,
    ) -> list[SubjectChunk]:
        """Vector search within one subject's corpus.

        Args:
            query_vector: a ``BAAI/bge-m3`` embedding of the query.

        Raises:
            ValueError: if the vector is the wrong width. A dimension
                mismatch means it came from a different model, and
                results would be meaningless rather than merely poor.
        """
        if len(query_vector) != CORPUS_EMBEDDING_DIM:
            raise ValueError(
                f"Query vector has {len(query_vector)} dimensions; the corpus "
                f"is embedded with {CORPUS_EMBEDDER} at {CORPUS_EMBEDDING_DIM}. "
                "A vector from a different model is not comparable to these "
                "embeddings."
            )
        table = self._open(lc_table_name(subject, level, language))
        scan_limit = limit * 5 if doc_kind else limit
        rows = table.search(list(query_vector)).limit(scan_limit).to_list()
        return self._to_chunks(rows, doc_kind=doc_kind, limit=limit)

    def competencies(self, limit: int = 100) -> list[Competency]:
        """Return the NCCA key competencies."""
        rows = self._open(COMPETENCIES_TABLE).search().limit(limit).to_list()
        return [Competency.model_validate(row) for row in rows]

    def coverage(self, level: str = "hl", language: str = "en") -> dict[str, bool]:
        """Report which subjects currently have corpus coverage.

        Useful as a preflight: the game should know which subjects it
        can actually build runs for before it offers them.
        """
        return {s: self.table_exists(s, level, language) for s in SUBJECTS}

    # -- helpers -------------------------------------------------------

    @staticmethod
    def _substring_scan(table: Any, query: str, limit: int) -> list[dict[str, Any]]:
        """Case-insensitive substring fallback when FTS is unavailable."""
        needle = query.lower()
        matched: list[dict[str, Any]] = []
        for row in table.search().limit(limit * 20).to_list():
            if needle in str(row.get("text", "")).lower():
                matched.append(row)
                if len(matched) >= limit:
                    break
        return matched

    @staticmethod
    def _to_chunks(
        rows: list[dict[str, Any]],
        *,
        doc_kind: str | None,
        limit: int,
    ) -> list[SubjectChunk]:
        chunks = [SubjectChunk.model_validate(row) for row in rows]
        if doc_kind is not None:
            if doc_kind not in DocKind.all():
                raise ValueError(
                    f"Unknown doc_kind {doc_kind!r}; expected one of "
                    f"{', '.join(DocKind.all())}."
                )
            chunks = [c for c in chunks if c.doc_kind == doc_kind]
        return chunks[:limit]


@lru_cache(maxsize=1)
def corpus() -> CorpusClient:
    """Return the process-wide corpus client."""
    return CorpusClient()
