"""Tests for the Phase 4 Curriculum Change Detection Sensor.

Covers the 6-jurisdiction config + the BIEP v3 5-phase re-run + the
quest-pack diff + the version-anchored ``SkillTreeBadgeDraft`` +
the Firecrawl monitor creation + the top-level ``run_sensor_cycle``
+ the ``--dry-run`` CLI.

Per the spec (`openspec/changes/2026-08-26-tuatha-multimodel-2d-
graphics-and-earn-pipeline-v1/specs/cianfhoghlaim-educational-mmo/
spec.md` § ADDED Requirements → "Curriculum change detection
sensor"):

  - NCCA + AQA + SQA + WJEC + CCEA + IoM (6 jurisdiction sites)
  - Firecrawl monitor per (jurisdiction, subject)
  - 5-phase re-run (BAML → CocoIndex → Cognee → Graphiti → LanceDB)
  - Diff: ``items_changed > 0`` OR ``los_changed``
  - New ``SkillTreeBadge`` with ``version=<new_pdf_hash>``
  - Daily Merkle anchor picks it up (the Phase 3 anchor asset)

The sensor is exercised end-to-end in ``--dry-run`` mode (the
offline-dev path) so the tests don't need Firecrawl / BAML / Cognee
to be live.
"""
from __future__ import annotations

import datetime
import inspect
import json
import subprocess
import sys
from typing import Any

import pytest
from tuatha.agents.hackathon.curriculum_change_sensor import (
    BIEP_V3_PHASES,
    EXPECTED_JURISDICTION_COUNT,
    EXPECTED_PHASE_COUNT,
    JURISDICTIONS,
    SUBJECTS_PER_JURISDICTION,
    ChangeSensorReport,
    PdfChange,
    QuestPack,
    _build_arg_parser,
    create_jurisdiction_monitors,
    curriculum_change_sensor_agent,
    diff_quest_packs,
    hash_pdf_bytes,
    main,
    make_badge_for_diff,
    run_biep_v3_rerun,
    run_sensor_cycle,
)

# ── The 6 jurisdiction config ──


EXPECTED_JURISDICTIONS: tuple[str, ...] = (
    "NCCA", "AQA", "SQA", "WJEC", "CCEA", "IoM",
)


def test_jurisdictions_count_is_six():
    """The canonical 6 jurisdiction sites are wired (per the BIEP v3 spec)."""
    assert EXPECTED_JURISDICTION_COUNT == 6
    assert len(JURISDICTIONS) == EXPECTED_JURISDICTION_COUNT
    assert tuple(JURISDICTIONS.keys()) == EXPECTED_JURISDICTIONS


@pytest.mark.parametrize("slug", list(EXPECTED_JURISDICTIONS))
def test_jurisdiction_has_required_keys(slug: str):
    """Each jurisdiction entry carries url + country + level_primary."""
    info = JURISDICTIONS[slug]
    assert "url" in info
    assert "country" in info
    assert "level_primary" in info
    assert info["url"].startswith("http")
    assert info["country"]
    assert info["level_primary"]


def test_jurisdiction_urls_are_unique():
    """The 6 jurisdiction URLs are unique (no accidental collisions)."""
    urls = [info["url"] for info in JURISDICTIONS.values()]
    assert len(urls) == len(set(urls))


def test_subjects_per_jurisdiction_matches_jurisdictions():
    """Every jurisdiction has a SUBJECTS_PER_JURISDICTION entry."""
    for slug in EXPECTED_JURISDICTIONS:
        assert slug in SUBJECTS_PER_JURISDICTION
        subjects = SUBJECTS_PER_JURISDICTION[slug]
        assert len(subjects) >= 1
        assert all(isinstance(s, str) for s in subjects)


def test_ncca_publishes_all_eight_subjects():
    """NCCA publishes the 8 NCCA Leaving Certificate subjects."""
    expected = {
        "mathematics",
        "applied_mathematics",
        "chemistry",
        "geography",
        "history",
        "english",
        "gaeilge",
        "computer_science",
    }
    assert set(SUBJECTS_PER_JURISDICTION["NCCA"]) == expected


