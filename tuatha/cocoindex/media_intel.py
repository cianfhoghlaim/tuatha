"""tuatha.cocoindex.media_intel — CocoIndex v1 App for media intel."""
from __future__ import annotations
from cocoindex import App, dataclass


@dataclass
class MediaIntelRecord:
    record_id: str
    work: str
    source_url: str
    source_timestamp: str
    vector: list[float]


media_intel_app = App(name="media_intel", description="CocoIndex v1 App for media intel")


@media_intel_app.mount_table(name="media_intel_lance", vector_dim=1024)
def media_intel_index(record: MediaIntelRecord) -> None:
    pass
