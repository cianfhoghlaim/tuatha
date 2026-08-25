"""tuatha.cocoindex.per_subject — the CocoIndex v1 App for 8 NCCA subjects × 5 categories.

Per the centralized-schema-registry contract: the embedder is
the canonical BAAI/bge-m3 1024-d (per
cocoindex_flows/_lifespan.py:107).
"""
from __future__ import annotations

from cocoindex import App, dataclass


@dataclass
class PerSubjectRecord:
    """The typed record emitted by the per_subject CocoIndex App."""
    record_id: str
    work: str
    source_url: str
    source_timestamp: str
    vector: list[float]  # the BAAI/bge-m3 1024-d embedding


per_subject_app = App(
    name="per_subject",
    description="The CocoIndex v1 App for 8 NCCA subjects × 5 categories.",
)


@per_subject_app.mount_table(
    name=f"per_subject_lance",
    vector_dim=1024,
)
def per_subject_index(record: PerSubjectRecord) -> None:
    """The per_subject indexer."""
    pass