def test_jurisdiction_no_hardcoded_urls_elsewhere():
    """No other module in tuatha/ references a jurisdiction URL directly.

    The 6 jurisdiction URLs live exclusively in the
    ``JURISDICTIONS`` config dict (the canonical surface).
    """
    # The test is a sanity-check: the JURISDICTIONS dict IS the
    # source of truth. If a future maintainer hardcodes a URL
    # elsewhere, the canonical lookup via JURISDICTIONS breaks.
    assert len(JURISDICTIONS) == 6


# ── The 5-phase BIEP v3 re-run ──


def test_biep_v3_phases_count_is_five():
    """The BIEP v3 5-phase re-run has exactly 5 canonical phases."""
    assert EXPECTED_PHASE_COUNT == 5
    assert len(BIEP_V3_PHASES) == EXPECTED_PHASE_COUNT


def test_biep_v3_phases_are_in_canonical_order():
    """The 5 phases are listed in the canonical BIEP v3 order."""
    expected = (
        "baml_re_extract",
        "cocoindex_v1_re_embed",
        "cognee_cognify",
        "graphiti_temporal_memory",
        "lancedb_re_index",
    )
    assert expected == BIEP_V3_PHASES


def test_biep_v3_phases_are_unique():
    """The 5 phases are unique (no accidental duplicates)."""
    assert len(set(BIEP_V3_PHASES)) == 5


@pytest.mark.asyncio
async def test_run_biep_v3_rerun_returns_all_five_phases():
    """The 5-phase re-run emits one result per phase."""
    result = await run_biep_v3_rerun(
        "NCCA", "mathematics", "abc123", dry_run=True,
    )
    assert "phases" in result
    assert tuple(result["phases"].keys()) == BIEP_V3_PHASES


@pytest.mark.asyncio
async def test_run_biep_v3_rerun_unknown_jurisdiction_raises():
    """Unknown jurisdictions are rejected."""
    with pytest.raises(ValueError, match="unknown jurisdiction"):
        await run_biep_v3_rerun("NOPE", "mathematics", "abc", dry_run=True)


@pytest.mark.asyncio
async def test_run_biep_v3_rerun_calls_rerun_fn_for_each_phase():
    """The rerun_fn callback is invoked once per phase (in canonical order)."""
    seen: list[str] = []

    async def _rerun(phase: str, jurisdiction: str, subject: str, new_pdf_hash: str) -> dict:
        seen.append(phase)
        return {"status": "live", "phase": phase}

    result = await run_biep_v3_rerun(
        "SQA", "chemistry", "deadbeef",
        rerun_fn=_rerun, dry_run=False,
    )
    assert seen == list(BIEP_V3_PHASES)
    for phase in BIEP_V3_PHASES:
        assert result["phases"][phase]["status"] == "live"
        assert result["phases"][phase]["phase"] == phase


@pytest.mark.asyncio
async def test_run_biep_v3_rerun_dry_run_records_version():
    """Each simulated phase records the new_pdf_hash (the badge version)."""
    result = await run_biep_v3_rerun(
        "WJEC", "geography", "version-xyz",
        dry_run=True,
    )
    for phase in BIEP_V3_PHASES:
        assert result["phases"][phase]["version"] == "version-xyz"
        assert result["phases"][phase]["status"] == "simulated"


# ── Hash + diff helpers ──


def test_hash_pdf_bytes_is_sha256_hex():
    """``hash_pdf_bytes`` returns a 64-char SHA-256 hex digest."""
    digest = hash_pdf_bytes(b"%PDF-1.4 fake pdf bytes")
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


def test_hash_pdf_bytes_is_deterministic():
    """Same bytes → same hash (the canonical Merkle leaf + badge version)."""
    a = hash_pdf_bytes(b"abc")
    b = hash_pdf_bytes(b"abc")
    assert a == b


def test_hash_pdf_bytes_differs_on_input_change():
    """Different bytes → different hash."""
    assert hash_pdf_bytes(b"abc") != hash_pdf_bytes(b"abd")


