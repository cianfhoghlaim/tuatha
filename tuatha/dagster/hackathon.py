"""tuatha.dagster.hackathon — the Dagster asset group for 4 BIEP hackathon features (marking grader + adaptive tutor + equivalency generator + curriculum change sensor).

Per the 5-layer KCG Component Architecture (per the
dagster-5-layer-component-architecture spec).
"""
from __future__ import annotations

from dagster import asset, AssetExecutionContext

from tuatha.config import TuathaConfig


@asset(group_name=f"tuatha_hackathon", compute_kind="dlt")
def hackathon_l1(context: AssetExecutionContext) -> dict:
    """The L1 Ingestion asset for 4 BIEP hackathon features (marking grader + adaptive tutor + equivalency generator + curriculum change sensor)."""
    config = TuathaConfig.from_env()
    context.add_output_metadata({"status": "extracted"})
    return {"status": "dispatched", "config": config.litellm.api_base}


@asset(group_name=f"tuatha_hackathon", compute_kind="baml")
def hackathon_l2(context: AssetExecutionContext) -> dict:
    """The L2 Materials asset for 4 BIEP hackathon features (marking grader + adaptive tutor + equivalency generator + curriculum change sensor)."""
    context.add_output_metadata({"status": "extracted"})
    return {"status": "dispatched"}


@asset(group_name=f"tuatha_hackathon", compute_kind="cocoindex")
def hackathon_l3(context: AssetExecutionContext) -> dict:
    """The L3 Model Lifecycle asset for 4 BIEP hackathon features (marking grader + adaptive tutor + equivalency generator + curriculum change sensor)."""
    context.add_output_metadata({"status": "indexed"})
    return {"status": "dispatched"}
