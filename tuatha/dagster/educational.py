"""tuatha.dagster.educational — educational agents asset group."""
from __future__ import annotations
from dagster import asset, AssetExecutionContext


@asset(group_name="tuatha_educational", compute_kind="dlt")
def educational_l1(context: AssetExecutionContext) -> dict:
    context.add_output_metadata({"status": "dispatched"})
    return {"phase": "rung-1", "agents": ["academic_history_agent", "celtic_grammar_agent", "celtic_morphology_agent"]}