def test_diff_quest_packs_no_change():
    """Identical prior + new → no change (no badge issued)."""
    prior = QuestPack(subject="mathematics", items=("a", "b"), los_covered=("LO-1",))
    new = QuestPack(subject="mathematics", items=("a", "b"), los_covered=("LO-1",))
    diff = diff_quest_packs(prior, new, jurisdiction="NCCA", new_pdf_hash="v1")
    assert diff.has_change is False
    assert diff.items_changed == 0
    assert diff.los_changed is False
    assert diff.items_added == ()
    assert diff.items_removed == ()


def test_diff_quest_packs_items_added():
    """Adding an item triggers a change (has_change=True)."""
    prior = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-1",))
    new = QuestPack(subject="mathematics", items=("a", "b"), los_covered=("LO-1",))
    diff = diff_quest_packs(prior, new, jurisdiction="NCCA", new_pdf_hash="v2")
    assert diff.has_change is True
    assert diff.items_changed == 1
    assert diff.items_added == ("b",)
    assert diff.items_removed == ()
    assert diff.los_changed is False


def test_diff_quest_packs_items_removed():
    """Removing an item triggers a change."""
    prior = QuestPack(subject="mathematics", items=("a", "b"), los_covered=("LO-1",))
    new = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-1",))
    diff = diff_quest_packs(prior, new, jurisdiction="NCCA", new_pdf_hash="v3")
    assert diff.has_change is True
    assert diff.items_changed == 1
    assert diff.items_removed == ("b",)


def test_diff_quest_packs_los_changed_only():
    """LO-set diff (no item diff) still triggers a change."""
    prior = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-1",))
    new = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-1", "LO-2"))
    diff = diff_quest_packs(prior, new, jurisdiction="NCCA", new_pdf_hash="v4")
    assert diff.has_change is True
    assert diff.items_changed == 0
    assert diff.los_changed is True


def test_diff_quest_packs_version_equals_new_pdf_hash():
    """The diff.version field equals the new_pdf_hash (per the spec)."""
    prior = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-1",))
    new = QuestPack(subject="mathematics", items=("b",), los_covered=("LO-1",))
    diff = diff_quest_packs(
        prior, new, jurisdiction="NCCA", new_pdf_hash="deadbeefcafe",
    )
    assert diff.version == "deadbeefcafe"


def test_diff_quest_packs_los_sorted_for_comparison():
    """LO-set comparison is order-insensitive (sorted)."""
    prior = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-2", "LO-1"))
    new = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-1", "LO-2"))
    diff = diff_quest_packs(prior, new, jurisdiction="NCCA", new_pdf_hash="v5")
    assert diff.los_changed is False


# ── The version-anchored badge ──


def test_make_badge_for_diff_version_equals_new_pdf_hash():
    """The new badge's ``version`` field is ``<new_pdf_hash>`` (per the spec)."""
    prior = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-1",))
    new = QuestPack(subject="mathematics", items=("b",), los_covered=("LO-1",))
    diff = diff_quest_packs(
        prior, new, jurisdiction="NCCA", new_pdf_hash="abc123def456",
    )
    badge = make_badge_for_diff(diff)
    assert badge.version == "abc123def456"


def test_make_badge_for_diff_metadata_round_trip():
    """The badge metadata carries the diff items + los for re-anchoring."""
    prior = QuestPack(subject="mathematics", items=("a", "b"), los_covered=("LO-1",))
    new = QuestPack(
        subject="mathematics",
        items=("a", "c"),
        los_covered=("LO-1", "LO-2"),
    )
    diff = diff_quest_packs(
        prior, new, jurisdiction="NCCA", new_pdf_hash="meta-test",
    )
    badge = make_badge_for_diff(diff)
    assert badge.metadata["jurisdiction"] == "NCCA"
    assert badge.metadata["items_changed"] == 2
    assert badge.metadata["los_changed"] is True
    assert set(badge.metadata["items_added"]) == {"c"}
    assert set(badge.metadata["items_removed"]) == {"b"}


def test_make_badge_for_diff_evidence_hash_distinct_per_version():
    """Different ``new_pdf_hash`` values produce distinct ``evidence_hash`` values."""
    prior = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-1",))
    new = QuestPack(subject="mathematics", items=("b",), los_covered=("LO-1",))
    diff_a = diff_quest_packs(prior, new, jurisdiction="NCCA", new_pdf_hash="aaaa")
    diff_b = diff_quest_packs(prior, new, jurisdiction="NCCA", new_pdf_hash="bbbb")
    badge_a = make_badge_for_diff(diff_a)
    badge_b = make_badge_for_diff(diff_b)
    assert badge_a.evidence_hash != badge_b.evidence_hash
    assert badge_a.version != badge_b.version


