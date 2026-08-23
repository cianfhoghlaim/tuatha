"""tuatha.cocoindex.cross_subject — the CocoIndex v1 App for cross-subject comparative embedding.

Per the centralized-schema-registry contract: the embedder is
the canonical BAAI/bge-m3 1024-d (per
cocoindex_flows/_lifespan.py:107).
"""
from __future__ import annotations

from cocoindex import App, dataclass


@dataclass
class CrossSubjectRecord:
    """The typed record emitted by the cross_subject CocoIndex App."""
    record_id: str
    work: str
    source_url: str
    source_timestamp: str
    vector: list[float]  # the BAAI/bge-m3 1024-d embedding


cross_subject_app = App(
    name="cross_subject",
    description="The CocoIndex v1 App for cross-subject comparative embedding.",
)


@cross_subject_app.mount_table(
    name=f"cross_subject_lance",
    vector_dim=1024,
)
def cross_subject_index(record: CrossSubjectRecord) -> None:
    """The cross_subject indexer."""
    pass
