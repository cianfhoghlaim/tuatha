## MODIFIED Requirements

### Requirement: 14 NCCA + adjacent subject agents × per-subject quest packs

The system SHALL provide 14 subject agents (8 NCCA + 6 NCCA-adjacent
per the 2026-08-26 subject-expansion change), each emitting typed
BAML responses per the `qpack_<subject>.baml` contract, each
carrying an ADK agent instruction with:

1. The 5-tool decision matrix (syllabus_lookup /
   past_paper_lookup / marking_scheme_lookup /
   formative_item_generate / response_score)
2. The Evidence Ladder G7 contract (no response without
   provenance)
3. The bilingual invariant (gaeilge only — emits EN + GA,
   others emit EN only per the 2026-08-27 change)
4. The difficulty calibration guide (1-5)
5. The NCCA LO numbering reference
   (e.g. `LC-MATHS-LO-<strand>.<index>`)

#### Scenario: Subject agent emits typed BAML response

- **GIVEN** a query to any of the 14 subject agents
- **WHEN** the agent routes to one of its 5 per-subject tools
- **THEN** the tool returns a typed BAML record with
  `provenance` (`source_pdf`, `source_page`, `verbatim_text`)
- **AND** the response carries `provenance_sha256` (G7
  contract) so the Evidence Ladder is verifiable
- **AND** the response carries `lo_code` (NCCA LO numbering)
  so the response is cross-referenced to the canonical
  syllabus

### Requirement: Educational observation eval coverage via Google ADK

The system SHALL provide observation-based evaluation via
Google ADK's `TrajectoryEvaluator` surface (NOT LLM-as-judge
RAGAS), with at least these 7 trajectory evaluators wired as
Dagster `@asset_check` decorators:

1. `AnamColorAnchorTrajectoryEvaluator` — scores the ANAM
   extraction trajectory's ΔE CIE76 between source colour and
   derived ANAM colour (threshold ≤ 8)
2. `MarkingAccuracyTrajectoryEvaluator` — scores whether the
   `MarkGrade` BAML function cited the correct
   `MarkingCriterion.criterion_id` in
   `GradingResult.per_criterion[i].evidence_source_pdfs`
3. `FeedbackQualityTrajectoryEvaluator` — scores whether the
   `feedback_en` is actionable + criterion-specific
4. `FormativeItemUniquenessTrajectoryEvaluator` — scores the
   cosine similarity between the new `FormativeItem` and the
   last 100 prior items
5. `AdaptiveTutorRelevanceTrajectoryEvaluator` — scores the
   consistency between `TutorState.mastery_score` and the
   chosen `TutorAction`
6. `EquivalencyConsistencyTrajectoryEvaluator` — scores the
   cross-jurisdiction depth consistency for the same `lo_code`
7. `SyllabusCoverageTrajectoryEvaluator` — scores the
   coverage of every NCCA LO by at least one emitted
   `FormativeItem` in the trajectory

#### Scenario: Eval trajectory runs end-to-end

- **GIVEN** the `tuatha/dagster/observation/eval_sets/anam.yaml`
  with 3 eval cases (one per ANAM source: hades_boons,
  xmen_powers, avatar_elemental_bending)
- **WHEN** `google.adk.evaluation.AgentEvaluator.run_eval(...)`
  is invoked via the `eval_runner.py` wrapper
- **THEN** the trajectory is emitted as an OpenTelemetry span
  to the Langfuse backend (`langfuse.cianfhoghlaim.ie`) via
  the `otel_langfuse_bridge.py` module
- **AND** each `TrajectoryEvaluator` returns a score in
  `[0.0, 1.0]`
- **AND** the Dagster `@asset_check` reports the score vs the
  threshold
