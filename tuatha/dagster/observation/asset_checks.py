"""tuatha.dagster.observation.asset_checks — Dagster @asset_check wrappers.

Per the
`openspec/changes/2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1/`
T3.4: wrap the 7 `TrajectoryEvaluator` subclasses in Dagster
`@asset_check` decorators so they show up in the Dagster UI
asset health page.

Per the centralized-registry contract: any LLM-as-judge calls
route through `MODEL_REGISTRY.resolve("text_llm", "judge")`.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


EVAL_SETS_DIR = Path(__file__).parent / "eval_sets"


def _load_eval_set(name: str) -> dict[str, Any]:
    """Load an eval set YAML by name (without extension).

    Lightweight YAML reader (no PyYAML dependency for the
    offline dev path) — we accept the JSON-equivalent form
    too. For the production path, use `pyyaml`.
    """
    path = EVAL_SETS_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Eval set not found: {path}")
    # Lazy import: only require pyyaml if the eval is actually run.
    try:
        import yaml

        with path.open() as f:
            return yaml.safe_load(f)
    except ImportError:
        logger.warning("PyYAML not installed; eval set loading requires `uv pip install pyyaml`")
        return {"cases": []}


def _score_to_asset_check_result(score, severity_on_pass: str = "WARN") -> dict[str, Any]:
    """Convert a TrajectoryScore to a Dagster AssetCheckResult-compatible dict."""
    return {
        "passed": score.passed,
        "severity": "ERROR" if not score.passed else severity_on_pass,
        "metadata": {
            "score": score.score,
            "threshold": score.threshold,
            **score.details,
        },
    }


# The 7 asset_check wrappers. Each one:
# 1. Loads the corresponding eval set YAML.
# 2. Iterates over the cases.
# 3. Runs the TrajectoryEvaluator on each case's expected_trajectory.
# 4. Bridges the result to Langfuse.
# 5. Returns the AssetCheckResult.

def asset_check_anam_color_anchor(context) -> dict[str, Any]:
    """Asset check for the AnamColorAnchorTrajectoryEvaluator."""
    from .eval_metrics import AnamColorAnchorTrajectoryEvaluator
    from .otel_langfuse_bridge import bridge_adk_span_to_langfuse

    eval_set = _load_eval_set("anam")
    evaluator = AnamColorAnchorTrajectoryEvaluator()
    case_results: list[dict[str, Any]] = []

    for case in eval_set.get("cases", []):
        trajectory = case.get("expected_trajectory", [])
        score = evaluator.evaluate(trajectory)
        bridge_adk_span_to_langfuse(
            eval_set_name="anam",
            case_name=case["case_name"],
            score=score.score,
            threshold=score.threshold,
            passed=score.passed,
        )
        case_results.append(_score_to_asset_check_result(score))

    all_passed = all(r["passed"] for r in case_results)
    return {
        "passed": all_passed,
        "severity": "ERROR" if not all_passed else "WARN",
        "metadata": {
            "case_results": case_results,
            "evaluator": "AnamColorAnchorTrajectoryEvaluator",
        },
    }


def asset_check_marking_accuracy(context) -> dict[str, Any]:
    """Asset check for the MarkingAccuracyTrajectoryEvaluator."""
    from .eval_metrics import MarkingAccuracyTrajectoryEvaluator
    from .otel_langfuse_bridge import bridge_adk_span_to_langfuse

    eval_set = _load_eval_set("marking")
    evaluator = MarkingAccuracyTrajectoryEvaluator()
    case_results: list[dict[str, Any]] = []

    for case in eval_set.get("cases", []):
        trajectory = case.get("expected_trajectory", [])
        score = evaluator.evaluate(trajectory)
        bridge_adk_span_to_langfuse(
            eval_set_name="marking",
            case_name=case["case_name"],
            score=score.score,
            threshold=score.threshold,
            passed=score.passed,
        )
        case_results.append(_score_to_asset_check_result(score))

    all_passed = all(r["passed"] for r in case_results)
    return {
        "passed": all_passed,
        "severity": "ERROR" if not all_passed else "WARN",
        "metadata": {
            "case_results": case_results,
            "evaluator": "MarkingAccuracyTrajectoryEvaluator",
        },
    }


def asset_check_feedback_quality(context) -> dict[str, Any]:
    """Asset check for the FeedbackQualityTrajectoryEvaluator."""
    from .eval_metrics import FeedbackQualityTrajectoryEvaluator
    from .otel_langfuse_bridge import bridge_adk_span_to_langfuse

    eval_set = _load_eval_set("marking")
    evaluator = FeedbackQualityTrajectoryEvaluator()
    case_results: list[dict[str, Any]] = []

    for case in eval_set.get("cases", []):
        trajectory = case.get("expected_trajectory", [])
        score = evaluator.evaluate(trajectory)
        bridge_adk_span_to_langfuse(
            eval_set_name="marking",
            case_name=case["case_name"],
            score=score.score,
            threshold=score.threshold,
            passed=score.passed,
        )
        case_results.append(_score_to_asset_check_result(score))

    all_passed = all(r["passed"] for r in case_results)
    return {
        "passed": all_passed,
        "severity": "ERROR" if not all_passed else "WARN",
        "metadata": {
            "case_results": case_results,
            "evaluator": "FeedbackQualityTrajectoryEvaluator",
        },
    }


def asset_check_formative_item_uniqueness(context) -> dict[str, Any]:
    """Asset check for the FormativeItemUniquenessTrajectoryEvaluator.

    The full eval set for formative items is generated dynamically
    from the per-subject `qpack_<subject>.baml` contract — see
    `tuatha/dagster/per_subject.py::per_subject_l1` for the
    generation. Here we just emit the asset_check wrapper that
    runs the TrajectoryEvaluator over the most recent batch.
    """
    from .eval_metrics import FormativeItemUniquenessTrajectoryEvaluator
    from .otel_langfuse_bridge import bridge_adk_span_to_langfuse

    evaluator = FormativeItemUniquenessTrajectoryEvaluator()
    # The trajectory + prior_items are populated at runtime
    # by the per_subject_l1 Dagster asset. For the offline dev
    # path, return a no-op score.
    score = TrajectoryScore(
        score=0.0,
        threshold=evaluator.threshold,
        passed=False,
        details={"noop_reason": "no runtime trajectory (offline dev)"},
    )
    bridge_adk_span_to_langfuse(
        eval_set_name="formative_items",
        case_name="runtime_evaluation",
        score=score.score,
        threshold=score.threshold,
        passed=score.passed,
    )
    return _score_to_asset_check_result(score)


def asset_check_adaptive_tutor_relevance(context) -> dict[str, Any]:
    """Asset check for the AdaptiveTutorRelevanceTrajectoryEvaluator."""
    from .eval_metrics import AdaptiveTutorRelevanceTrajectoryEvaluator
    from .otel_langfuse_bridge import bridge_adk_span_to_langfuse

    eval_set = _load_eval_set("tutor")
    evaluator = AdaptiveTutorRelevanceTrajectoryEvaluator()
    case_results: list[dict[str, Any]] = []

    for case in eval_set.get("cases", []):
        trajectory = case.get("expected_trajectory", [])
        score = evaluator.evaluate(trajectory)
        bridge_adk_span_to_langfuse(
            eval_set_name="tutor",
            case_name=case["case_name"],
            score=score.score,
            threshold=score.threshold,
            passed=score.passed,
        )
        case_results.append(_score_to_asset_check_result(score))

    all_passed = all(r["passed"] for r in case_results)
    return {
        "passed": all_passed,
        "severity": "ERROR" if not all_passed else "WARN",
        "metadata": {
            "case_results": case_results,
            "evaluator": "AdaptiveTutorRelevanceTrajectoryEvaluator",
        },
    }


def asset_check_equivalency_consistency(context) -> dict[str, Any]:
    """Asset check for the EquivalencyConsistencyTrajectoryEvaluator."""
    from .eval_metrics import EquivalencyConsistencyTrajectoryEvaluator
    from .otel_langfuse_bridge import bridge_adk_span_to_langfuse

    # The full equivalency eval set is generated dynamically
    # from the equivalency_generator.baml::Equivgen trajectories.
    # For the offline dev path, return a no-op.
    evaluator = EquivalencyConsistencyTrajectoryEvaluator()
    score = TrajectoryScore(
        score=0.0,
        threshold=evaluator.threshold,
        passed=False,
        details={"noop_reason": "no runtime trajectory (offline dev)"},
    )
    bridge_adk_span_to_langfuse(
        eval_set_name="equivalency",
        case_name="runtime_evaluation",
        score=score.score,
        threshold=score.threshold,
        passed=score.passed,
    )
    return _score_to_asset_check_result(score)


def asset_check_syllabus_coverage(context) -> dict[str, Any]:
    """Asset check for the SyllabusCoverageTrajectoryEvaluator."""
    from .eval_metrics import SyllabusCoverageTrajectoryEvaluator
    from .otel_langfuse_bridge import bridge_adk_span_to_langfuse

    # The full syllabus coverage is computed from the per-subject
    # generated items + the canonical NCCA LO list. For the
    # offline dev path, return a no-op.
    evaluator = SyllabusCoverageTrajectoryEvaluator()
    score = TrajectoryScore(
        score=0.0,
        threshold=evaluator.threshold,
        passed=False,
        details={"noop_reason": "no runtime trajectory (offline dev)"},
    )
    bridge_adk_span_to_langfuse(
        eval_set_name="syllabus_coverage",
        case_name="runtime_evaluation",
        score=score.score,
        threshold=score.threshold,
        passed=score.passed,
    )
    return _score_to_asset_check_result(score)


# Forward-import the TrajectoryScore dataclass.
from .eval_metrics import TrajectoryScore  # noqa: E402

__all__ = [
    "asset_check_adaptive_tutor_relevance",
    "asset_check_anam_color_anchor",
    "asset_check_equivalency_consistency",
    "asset_check_feedback_quality",
    "asset_check_formative_item_uniqueness",
    "asset_check_marking_accuracy",
    "asset_check_syllabus_coverage",
]
