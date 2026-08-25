"""tuatha.dagster.hackathon — BIEP hackathon features asset group."""
from __future__ import annotations
from dagster import asset, AssetExecutionContext


@asset(group_name="tuatha_hackathon", compute_kind="dlt")
def hackathon_l1(context: AssetExecutionContext) -> dict:
    context.add_output_metadata({"status": "dispatched"})
    return {"phase": "rung-1", "agents": ["marking_grader", "adaptive_tutor", "equivalency_generator", "curriculum_change_sensor"]}
