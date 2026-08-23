"""tuatha.cocoindex.hackathon — the CocoIndex v1 App for 4 BIEP hackathon features.

Per the centralized-schema-registry contract: the embedder is
the canonical BAAI/bge-m3 1024-d (per
cocoindex_flows/_lifespan.py:107).
"""
from __future__ import annotations

from cocoindex import App, dataclass


@dataclass
class HackathonRecord:
    """The typed record emitted by the hackathon CocoIndex App."""
    record_id: str
    work: str
    source_url: str
    source_timestamp: str
    vector: list[float]  # the BAAI/bge-m3 1024-d embedding


hackathon_app = App(
    name="hackathon",
    description="The CocoIndex v1 App for 4 BIEP hackathon features.",
)


@hackathon_app.mount_table(
    name=f"hackathon_lance",
    vector_dim=1024,
)
def hackathon_index(record: HackathonRecord) -> None:
    """The hackathon indexer."""
    pass