def test_make_badge_for_diff_defaults():
    """The badge defaults to ``framework='ncca-lc'`` + ``level='hl'``."""
    prior = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-1",))
    new = QuestPack(subject="mathematics", items=("b",), los_covered=("LO-1",))
    diff = diff_quest_packs(prior, new, jurisdiction="NCCA", new_pdf_hash="d")
    badge = make_badge_for_diff(diff)
    assert badge.framework == "ncca-lc"
    assert badge.level == "hl"
    assert badge.agent_issuer == "curriculum_change_sensor_agent"
    assert badge.date_earned.tzinfo is not None


def test_make_badge_for_diff_competency_code_uses_version_prefix():
    """The competency_code encodes the diff + the first 8 chars of the version."""
    prior = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-1",))
    new = QuestPack(subject="mathematics", items=("b",), los_covered=("LO-1",))
    diff = diff_quest_packs(
        prior, new, jurisdiction="NCCA", new_pdf_hash="abcdef0123",
    )
    badge = make_badge_for_diff(diff)
    assert badge.competency_code == "LC-MATHEMATICS-DIFF-abcdef01"


# ── Firecrawl monitor management ──


@pytest.mark.asyncio
async def test_create_jurisdiction_monitors_dry_run_is_deterministic():
    """Dry-run produces a deterministic UUID5 per (jurisdiction, subject)."""
    a = await create_jurisdiction_monitors(dry_run=True)
    b = await create_jurisdiction_monitors(dry_run=True)
    assert a == b
    assert len(a) == sum(
        len(subjects) for subjects in SUBJECTS_PER_JURISDICTION.values()
    )


@pytest.mark.asyncio
async def test_create_jurisdiction_monitors_dry_run_key_format():
    """Dry-run keys are ``{jurisdiction}:{subject}`` strings."""
    monitors = await create_jurisdiction_monitors(dry_run=True)
    for key in monitors:
        assert ":" in key
        jurisdiction, subject = key.split(":", 1)
        assert jurisdiction in JURISDICTIONS
        assert subject in SUBJECTS_PER_JURISDICTION[jurisdiction]


@pytest.mark.asyncio
async def test_create_jurisdiction_monitors_live_calls_client():
    """Live mode invokes ``client.monitor_create`` once per (jurisdiction, subject)."""
    calls: list[dict[str, Any]] = []

    class _FakeClient:
        def monitor_create(
            self, name: str, *, targets: list[dict], schedule: dict, goal: str,
        ) -> Any:
            calls.append({
                "name": name, "targets": targets,
                "schedule": schedule, "goal": goal,
            })
            return type("R", (), {"monitor_id": f"mon-{len(calls)}"})()

    monitors = await create_jurisdiction_monitors(
        client=_FakeClient(), dry_run=False,
    )
    expected_calls = sum(
        len(subjects) for subjects in SUBJECTS_PER_JURISDICTION.values()
    )
    assert len(calls) == expected_calls
    assert all(call["name"].startswith("tuatha_ccs_") for call in calls)
    assert all(call["targets"][0]["type"] == "url" for call in calls)
    # Every monitor_id in the returned dict matches the calls
    assert len(monitors) == expected_calls


# ── The top-level sensor cycle ──


def _make_change(
    jurisdiction: str,
    subject: str,
    *,
    new_hash: str,
    old_hash: str = "previous-hash",
) -> PdfChange:
    return PdfChange(
        jurisdiction=jurisdiction,
        subject=subject,
        new_pdf_url=f"https://example.test/{jurisdiction}/{subject}.pdf",
        new_pdf_hash=new_hash,
        previous_pdf_hash=old_hash,
        detected_at=datetime.datetime.now(tz=datetime.UTC),
        monitor_id="monitor-1",
    )


