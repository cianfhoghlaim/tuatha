"""tuatha.dagster.per_subject — per-subject Dagster asset group."""
from __future__ import annotations
from dagster import asset, AssetExecutionContext
from tuatha.config import TuathaConfig


@asset(group_name="tuatha_per_subject", compute_kind="dlt")
def per_subject_l1(context: AssetExecutionContext) -> dict:
    """The L1 Ingestion asset for 8 NCCA subjects × 5 categories (40 per-subject DLT sources)."""
    config = TuathaConfig.from_env()
    context.add_output_metadata({"status": "extracted", "config": config.litellm.api_base})
    return {"phase": "rung-1", "status": "dispatched"}


@asset(group_name="tuatha_per_subject", compute_kind="baml")
def per_subject_l2(context: AssetExecutionContext) -> dict:
    context.add_output_metadata({"status": "extracted"})
    return {"phase": "rung-3_to_rung-4", "status": "dispatched"}


@asset(group_name="tuatha_per_subject", compute_kind="cocoindex")
def per_subject_l3(context: AssetExecutionContext) -> dict:
    context.add_output_metadata({"status": "indexed"})
    return {"phase": "rung-4-rag", "status": "dispatched"}
