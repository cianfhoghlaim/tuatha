"""tuatha.dagster.media_intel — media descriptor + 5-class extraction asset group."""
from __future__ import annotations
from dagster import asset, AssetExecutionContext


@asset(group_name="tuatha_media_intel", compute_kind="dlt")
def media_intel_l1(context: AssetExecutionContext) -> dict:
    context.add_output_metadata({"status": "dispatched"})
    return {"phase": "rung-1_pdfs", "classes": ["comic", "prose", "animation", "gameplay", "official_document"]}
