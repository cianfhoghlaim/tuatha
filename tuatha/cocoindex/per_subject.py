"""tuatha.cocoindex.per_subject — CocoIndex v1 App for per subject."""
from __future__ import annotations
from cocoindex import App, dataclass


@dataclass
class PerSubjectRecord:
    record_id: str
    work: str
    source_url: str
    source_timestamp: str
    vector: list[float]


per_subject_app = App(name="per_subject", description="CocoIndex v1 App for per subject")


@per_subject_app.mount_table(name="per_subject_lance", vector_dim=1024)
def per_subject_index(record: PerSubjectRecord) -> None:
    pass
