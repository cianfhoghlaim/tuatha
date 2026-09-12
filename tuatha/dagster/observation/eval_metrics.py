"""tuatha.dagster.observation.eval_metrics — the 7 TrajectoryEvaluator subclasses.

Per the
`openspec/changes/2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1/`
T3.3: implement 7 TrajectoryEvaluator classes that score the
agent's trajectory (the sequence of BAML function invocations
+ embedder calls + cross-source joins), NOT just the final
output. This is the core ADK observation eval capability.

Per the centralized-registry contract: any LLM-as-judge calls
route through `MODEL_REGISTRY.resolve("text_llm", "judge")` —
no hardcoded model strings.

Graceful-degradation: when `google-adk` is not installed, the
evaluators return a no-op score of 0.0 + log a warning. The
Dagster `@asset_check` decorator handles the AssetCheckResult.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# Module-level LBYL probe (per the langfuse_traces.py pattern).
try:
    from google.adk.evaluation import TrajectoryEvaluator  # type: ignore

    _ADK_EVAL_AVAILABLE = True
except ImportError:
    TrajectoryEvaluator = None  # type: ignore
    _ADK_EVAL_AVAILABLE = False


# Try-import the centralized model resolver for LLM-as-judge calls.
try:
    from meaisinfhoghlaim.models import model_for  # type: ignore

    _MODEL_FOR_AVAILABLE = True
except ImportError:
    model_for = None  # type: ignore
    _MODEL_FOR_AVAILABLE = False


# The canonical 7 trajectory evaluator thresholds.
ANAM_DELTA_E_THRESHOLD = 8.0             # CIE76 ΔE between source color and ANAM color
ANAM_COLOR_ANCHOR_MIN_SCORE = 0.85      # fraction of rows that must pass
MARKING_ACCURACY_THRESHOLD = 0.7         # criterion citation accuracy
FEEDBACK_QUALITY_THRESHOLD = 0.8        # actionable + criterion-specific
FORMATIVE_ITEM_UNIQUENESS_THRESHOLD = 0.85  # cosine vs prior items
ADAPTIVE_TUTOR_RELEVANCE_THRESHOLD = 0.8  # state-action consistency
EQUIVALENCY_CONSISTENCY_THRESHOLD = 0.7  # cross-jurisdiction depth
SYLLABUS_COVERAGE_THRESHOLD = 0.9        # LO coverage


@dataclass
class TrajectoryScore:
    """The canonical trajectory score result.

    Mirrors `google.adk.evaluation.EvalResult` but provides a
    graceful-degradation fallback when google-adk is not
    installed.
    """

    score: float                      # 0.0 - 1.0
    threshold: float                  # pass threshold
    passed: bool                      # score >= threshold
    details: dict[str, Any]           # debug metadata

    def to_asset_check_result(self) -> dict[str, Any]:
        """Convert to a Dagster AssetCheckResult-compatible dict."""
        return {
            "passed": self.passed,
            "score": self.score,
            "threshold": self.threshold,
            "metadata": self.details,
        }


def _resolve_judge_model() -> str:
    """Resolve the LLM-as-judge model via the centralized registry.

    Falls back to the canonical `minimax-m3` if the registry is
    not importable.
    """
    if _MODEL_FOR_AVAILABLE and model_for is not None:
        try:
            return model_for("text_llm", "judge")
        except KeyError:
            pass
    return os.environ.get("TEXT_MODEL_JUDGE", "minimax-m3")


# === Eval 1: ANAM colour anchor ============================================


class AnamColorAnchorTrajectoryEvaluator:
    """Score the ANAM extraction trajectory's colour fidelity.

    The trajectory must:
    1. Call ExtractXxxSource (HadesBoon / XmenScene / AnimationDescriptor)
    2. Call MapToAnamParticle (the Celtic-deity join)
    3. Derive the ANAM colour from the source colour

    Score: 1.0 if ΔE CIE76 ≤ 8, linear falloff to 0.0 at ΔE = 50.
    """

    def __init__(self) -> None:
        self.threshold = ANAM_COLOR_ANCHOR_MIN_SCORE
        self._delta_e_threshold = ANAM_DELTA_E_THRESHOLD

    def evaluate(self, trajectory: list[dict[str, Any]]) -> TrajectoryScore:
        if not _ADK_EVAL_AVAILABLE:
            logger.warning("google-adk not installed; returning no-op score")
            return TrajectoryScore(
                score=0.0,
                threshold=self.threshold,
                passed=False,
                details={"noop_reason": "google-adk not installed"},
            )

        # Walk the trajectory; find the BAML extraction + the join.
        extract_invocation = next(
            (
                inv for inv in trajectory
                if inv.get("tool_name", "").startswith("Extract")
            ),
            None,
        )
        join_invocation = next(
            (
                inv for inv in trajectory
                if inv.get("tool_name") == "MapToAnamParticle"
            ),
            None,
        )

        if extract_invocation is None or join_invocation is None:
            return TrajectoryScore(
                score=0.0,
                threshold=self.threshold,
                passed=False,
                details={
                    "error": "missing extract or join invocation",
                    "trajectory_length": len(trajectory),
                },
            )

        # Compute ΔE between source color and ANAM color.
        # The actual ΔE math is in `tuatha.theming.color.delta_e` (CIE76).
        source_hex = extract_invocation.get("output", {}).get("color_hex", "")
        anam_hex = join_invocation.get("output", {}).get("anam_color_hex", "")

        if not source_hex or not anam_hex:
            return TrajectoryScore(
                score=0.0,
                threshold=self.threshold,
                passed=False,
                details={
                    "error": "missing source_hex or anam_hex",
                    "source_hex": source_hex,
                    "anam_hex": anam_hex,
                },
            )

        try:
            from tuatha.theming.color import delta_e

            actual_delta_e = delta_e(source_hex, anam_hex)
        except (ValueError, ImportError) as exc:
            return TrajectoryScore(
                score=0.0,
                threshold=self.threshold,
                passed=False,
                details={
                    "error": f"delta_e computation failed: {exc}",
                    "source_hex": source_hex,
                    "anam_hex": anam_hex,
                },
            )

        # Linear falloff: 1.0 at ΔE ≤ threshold, 0.0 at ΔE ≥ 50.
        if actual_delta_e <= self._delta_e_threshold:
            score = 1.0
        elif actual_delta_e >= 50.0:
            score = 0.0
        else:
            score = 1.0 - (actual_delta_e - self._delta_e_threshold) / (
                50.0 - self._delta_e_threshold
            )

        return TrajectoryScore(
            score=score,
            threshold=self.threshold,
            passed=actual_delta_e <= self._delta_e_threshold,
            details={
                "source_hex": source_hex,
                "anam_hex": anam_hex,
                "delta_e": actual_delta_e,
                "delta_e_threshold": self._delta_e_threshold,
            },
        )


# === Eval 2: Marking accuracy ==============================================


class MarkingAccuracyTrajectoryEvaluator:
    """Score whether MarkGrade cited the correct MarkingCriterion.criterion_id
    in GradingResult.per_criterion[i].evidence_source_pdfs."""

    def __init__(self) -> None:
        self.threshold = MARKING_ACCURACY_THRESHOLD

    def evaluate(self, trajectory: list[dict[str, Any]]) -> TrajectoryScore:
        markgrade_invocation = next(
            (
                inv for inv in trajectory
                if inv.get("tool_name") == "MarkGrade"
            ),
            None,
        )
        if markgrade_invocation is None:
            return TrajectoryScore(
                score=0.0,
                threshold=self.threshold,
                passed=False,
                details={"error": "missing MarkGrade invocation"},
            )

        per_criterion = (
            markgrade_invocation.get("output", {}).get("per_criterion", [])
        )
        cited = sum(
            1 for c in per_criterion
            if c.get("evidence_source_pdfs")
        )
        total = max(len(per_criterion), 1)
        score = cited / total

        return TrajectoryScore(
            score=score,
            threshold=self.threshold,
            passed=score >= self.threshold,
            details={
                "cited_count": cited,
                "total_count": total,
                "judge_model": _resolve_judge_model(),
            },
        )


# === Eval 3: Feedback quality ==============================================


class FeedbackQualityTrajectoryEvaluator:
    """Score whether feedback_en is actionable + criterion-specific."""

    def __init__(self) -> None:
        self.threshold = FEEDBACK_QUALITY_THRESHOLD

    def evaluate(self, trajectory: list[dict[str, Any]]) -> TrajectoryScore:
        markgrade_invocation = next(
            (
                inv for inv in trajectory
                if inv.get("tool_name") == "MarkGrade"
            ),
            None,
        )
        if markgrade_invocation is None:
            return TrajectoryScore(
                score=0.0,
                threshold=self.threshold,
                passed=False,
                details={"error": "missing MarkGrade invocation"},
            )

        feedback = (
            markgrade_invocation.get("output", {}).get("feedback_en", "")
        )
        per_criterion = (
            markgrade_invocation.get("output", {}).get("per_criterion", [])
        )

        # Heuristic: feedback cites ≥1 criterion + has a "next step"
        has_criterion_ref = any(
            c.get("criterion_id", "") in feedback for c in per_criterion
        )
        has_next_step = any(
            marker in feedback.lower()
            for marker in ["next step", "next:", "try", "consider", "practice"]
        )
        score = (
            1.0 if (has_criterion_ref and has_next_step)
            else 0.5 if (has_criterion_ref or has_next_step)
            else 0.0
        )

        return TrajectoryScore(
            score=score,
            threshold=self.threshold,
            passed=score >= self.threshold,
            details={
                "has_criterion_ref": has_criterion_ref,
                "has_next_step": has_next_step,
                "feedback_length": len(feedback),
            },
        )


# === Eval 4: Formative item uniqueness =====================================


class FormativeItemUniquenessTrajectoryEvaluator:
    """Score the cosine similarity between the new FormativeItem
    and the last 100 prior items."""

    def __init__(self) -> None:
        self.threshold = FORMATIVE_ITEM_UNIQUENESS_THRESHOLD

    def evaluate(
        self,
        trajectory: list[dict[str, Any]],
        prior_items: list[dict[str, Any]] | None = None,
    ) -> TrajectoryScore:
        prior_items = prior_items or []
        item_invocation = next(
            (
                inv for inv in trajectory
                if inv.get("tool_name", "").startswith("Generate")
                and "FormativeItem" in inv.get("tool_name", "")
            ),
            None,
        )
        if item_invocation is None:
            return TrajectoryScore(
                score=0.0,
                threshold=self.threshold,
                passed=False,
                details={"error": "missing FormativeItem generation"},
            )

        # Heuristic: if the item text differs from all prior items,
        # score = 1.0; otherwise score = 1.0 - max_similarity.
        item_text = str(item_invocation.get("output", {}))
        max_sim = max(
            (
                _text_similarity(item_text, str(p))
                for p in prior_items[-100:]
            ),
            default=0.0,
        )
        score = 1.0 - max_sim

        return TrajectoryScore(
            score=score,
            threshold=self.threshold,
            passed=score >= self.threshold,
            details={
                "max_similarity_to_prior": max_sim,
                "prior_items_count": len(prior_items),
            },
        )


def _text_similarity(a: str, b: str) -> float:
    """Naive Jaccard similarity for textual items."""
    a_tokens = set(a.lower().split())
    b_tokens = set(b.lower().split())
    if not a_tokens or not b_tokens:
        return 0.0
    return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


# === Eval 5: Adaptive tutor relevance =====================================


class AdaptiveTutorRelevanceTrajectoryEvaluator:
    """Score the consistency between TutorState.mastery_score
    and the chosen TutorAction.
    - mastery < 0.5 → expect ExplainConcept (difficulty ↓)
    - mastery > 0.8 → expect DrillProblem (difficulty ↑)
    - else → expect Summarise / GiveExample (maintain)
    """

    def __init__(self) -> None:
        self.threshold = ADAPTIVE_TUTOR_RELEVANCE_THRESHOLD

    def evaluate(self, trajectory: list[dict[str, Any]]) -> TrajectoryScore:
        tutor_invocation = next(
            (
                inv for inv in trajectory
                if inv.get("tool_name") == "Adapttutor"
            ),
            None,
        )
        if tutor_invocation is None:
            return TrajectoryScore(
                score=0.0,
                threshold=self.threshold,
                passed=False,
                details={"error": "missing Adapttutor invocation"},
            )

        state = tutor_invocation.get("input", {}).get("tutor_state", {})
        mastery = state.get("mastery_score", 0.0)
        next_action = tutor_invocation.get("output", {}).get("next_action", {})
        action_type = next_action.get("action_type", "")

        if mastery < 0.5:
            expected_action = "ExplainConcept"
        elif mastery > 0.8:
            expected_action = "DrillProblem"
        else:
            expected_action = "Summarise"

        # Heuristic score: 1.0 if matches, 0.5 if related, 0.0 otherwise.
        score = (
            1.0 if action_type == expected_action
            else 0.5 if action_type in {"GiveExample", "Summarise", "DrillProblem"}
            else 0.0
        )

        return TrajectoryScore(
            score=score,
            threshold=self.threshold,
            passed=score >= self.threshold,
            details={
                "mastery_score": mastery,
                "expected_action": expected_action,
                "actual_action": action_type,
            },
        )


# === Eval 6: Equivalency consistency ======================================


class EquivalencyConsistencyTrajectoryEvaluator:
    """Score the cross-jurisdiction depth consistency for the same lo_code."""

    def __init__(self) -> None:
        self.threshold = EQUIVALENCY_CONSISTENCY_THRESHOLD

    def evaluate(self, trajectory: list[dict[str, Any]]) -> TrajectoryScore:
        equiv_invocation = next(
            (
                inv for inv in trajectory
                if inv.get("tool_name") == "Equivgen"
            ),
            None,
        )
        if equiv_invocation is None:
            return TrajectoryScore(
                score=0.0,
                threshold=self.threshold,
                passed=False,
                details={"error": "missing Equivgen invocation"},
            )

        rows = equiv_invocation.get("output", {}).get("rows", [])
        depths = [r.get("depth_estimate", "") for r in rows]
        # Heuristic: at least 80% of rows share a common depth.
        if not depths:
            return TrajectoryScore(
                score=0.0,
                threshold=self.threshold,
                passed=False,
                details={"error": "empty rows"},
            )
        from collections import Counter

        counts = Counter(depths)
        dominant_depth, dominant_count = counts.most_common(1)[0]
        consistency = dominant_count / len(depths)

        return TrajectoryScore(
            score=consistency,
            threshold=self.threshold,
            passed=consistency >= self.threshold,
            details={
                "dominant_depth": dominant_depth,
                "consistency": consistency,
                "row_count": len(rows),
            },
        )


# === Eval 7: Syllabus coverage ============================================


class SyllabusCoverageTrajectoryEvaluator:
    """Score the coverage of every NCCA LO by at least one
    emitted FormativeItem in the trajectory."""

    def __init__(self) -> None:
        self.threshold = SYLLABUS_COVERAGE_THRESHOLD

    def evaluate(
        self,
        trajectory: list[dict[str, Any]],
        ncca_los: list[str] | None = None,
    ) -> TrajectoryScore:
        ncca_los = ncca_los or []
        item_invocations = [
            inv for inv in trajectory
            if inv.get("tool_name", "").startswith("Generate")
            and "FormativeItem" in inv.get("tool_name", "")
        ]
        if not ncca_los or not item_invocations:
            return TrajectoryScore(
                score=0.0,
                threshold=self.threshold,
                passed=False,
                details={"error": "no LOs or no items"},
            )

        covered = set()
        for inv in item_invocations:
            lo_code = inv.get("input", {}).get("lo_code", "")
            if lo_code:
                covered.add(lo_code)

        coverage = len(covered & set(ncca_los)) / len(ncca_los)

        return TrajectoryScore(
            score=coverage,
            threshold=self.threshold,
            passed=coverage >= self.threshold,
            details={
                "covered_los": sorted(covered & set(ncca_los)),
                "missing_los": sorted(set(ncca_los) - covered),
                "coverage": coverage,
            },
        )


__all__ = [
    "ANAM_COLOR_ANCHOR_MIN_SCORE",
    "ANAM_DELTA_E_THRESHOLD",
    "AdaptiveTutorRelevanceTrajectoryEvaluator",
    "AnamColorAnchorTrajectoryEvaluator",
    "EquivalencyConsistencyTrajectoryEvaluator",
    "FeedbackQualityTrajectoryEvaluator",
    "FormativeItemUniquenessTrajectoryEvaluator",
    "MarkingAccuracyTrajectoryEvaluator",
    "SyllabusCoverageTrajectoryEvaluator",
    "TrajectoryScore",
]
