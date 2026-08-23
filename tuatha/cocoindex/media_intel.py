"""tuatha.cocoindex.media_intel — the CocoIndex v1 App for the 5-class media descriptor pipeline.

Per the centralized-schema-registry contract: the embedder is
the canonical BAAI/bge-m3 1024-d (per
cocoindex_flows/_lifespan.py:107).
"""
from __future__ import annotations

from cocoindex import App, dataclass


@dataclass
class MediaIntelRecord:
    """The typed record emitted by the media_intel CocoIndex App."""
    record_id: str
    work: str
    source_url: str
    source_timestamp: str
    vector: list[float]  # the BAAI/bge-m3 1024-d embedding


media_intel_app = App(
    name="media_intel",
    description="The CocoIndex v1 App for the 5-class media descriptor pipeline.",
)


@media_intel_app.mount_table(
    name=f"media_intel_lance",
    vector_dim=1024,
)
def media_intel_index(record: MediaIntelRecord) -> None:
    """The media_intel indexer."""
    pass
