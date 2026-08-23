"""tuatha.dagster.educational — the Dagster asset group for 3 educational agents (academic history + celtic grammar + celtic morphology).

Per the 5-layer KCG Component Architecture (per the
dagster-5-layer-component-architecture spec).
"""
from __future__ import annotations

from dagster import asset, AssetExecutionContext

from tuatha.config import TuathaConfig


@asset(group_name=f"tuatha_educational", compute_kind="dlt")
def educational_l1(context: AssetExecutionContext) -> dict:
    """The L1 Ingestion asset for 3 educational agents (academic history + celtic grammar + celtic morphology)."""
    config = TuathaConfig.from_env()
    context.add_output_metadata({"status": "extracted"})
    return {"status": "dispatched", "config": config.litellm.api_base}


@asset(group_name=f"tuatha_educational", compute_kind="baml")
def educational_l2(context: AssetExecutionContext) -> dict:
    """The L2 Materials asset for 3 educational agents (academic history + celtic grammar + celtic morphology)."""
    context.add_output_metadata({"status": "extracted"})
    return {"status": "dispatched"}


@asset(group_name=f"tuatha_educational", compute_kind="cocoindex")
def educational_l3(context: AssetExecutionContext) -> dict:
    """The L3 Model Lifecycle asset for 3 educational agents (academic history + celtic grammar + celtic morphology)."""
    context.add_output_metadata({"status": "indexed"})
    return {"status": "dispatched"}
