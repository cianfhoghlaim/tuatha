"""tuatha.cocoindex.cross_subject — CocoIndex v1 App for cross subject."""
from __future__ import annotations
from cocoindex import App, dataclass


@dataclass
class CrossSubjectRecord:
    record_id: str
    work: str
    source_url: str
    source_timestamp: str
    vector: list[float]


cross_subject_app = App(name="cross_subject", description="CocoIndex v1 App for cross subject")


@cross_subject_app.mount_table(name="cross_subject_lance", vector_dim=1024)
def cross_subject_index(record: CrossSubjectRecord) -> None:
    pass