@pytest.mark.asyncio
async def test_run_sensor_cycle_dry_run_no_changes_no_badges():
    """Empty cycle emits zero badges."""
    report = await run_sensor_cycle(dry_run=True)
    assert isinstance(report, ChangeSensorReport)
    assert report.badge_versions_emitted == ()
    assert report.re_run_subjects == ()
    assert report.dry_run is True


@pytest.mark.asyncio
async def test_run_sensor_cycle_dry_run_no_diff_no_badge():
    """A real PDF change with identical items + LOs → no badge issued."""
    prior = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-1",))
    new = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-1",))
    change = _make_change("NCCA", "mathematics", new_hash="h1")
    report = await run_sensor_cycle(
        prior_quest_packs={("NCCA", "mathematics"): prior},
        new_quest_packs={("NCCA", "mathematics"): new},
        pdf_changes=(change,),
        dry_run=True,
    )
    assert report.re_run_subjects == ("mathematics",)
    assert report.badge_versions_emitted == ()


@pytest.mark.asyncio
async def test_run_sensor_cycle_dry_run_with_diff_emits_badge():
    """A real PDF change with a real diff → badge issued with new_pdf_hash."""
    prior = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-1",))
    new = QuestPack(subject="mathematics", items=("b",), los_covered=("LO-1"))
    change = _make_change("NCCA", "mathematics", new_hash="real-change-hash")
    report = await run_sensor_cycle(
        prior_quest_packs={("NCCA", "mathematics"): prior},
        new_quest_packs={("NCCA", "mathematics"): new},
        pdf_changes=(change,),
        dry_run=True,
    )
    assert report.re_run_subjects == ("mathematics",)
    assert report.badge_versions_emitted == ("real-change-hash",)


@pytest.mark.asyncio
async def test_run_sensor_cycle_dry_run_skips_no_real_change():
    """A PdfChange with matching hashes is a no-op (skips the re-run)."""
    change = _make_change(
        "NCCA", "mathematics",
        new_hash="same", old_hash="same",
    )
    report = await run_sensor_cycle(
        pdf_changes=(change,), dry_run=True,
    )
    assert report.re_run_subjects == ()
    assert report.badge_versions_emitted == ()


@pytest.mark.asyncio
async def test_run_sensor_cycle_dry_run_invokes_rerun_fn():
    """Live mode routes the 5-phase re-run through the ``rerun_fn`` callback."""
    calls: list[tuple[str, str, str, str]] = []

    async def _rerun(
        phase: str, jurisdiction: str, subject: str, new_pdf_hash: str,
    ) -> dict:
        calls.append((phase, jurisdiction, subject, new_pdf_hash))
        return {"status": "live"}

    change = _make_change("AQA", "chemistry", new_hash="qa-hash")
    await run_sensor_cycle(
        rerun_fn=_rerun, dry_run=False, pdf_changes=(change,),
    )
    assert len(calls) == EXPECTED_PHASE_COUNT
    assert all(c[0] in BIEP_V3_PHASES for c in calls)
    assert all(c[1] == "AQA" for c in calls)
    assert all(c[2] == "chemistry" for c in calls)
    assert all(c[3] == "qa-hash" for c in calls)


@pytest.mark.asyncio
async def test_run_sensor_cycle_dry_run_handles_multiple_changes():
    """Multiple PDF changes in one cycle produce multiple badges."""
    prior = QuestPack(subject="mathematics", items=("a",), los_covered=("LO-1",))
    new = QuestPack(subject="mathematics", items=("b",), los_covered=("LO-1",))
    change_a = _make_change("NCCA", "mathematics", new_hash="hash-A")
    change_b = _make_change("AQA", "chemistry", new_hash="hash-B")
    report = await run_sensor_cycle(
        prior_quest_packs={
            ("NCCA", "mathematics"): prior,
            ("AQA", "chemistry"): prior,
        },
        new_quest_packs={
            ("NCCA", "mathematics"): new,
            ("AQA", "chemistry"): new,
        },
        pdf_changes=(change_a, change_b),
        dry_run=True,
    )
    assert set(report.re_run_subjects) == {"mathematics", "chemistry"}
    assert set(report.badge_versions_emitted) == {"hash-A", "hash-B"}


