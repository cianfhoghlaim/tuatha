"""tuatha.dagster.observation — the ADK observation eval surface.

Per the
`openspec/changes/2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1/`
T3.1-T3.6: Google ADK observation evals replace the 8 RAGAS
LLM-judge asset checks. The 7 TrajectoryEvaluator subclasses
score the trajectory (the path the agent took through BAML
functions, embedders, cross-source joins) — not just the final
output.

Sub-modules:
- `eval_runner.py` — wraps google.adk.evaluation.AgentEvaluator.run_eval(...)
- `eval_metrics.py` — the 7 TrajectoryEvaluator subclasses
- `otel_langfuse_bridge.py` — sends ADK OTEL spans to Langfuse
- `eval_sets/` — YAML eval cases (anam / marking / tutor)

Per the centralized-registry contract: no hardcoded model
strings. All LLM-as-judge calls route through
`MODEL_REGISTRY.resolve("text_llm", "judge")`.

Per the 2026-08-27 change: 7 TrajectoryEvaluators (one for
each educational pipeline stage), each gated as a Dagster
`@asset_check`.
"""
from __future__ import annotations

from .eval_metrics import (
    AdaptiveTutorRelevanceTrajectoryEvaluator,
    AnamColorAnchorTrajectoryEvaluator,
    EquivalencyConsistencyTrajectoryEvaluator,
    FeedbackQualityTrajectoryEvaluator,
    FormativeItemUniquenessTrajectoryEvaluator,
    MarkingAccuracyTrajectoryEvaluator,
    SyllabusCoverageTrajectoryEvaluator,
)

__all__ = [
    "AdaptiveTutorRelevanceTrajectoryEvaluator",
    "AnamColorAnchorTrajectoryEvaluator",
    "EquivalencyConsistencyTrajectoryEvaluator",
    "FeedbackQualityTrajectoryEvaluator",
    "FormativeItemUniquenessTrajectoryEvaluator",
    "MarkingAccuracyTrajectoryEvaluator",
    "SyllabusCoverageTrajectoryEvaluator",
]
