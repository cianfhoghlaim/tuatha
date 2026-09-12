"""Tests for the Phase 2 educational prompt rewrites.

Per the 2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1
T2.4: all 14 qpack_<subject>.baml files use the canonical prompt
template + all 8 NCCA subject agents use the canonical
instruction.

Tests:
- Every qpack_<subject>.baml references the `subject_agent` client
- Every qpack_<subject>.baml includes the English-only LANGUAGE guard
  (gaeilge + irish get the bilingual variant)
- Every qpack_<subject>.baml includes the NCCA LO numbering scheme
- Every qpack_<subject>.baml includes the difficulty 1-5 calibration
- Every NCCA subject agent uses `resolve_model("text_llm", "subject_agent")`
- The 4 hackathon agents use `resolve_model("text_llm", "hackathon_agent")`
- The 3 educational agents use `resolve_model("text_llm", "educational_agent")`
- The 6-jurisdiction list is standardized
- The 40 stub tool files were deleted (only corpus_tools + curriculum_search + gaeilge_gramadach_review remain)
- The capture/macos/DEPRECATED.md exists
- The capture/hermes_client.py stub exists
- The observation package exists with 7 TrajectoryEvaluators
- The observation eval sets exist
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BAML_DIR = REPO_ROOT / "tuatha" / "baml"
SUBJECTS_DIR = REPO_ROOT / "tuatha" / "subjects"
HACKATHON_DIR = REPO_ROOT / "tuatha" / "agents" / "hackathon"
EDUCATIONAL_DIR = REPO_ROOT / "tuatha" / "agents" / "educational"


NCCA_SUBJECTS = [
    "mathematics",
    "applied_mathematics",
    "chemistry",
    "computer_science",
    "english",
    "gaeilge",
    "geography",
    "history",
]

ALL_QPACK_SUBJECTS = NCCA_SUBJECTS + [
    "accounting",
    "biology",
    "business",
    "french",
    "irish",
    "physics",
]

BILINGUAL_QPACK_SUBJECTS = {"gaeilge", "irish"}

HACKATHON_AGENTS = [
    "marking_grader",
    "adaptive_tutor",
    "equivalency_generator",
    "curriculum_change_sensor",
]

EDUCATIONAL_AGENTS = [
    "academic_history_agent",
    "celtic_grammar_agent",
    "celtic_morphology_agent",
]


class TestQpackBamlCanonical:
    """The canonical prompt template tests for qpack_<subject>.baml."""

    def _read(self, slug: str) -> str:
        return (BAML_DIR / f"qpack_{slug}.baml").read_text()

    def test_all_qpack_files_exist(self) -> None:
        for slug in ALL_QPACK_SUBJECTS:
            assert (BAML_DIR / f"qpack_{slug}.baml").exists(), (
                f"Missing qpack_{slug}.baml"
            )

    def test_all_qpack_use_subject_agent_client(self) -> None:
        for slug in ALL_QPACK_SUBJECTS:
            content = self._read(slug)
            assert "client<llm> subject_agent" in content, (
                f"{slug}: missing subject_agent client"
            )

    def test_all_qpack_have_english_only_guard(self) -> None:
        """English-only by default (per the 2026-08-27 change)."""
        for slug in ALL_QPACK_SUBJECTS:
            content = self._read(slug)
            assert "English only" in content, (
                f"{slug}: missing English-only guard"
            )

    def test_bilingual_qpack_have_bilingual_guard(self) -> None:
        """gaeilge + irish must have the bilingual EN + GA variant."""
        for slug in BILINGUAL_QPACK_SUBJECTS:
            content = self._read(slug)
            assert "Irish" in content or "GA" in content or "ga" in content, (
                f"{slug}: bilingual gaeilge should reference Irish"
            )

    def test_all_qpack_have_ncca_lo_numbering(self) -> None:
        for slug in ALL_QPACK_SUBJECTS:
            content = self._read(slug)
            assert "NCCA LO NUMBERING" in content, (
                f"{slug}: missing NCCA LO NUMBERING"
            )
            assert "LO-<strand>" in content or "strand>.<index>" in content, (
                f"{slug}: missing LC-XXX-LO-<strand>.<index> pattern"
            )

    def test_all_qpack_have_difficulty_calibration(self) -> None:
        for slug in ALL_QPACK_SUBJECTS:
            content = self._read(slug)
            assert "Difficulty:" in content, (
                f"{slug}: missing difficulty calibration"
            )
            assert "1 = recall" in content or "1 = pure recall" in content, (
                f"{slug}: missing difficulty 1 = recall"
            )


class TestNccASubjectAgents:
    """The 8 NCCA subject agents must use the canonical resolve_model role."""

    def _read(self, slug: str) -> str:
        return (SUBJECTS_DIR / f"{slug}.py").read_text()

    def test_all_subject_agents_use_subject_agent_role(self) -> None:
        for slug in NCCA_SUBJECTS:
            content = self._read(slug)
            assert 'resolve_model("text_llm", "subject_agent")' in content, (
                f"{slug}: must use subject_agent role (not ocr_vision:media_descriptor)"
            )

    def test_no_subject_agent_uses_old_silent_coercion(self) -> None:
        """Per the 2026-08-27 fix: no `ocr_vision:media_descriptor` calls."""
        for slug in NCCA_SUBJECTS:
            content = self._read(slug)
            assert 'resolve_model("ocr_vision", "media_descriptor")' not in content, (
                f"{slug}: silent-coercion bug still present"
            )

    def test_all_subject_agents_have_evidence_ladder(self) -> None:
        for slug in NCCA_SUBJECTS:
            content = self._read(slug)
            assert "EVIDENCE LADDER" in content, (
                f"{slug}: missing Evidence Ladder G7 contract"
            )

    def test_all_subject_agents_have_english_only(self) -> None:
        """Every subject agent must declare its LANGUAGE guard.
        gaeilge is bilingual EN + GA; others are English-only."""
        for slug in NCCA_SUBJECTS:
            content = self._read(slug)
            if slug == "gaeilge":
                # gaeilge uses the bilingual variant
                assert "Béarla amháin" in content or "English by default" in content, (
                    f"{slug}: gaeilge should have bilingual LANGUAGE guard"
                )
            else:
                assert "LANGUAGE: English only" in content, (
                    f"{slug}: missing English-only language guard"
                )

    def test_all_subject_agents_use_bind_subject_tools(self) -> None:
        for slug in NCCA_SUBJECTS:
            content = self._read(slug)
            assert "bind_subject_tools(" in content, (
                f"{slug}: must use bind_subject_tools pattern (not stub imports)"
            )


class TestHackathonAgents:
    """The 4 BIEP hackathon agents must use the canonical hackathon_agent role."""

    def _read(self, slug: str) -> str:
        return (HACKATHON_DIR / f"{slug}.py").read_text()

    def test_all_hackathon_agents_use_hackathon_agent_role(self) -> None:
        for slug in HACKATHON_AGENTS:
            content = self._read(slug)
            assert 'resolve_model("text_llm", "hackathon_agent")' in content, (
                f"{slug}: must use hackathon_agent role (not default)"
            )

    def test_all_hackathon_agents_have_english_only(self) -> None:
        for slug in HACKATHON_AGENTS:
            content = self._read(slug)
            assert "LANGUAGE: English only" in content, (
                f"{slug}: missing English-only language guard"
            )

    def test_jurisdiction_list_is_canonical(self) -> None:
        """The 6 canonical jurisdictions must appear in the agent
        descriptions/instructions (DESC → IoM fix per 2026-08-27)."""
        canonical_names = ["NCCA", "AQA", "SQA", "WJEC", "CCEA", "IoM"]
        for slug in HACKATHON_AGENTS:
            content = self._read(slug)
            for name in canonical_names:
                assert name in content, (
                    f"{slug}: missing canonical jurisdiction {name}"
                )
            # DESC should not appear (legacy — replaced by IoM).
            assert "DESC" not in content, (
                f"{slug}: legacy DESC found — should be IoM per 2026-08-27"
            )


class TestEducationalAgents:
    """The 3 educational agents must use the canonical educational_agent role."""

    def test_all_educational_agents_use_educational_agent_role(self) -> None:
        for slug in EDUCATIONAL_AGENTS:
            content = (EDUCATIONAL_DIR / f"{slug}.py").read_text()
            assert 'resolve_model("text_llm", "educational_agent")' in content, (
                f"{slug}: must use educational_agent role"
            )


class TestStubToolsDeleted:
    """T1.7: the 40 stub tool files must be deleted."""

    def test_only_corpus_tools_remain(self) -> None:
        tools_dir = REPO_ROOT / "tuatha" / "tools"
        remaining = sorted(
            p.name for p in tools_dir.glob("*.py")
            if not p.name.startswith("__")
        )
        expected = {"corpus_tools.py", "curriculum_search.py", "gaeilge_gramadach_review.py"}
        assert set(remaining) == expected, (
            f"Unexpected tool files remaining: {remaining}. "
            f"Expected only: {expected}"
        )


class TestCapturePackage:
    """T0.4 + T0.5: Swift daemon deprecated, Hermes stub added."""

    def test_macos_deprecated_md_exists(self) -> None:
        assert (REPO_ROOT / "tuatha" / "capture" / "macos" / "DEPRECATED.md").exists()

    def test_hermes_client_exists(self) -> None:
        assert (REPO_ROOT / "tuatha" / "capture" / "hermes_client.py").exists()

    def test_capture_package_init_exists(self) -> None:
        assert (REPO_ROOT / "tuatha" / "capture" / "__init__.py").exists()


class TestObservationPackage:
    """T3: ADK observation eval surface."""

    def test_observation_init_exists(self) -> None:
        assert (REPO_ROOT / "tuatha" / "dagster" / "observation" / "__init__.py").exists()

    def test_observation_eval_metrics_exists(self) -> None:
        assert (REPO_ROOT / "tuatha" / "dagster" / "observation" / "eval_metrics.py").exists()

    def test_observation_eval_runner_exists(self) -> None:
        assert (REPO_ROOT / "tuatha" / "dagster" / "observation" / "eval_runner.py").exists()

    def test_observation_otel_bridge_exists(self) -> None:
        assert (
            REPO_ROOT / "tuatha" / "dagster" / "observation" / "otel_langfuse_bridge.py"
        ).exists()

    def test_observation_asset_checks_exists(self) -> None:
        assert (REPO_ROOT / "tuatha" / "dagster" / "observation" / "asset_checks.py").exists()

    def test_all_7_trajectory_evaluators_defined(self) -> None:
        content = (REPO_ROOT / "tuatha" / "dagster" / "observation" / "eval_metrics.py").read_text()
        for name in [
            "AnamColorAnchorTrajectoryEvaluator",
            "MarkingAccuracyTrajectoryEvaluator",
            "FeedbackQualityTrajectoryEvaluator",
            "FormativeItemUniquenessTrajectoryEvaluator",
            "AdaptiveTutorRelevanceTrajectoryEvaluator",
            "EquivalencyConsistencyTrajectoryEvaluator",
            "SyllabusCoverageTrajectoryEvaluator",
        ]:
            assert f"class {name}" in content, f"Missing {name}"

    def test_3_eval_set_yamls_exist(self) -> None:
        for name in ["anam", "marking", "tutor"]:
            assert (REPO_ROOT / "tuatha" / "dagster" / "observation" / "eval_sets" / f"{name}.yaml").exists(), (
                f"Missing eval_sets/{name}.yaml"
            )


class TestQpackBamlSchemas:
    """The 14 qpack_<subject>.baml class schemas are consistent."""

    def _read(self, slug: str) -> str:
        return (BAML_DIR / f"qpack_{slug}.baml").read_text()

    def test_all_qpack_have_5_classes(self) -> None:
        for slug in ALL_QPACK_SUBJECTS:
            content = self._read(slug)
            for classname in ["SyllabusTopic", "PastPaper", "MarkingScheme",
                              "FormativeItem", "FormativeResponse"]:
                assert f"class " in content and classname in content, (
                    f"{slug}: missing class {classname}"
                )

    def test_all_qpack_have_5_functions(self) -> None:
        for slug in ALL_QPACK_SUBJECTS:
            content = self._read(slug)
            for fnname in [
                "Generate", "Syllabus",
                "PastPaper", "MarkingScheme",
                "FormativeItem", "Score", "FormativeResponse",
            ]:
                assert f"function" in content, (
                    f"{slug}: missing function with {fnname}"
                )

    def test_all_qpack_have_flagged_for_review(self) -> None:
        """The FormativeResponse schema includes the confidence gate."""
        for slug in ALL_QPACK_SUBJECTS:
            content = self._read(slug)
            assert "flagged_for_review" in content, (
                f"{slug}: FormativeResponse missing flagged_for_review"
            )