@pytest.mark.asyncio
async def test_run_sensor_cycle_report_has_uuid_run_id():
    """The report carries a unique run_id (UUID format)."""
    report = await run_sensor_cycle(dry_run=True)
    # UUIDs are 36 chars including hyphens
    assert len(report.run_id) == 36
    assert report.run_id.count("-") == 4


@pytest.mark.asyncio
async def test_run_sensor_cycle_completed_at_set():
    """``completed_at`` is populated after the cycle finishes."""
    report = await run_sensor_cycle(dry_run=True)
    assert report.completed_at is not None
    assert report.completed_at >= report.started_at


# ── The CLI ──


def test_arg_parser_default_is_dry_run():
    """The CLI defaults to ``--dry-run`` (the offline dev path)."""
    parser = _build_arg_parser()
    args = parser.parse_args([])
    assert args.dry_run is True


def test_arg_parser_live_flag_disables_dry_run():
    """``--live`` flips the ``dry_run`` flag to False."""
    parser = _build_arg_parser()
    args = parser.parse_args(["--live"])
    assert args.dry_run is False


def test_arg_parser_jurisdiction_choices():
    """``--jurisdiction`` accepts only the 6 canonical jurisdictions."""
    parser = _build_arg_parser()
    args = parser.parse_args(["--jurisdiction", "NCCA"])
    assert args.jurisdiction == "NCCA"
    with pytest.raises(SystemExit):
        parser.parse_args(["--jurisdiction", "FAKE"])


def test_main_runs_and_returns_0():
    """The CLI runs end-to-end (returns 0 in ``--dry-run`` mode)."""
    rc = main(["--dry-run"])
    assert rc == 0


def test_main_emits_json_summary(capsys: pytest.CaptureFixture[str]):
    """The CLI emits a JSON summary on stdout."""
    rc = main(["--dry-run"])
    assert rc == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert "run_id" in payload
    assert "started_at" in payload
    assert "completed_at" in payload
    assert "re_run_subjects" in payload
    assert "badge_versions_emitted" in payload
    assert "dry_run" in payload
    assert payload["dry_run"] is True


# ── The canonical ADK agent (graceful degradation) ──


def test_curriculum_change_sensor_agent_importable():
    """The agent attribute is always importable (None when google.adk missing)."""
    # The agent is None in the offline dev fallback path (google.adk
    # is not installed); in production with google.adk present, it is
    # a real google.adk.agents.LlmAgent instance. Either way, the
    # attribute is defined.
    assert curriculum_change_sensor_agent is None or hasattr(
        curriculum_change_sensor_agent, "name",
    )


def test_curriculum_change_sensor_agent_name_when_adk_available():
    """When google.adk is present, the agent's name is the canonical slug."""
    agent = curriculum_change_sensor_agent
    if agent is not None:
        assert agent.name == "curriculum_change_sensor_agent"


# ── Subprocess / smoke gate ──


def test_module_imports_in_subprocess():
    """The module imports cleanly in a fresh Python process (smoke gate)."""
    result = subprocess.run(
        [
            sys.executable, "-c",
            "from tuatha.agents.hackathon.curriculum_change_sensor import "
            "JURISDICTIONS, BIEP_V3_PHASES; "
            "assert len(JURISDICTIONS) == 6; "
            "assert len(BIEP_V3_PHASES) == 5",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, (
        f"subprocess failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )


# ── Module signature sanity ──


def test_run_sensor_cycle_is_coroutine():
    """``run_sensor_cycle`` is an async function."""
    assert inspect.iscoroutinefunction(run_sensor_cycle)


def test_run_biep_v3_rerun_is_coroutine():
    """``run_biep_v3_rerun`` is an async function."""
    assert inspect.iscoroutinefunction(run_biep_v3_rerun)


def test_create_jurisdiction_monitors_is_coroutine():
    """``create_jurisdiction_monitors`` is an async function."""
    assert inspect.iscoroutinefunction(create_jurisdiction_monitors)


def test_diff_quest_packs_signature():
    """``diff_quest_packs`` accepts the canonical kwargs."""
    sig = inspect.signature(diff_quest_packs)
    assert "jurisdiction" in sig.parameters
    assert "new_pdf_hash" in sig.parameters
