"""tuatha.cocoindex.hackathon — CocoIndex v1 App for hackathon."""
from __future__ import annotations
from cocoindex import App, dataclass


@dataclass
class HackathonRecord:
    record_id: str
    work: str
    source_url: str
    source_timestamp: str
    vector: list[float]


hackathon_app = App(name="hackathon", description="CocoIndex v1 App for hackathon")


@hackathon_app.mount_table(name="hackathon_lance", vector_dim=1024)
def hackathon_index(record: HackathonRecord) -> None:
    pass
