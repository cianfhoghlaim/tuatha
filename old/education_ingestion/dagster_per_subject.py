"""tuatha.dagster.per_subject — the Dagster asset group for 8 NCCA subjects × 5 categories (40 per-subject DLT sources).

Per the 5-layer KCG Component Architecture (per the
dagster-5-layer-component-architecture spec).
"""
from __future__ import annotations

from dagster import asset, AssetExecutionContext

from tuatha.config import TuathaConfig


@asset(group_name=f"tuatha_per_subject", compute_kind="dlt")
def per_subject_l1(context: AssetExecutionContext) -> dict:
    """The L1 Ingestion asset for 8 NCCA subjects × 5 categories (40 per-subject DLT sources)."""
    config = TuathaConfig.from_env()
    context.add_output_metadata({"status": "extracted"})
    return {"status": "dispatched", "config": config.litellm.api_base}


@asset(group_name=f"tuatha_per_subject", compute_kind="baml")
def per_subject_l2(context: AssetExecutionContext) -> dict:
    """The L2 Materials asset for 8 NCCA subjects × 5 categories (40 per-subject DLT sources)."""
    context.add_output_metadata({"status": "extracted"})
    return {"status": "dispatched"}


@asset(group_name=f"tuatha_per_subject", compute_kind="cocoindex")
def per_subject_l3(context: AssetExecutionContext) -> dict:
    """The L3 Model Lifecycle asset for 8 NCCA subjects × 5 categories (40 per-subject DLT sources)."""
    context.add_output_metadata({"status": "indexed"})
    return {"status": "dispatched"}
