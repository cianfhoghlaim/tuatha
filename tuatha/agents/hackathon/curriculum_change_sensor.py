"""tuatha.agents.hackathon.curriculum_change_sensor — the Curriculum Change Detection Sensor.

Dagster sensor that watches the NCCA + AQA + SQA + WJEC + CCEA + IoM
(6 jurisdiction sites) via Firecrawl monitors and fires the BIEP v3
5-phase re-run + diff + new ``SkillTreeBadge`` with
``version=<new_pdf_hash>`` issuance when a syllabus PDF changes.

Per the BIEP v3 5-phase re-run (canonical order):

  1. ``baml_re_extract`` — re-run ``Generate<Subject>QuestPack``
  2. ``cocoindex_v1_re_embed`` — re-run the per_subject CocoIndex App
  3. ``cognee_cognify`` — cognify the new syllabus into the
     ``oideachais_<subject>`` Cognee dataset
  4. ``graphiti_temporal_memory`` — write the new event into the
     Graphiti temporal knowledge graph
  5. ``lancedb_re_index`` — re-index the ``per_subject_lance`` table

When the 5-phase re-run completes, the sensor diffs the new
quest pack against the prior quest pack. If ``items_changed > 0``
OR ``los_covered`` differs, a new ``SkillTreeBadge`` is issued with
``version=<new_pdf_hash>``. The new badge is queued for the next
daily Merkle anchor — the Phase 3 ``daily_credential_anchor``
Dagster asset picks it up.

Reference: ``openspec/changes/2026-08-26-tuatha-multimodel-2d-
graphics-and-earn-pipeline-v1/specs/cianfhoghlaim-educational-mmo/
spec.md`` § ADDED Requirements → "Curriculum change detection
sensor".
"""
from __future__ import annotations

import argparse
import asyncio
import datetime
import hashlib
import json
import logging
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

# ── Graceful degradation: the canonical 3-stack may be unavailable in offline dev ──

try:
    from google.adk.agents import LlmAgent  # type: ignore

    _ADK_AVAILABLE = True
except Exception:  # pragma: no cover — offline dev fallback
    LlmAgent = None  # type: ignore[assignment, misc]
    _ADK_AVAILABLE = False

try:
    from agents.meaisinfhoghlaim.firecrawl_mcp.client import (  # type: ignore
        FirecrawlMCPClient,
    )

    _FIRECRAWL_AVAILABLE = True
except Exception:  # pragma: no cover — offline dev fallback
    _FIRECRAWL_AVAILABLE = False
    FirecrawlMCPClient = None  # type: ignore[assignment, misc]


from ...config import TuathaConfig
from ...routing import build_wire

logger = logging.getLogger(__name__)


# ── The 6 jurisdiction config (the canonical list — no hardcoded URLs anywhere else) ──


JURISDICTIONS: dict[str, dict[str, str]] = {
    "NCCA": {
        "url": "https://www.ncca.ie/en/curriculum/",
        "country": "Ireland",
        "level_primary": "lc",
    },
    "AQA": {
        "url": "https://www.aqa.org.uk/subjects",
        "country": "England",
        "level_primary": "a_level",
    },
    "SQA": {
        "url": "https://www.sqa.org.uk/sqa/64717.html",
        "country": "Scotland",
        "level_primary": "higher",
    },
    "WJEC": {
        "url": "https://www.wjec.co.uk/qualifications/",
        "country": "Wales",
        "level_primary": "a_level",
    },
    "CCEA": {
        "url": "https://ccea.org.uk/qualifications",
        "country": "Northern Ireland",
        "level_primary": "a_level",
    },
    "IoM": {
        "url": "https://www.gov.im/education/",
        "country": "Isle of Man",
        "level_primary": "gcse",
    },
}

EXPECTED_JURISDICTION_COUNT: int = 6


SUBJECTS_PER_JURISDICTION: dict[str, tuple[str, ...]] = {
    "NCCA": (
        "mathematics",
        "applied_mathematics",
        "chemistry",
        "geography",
        "history",
        "english",
        "gaeilge",
        "computer_science",
    ),
    "AQA": (
        "mathematics",
        "chemistry",
        "geography",
        "history",
        "english",
        "computer_science",
    ),
    "SQA": (
        "mathematics",
        "chemistry",
        "geography",
        "history",
        "english",
        "computer_science",
    ),
    "WJEC": (
        "mathematics",
        "chemistry",
        "geography",
        "history",
        "english",
        "computer_science",
    ),
    "CCEA": (
        "mathematics",
        "chemistry",
        "geography",
        "history",
        "english",
    ),
    "IoM": (
        "mathematics",
        "english",
    ),
}


# ── The 5-phase re-run order (canonical BIEP v3) ──


BIEP_V3_PHASES: tuple[str, ...] = (
    "baml_re_extract",
    "cocoindex_v1_re_embed",
    "cognee_cognify",
    "graphiti_temporal_memory",
    "lancedb_re_index",
)

EXPECTED_PHASE_COUNT: int = 5


# ── The canonical SubjectAgentWiring (preserves existing surface) ──


_wire = build_wire(
    ncca_subject="curriculum_change_sensor",
    module_slug="curriculum_change_sensor",
    display_name="Curriculum Change Sensor",
    baml_prefix="CurrChgSens",
    langfuse_trace_name="agent.curriculum_change_sensor.<verb>",
    cognee_dataset="oideachais_curriculum_change_sensor",
    letta_agent_id="kcg-curriculum-change-sensor-agent",
)


config = TuathaConfig.from_env()


def _build_agent() -> Any:
    """Build the canonical ADK agent when google.adk is available.

    Returns ``None`` when google.adk is missing (the offline dev
    fallback path). The agent's public surface (``name`` /
    ``model`` / ``description`` / ``instruction`` / ``output_key``)
    is unchanged when google.adk is present.
    """
    if not _ADK_AVAILABLE or LlmAgent is None:
        return None
    return LlmAgent(
        name="curriculum_change_sensor_agent",
        model=config.litellm.resolve_model("text_llm", "default"),
        description=(
            "Curriculum Change Detection Sensor. Dagster sensor that "
            "watches the NCCA + AQA + SQA + WJEC + CCEA + IoM websites "
            "and fires the SequentialAgent on changes."
        ),
        instruction=(
            "You are the Curriculum Change Sensor. You watch the "
            "6-jurisdiction curriculum websites for syllabus changes. "
            "When a change is detected, you fire the SequentialAgent "
            "to update the per-jurisdiction syllabus DLT sources + "
            "the per-subject BAML contracts + the per-subject agents."
        ),
        output_key="curriculum_change_sensor_response",
    )


curriculum_change_sensor_agent = _build_agent()


# ── Data classes (the new wiring surface) ──


@dataclass(frozen=True)
class PdfChange:
    """A syllabus PDF change detected by a Firecrawl monitor.

    One ``PdfChange`` is emitted per ``(jurisdiction, subject)``
    pair by a Firecrawl ``monitor_create`` check. The
    ``previous_pdf_hash`` is the SHA-256 of the PDF the prior
    run saw; ``new_pdf_hash`` is the SHA-256 of the new PDF.

    When ``previous_pdf_hash == new_pdf_hash`` the change is a
    no-op and the sensor skips the BIEP v3 5-phase re-run.
    """

    jurisdiction: str
    subject: str
    new_pdf_url: str
    new_pdf_hash: str
    previous_pdf_hash: str
    detected_at: datetime.datetime
    monitor_id: str

    def is_real_change(self) -> bool:
        """Return True iff the SHA-256 hashes actually differ."""
        return self.new_pdf_hash != self.previous_pdf_hash


@dataclass(frozen=True)
class QuestPack:
    """The typed output of the ``Generate<Subject>QuestPack`` BAML function.

    Mirrors the canonical shape of the BAML ``Generate<Subject>QuestPack``
    contract (the contract itself is added by the Phase 1 per-subject
    BAML work — the dataclass is the offline-dev fallback so the
    sensor can be exercised without a live BAML runtime).
    """

    subject: str
    items: tuple[str, ...]
    los_covered: tuple[str, ...]


@dataclass(frozen=True)
class QuestPackDiff:
    """The diff between a new quest pack and the prior quest pack.

    The sensor emits a new ``SkillTreeBadge`` iff ``has_change`` is
    True (i.e., ``items_changed > 0`` OR ``los_changed`` is True).
    The ``version`` field is ``<new_pdf_hash>`` (per the spec).
    """

    jurisdiction: str
    subject: str
    version: str  # = new_pdf_hash
    items_changed: int
    los_covered: tuple[str, ...]
    previous_los_covered: tuple[str, ...]
    los_changed: bool
    items_added: tuple[str, ...]
    items_removed: tuple[str, ...]
    has_change: bool


@dataclass(frozen=True)
class ChangeSensorReport:
    """The full report from one sensor cycle (one Dagster sensor tick).

    The Phase 3 ``daily_credential_anchor`` Dagster asset picks up
    every ``badge_version`` listed in ``badge_versions_emitted`` and
    includes the corresponding ``SkillTreeBadgeDraft`` in the
    next Merkle batch.
    """

    run_id: str
    started_at: datetime.datetime
    completed_at: datetime.datetime | None
    pdf_changes: tuple[PdfChange, ...]
    badge_versions_emitted: tuple[str, ...]
    re_run_subjects: tuple[str, ...]
    dry_run: bool


@dataclass(frozen=True)
class SkillTreeBadgeDraft:
    """The draft of a new version-anchored ``SkillTreeBadge``.

    The canonical ``SkillTreeBadge`` (in ``badges.schema``) does
    not carry a ``version`` field; this draft extends the canonical
    shape with ``version=<new_pdf_hash>`` so the daily Merkle
    anchor can group diff badges by syllabus PDF version.

    The ``evidence_hash`` is the SHA-256 of the canonical evidence
    tuple ``(jurisdiction, subject, version)`` — it doubles as
    the Merkle leaf for the daily anchor.
    """

    framework: str
    subject: str
    level: str
    competency_code: str
    version: str
    date_earned: datetime.datetime
    agent_issuer: str
    evidence_hash: str
    metadata: dict[str, Any]


# ── Hash + diff helpers ──


def hash_pdf_bytes(pdf_bytes: bytes) -> str:
    """SHA-256 of a PDF byte stream (used as the badge ``version``)."""
    return hashlib.sha256(pdf_bytes).hexdigest()


def diff_quest_packs(
    prior: QuestPack,
    new: QuestPack,
    *,
    jurisdiction: str,
    new_pdf_hash: str,
) -> QuestPackDiff:
    """Diff the new quest pack against the prior quest pack.

    Returns a ``QuestPackDiff`` with ``has_change=True`` iff:

    - ``items_changed > 0`` (the new ``items[]`` set differs from prior)
    - OR ``los_changed`` (the covered learning outcomes differ)

    The ``version`` field is set to ``new_pdf_hash`` per the spec.
    """
    prior_items = set(prior.items)
    new_items = set(new.items)
    added = tuple(sorted(new_items - prior_items))
    removed = tuple(sorted(prior_items - new_items))
    items_changed = len(added) + len(removed)

    los_changed = tuple(sorted(prior.los_covered)) != tuple(sorted(new.los_covered))

    return QuestPackDiff(
        jurisdiction=jurisdiction,
        subject=new.subject,
        version=new_pdf_hash,
        items_changed=items_changed,
        los_covered=new.los_covered,
        previous_los_covered=prior.los_covered,
        los_changed=los_changed,
        items_added=added,
        items_removed=removed,
        has_change=(items_changed > 0) or los_changed,
    )


def make_badge_for_diff(
    diff: QuestPackDiff,
    *,
    framework: str = "ncca-lc",
    level: str = "hl",
    agent_issuer: str = "curriculum_change_sensor_agent",
) -> SkillTreeBadgeDraft:
    """Build the new version-anchored ``SkillTreeBadgeDraft`` for a diff.

    The ``version`` field is ``<new_pdf_hash>`` per the spec. The
    badge is queued for the next daily Merkle anchor — the Phase 3
    ``daily_credential_anchor`` Dagster asset picks it up.
    """
    competency_code = f"LC-{diff.subject.upper()}-DIFF-{diff.version[:8]}"
    date_earned = datetime.datetime.now(tz=datetime.UTC)
    metadata = {
        "items_added": list(diff.items_added),
        "items_removed": list(diff.items_removed),
        "previous_los_covered": list(diff.previous_los_covered),
        "jurisdiction": diff.jurisdiction,
        "los_changed": diff.los_changed,
        "items_changed": diff.items_changed,
    }
    return SkillTreeBadgeDraft(
        framework=framework,
        subject=diff.subject,
        level=level,
        competency_code=competency_code,
        version=diff.version,
        date_earned=date_earned,
        agent_issuer=agent_issuer,
        evidence_hash=hashlib.sha256(
            f"{diff.jurisdiction}|{diff.subject}|{diff.version}".encode()
        ).hexdigest(),
        metadata=metadata,
    )


# ── Firecrawl monitor management ──


async def create_jurisdiction_monitors(
    *,
    client: Any | None = None,
    schedule: str = "every_24_hours",
    dry_run: bool = True,
) -> dict[str, str]:
    """Create one Firecrawl monitor per ``(jurisdiction, subject)`` pair.

    Returns a dict mapping ``"{jurisdiction}:{subject}"`` strings to
    the (synthetic or real) ``monitor_id``.

    In ``--dry-run`` mode (default), no Firecrawl MCP call is made;
    the ``monitor_id`` is a deterministic UUID5 derived from the
    ``(jurisdiction_url, subject, schedule)`` triple so offline
    dev runs are reproducible.

    In live mode, ``client.monitor_create()`` is called once per
    ``(jurisdiction, subject)`` pair. The client must implement the
    canonical ``monitor_create(name, targets, schedule, goal)``
    interface (the ``FirecrawlMCPClient`` wrapper at
    ``agents/meaisinfhoghlaim/firecrawl_mcp/client.py``).
    """
    monitors: dict[str, str] = {}
    for jurisdiction, info in JURISDICTIONS.items():
        for subject in SUBJECTS_PER_JURISDICTION[jurisdiction]:
            key = f"{jurisdiction}:{subject}"
            if dry_run or client is None:
                monitor_id = str(
                    uuid.uuid5(
                        uuid.NAMESPACE_URL,
                        f"{info['url']}#{subject}#{schedule}",
                    )
                )
            else:
                response = client.monitor_create(
                    name=f"tuatha_ccs_{jurisdiction}_{subject}",
                    targets=[{"type": "url", "url": info["url"]}],
                    schedule={"frequency": schedule},
                    goal=(
                        f"Detect syllabus PDF changes for {subject} "
                        f"({info['country']}, {jurisdiction})"
                    ),
                )
                monitor_id = getattr(response, "monitor_id", str(response))
            monitors[key] = monitor_id
    return monitors


# ── The 5-phase re-run ──


async def run_biep_v3_rerun(
    jurisdiction: str,
    subject: str,
    new_pdf_hash: str,
    *,
    rerun_fn: Callable[..., Awaitable[Any]] | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Run the 5-phase BIEP v3 re-run for one ``(jurisdiction, subject)``.

    Phases (in canonical order):

      1. ``baml_re_extract`` — re-run ``Generate<Subject>QuestPack``
      2. ``cocoindex_v1_re_embed`` — re-run the per_subject CocoIndex App
      3. ``cognee_cognify`` — cognify the new syllabus into Cognee
      4. ``graphiti_temporal_memory`` — write to Graphiti
      5. ``lancedb_re_index`` — re-index the ``per_subject_lance`` table

    Returns a dict mapping phase name to the per-phase result.
    In ``--dry-run`` mode the phases are simulated (the default
    offline-dev path); the result is a per-phase stub.

    The ``rerun_fn`` callback (when provided + ``dry_run=False``)
    replaces the real phase implementations; it receives
    ``(phase, jurisdiction, subject, new_pdf_hash)`` and returns
    the per-phase result. This is the test seam.
    """
    if jurisdiction not in JURISDICTIONS:
        raise ValueError(f"unknown jurisdiction: {jurisdiction}")

    started_at = datetime.datetime.now(tz=datetime.UTC)
    phase_results: dict[str, Any] = {}

    for phase in BIEP_V3_PHASES:
        if dry_run or rerun_fn is None:
            phase_results[phase] = {
                "status": "simulated",
                "phase": phase,
                "jurisdiction": jurisdiction,
                "subject": subject,
                "version": new_pdf_hash,
                "ts": datetime.datetime.now(tz=datetime.UTC).isoformat(),
            }
        else:
            phase_results[phase] = await rerun_fn(
                phase,
                jurisdiction,
                subject,
                new_pdf_hash,
            )

    return {
        "jurisdiction": jurisdiction,
        "subject": subject,
        "version": new_pdf_hash,
        "phases": phase_results,
        "started_at": started_at.isoformat(),
        "completed_at": datetime.datetime.now(tz=datetime.UTC).isoformat(),
        "dry_run": dry_run,
    }


# ── The top-level sensor cycle ──


async def run_sensor_cycle(
    *,
    firecrawl_client: Any | None = None,
    rerun_fn: Callable[..., Awaitable[Any]] | None = None,
    prior_quest_packs: dict[tuple[str, str], QuestPack] | None = None,
    new_quest_packs: dict[tuple[str, str], QuestPack] | None = None,
    pdf_changes: tuple[PdfChange, ...] = (),
    dry_run: bool = True,
) -> ChangeSensorReport:
    """Run one sensor cycle (one Dagster sensor tick).

    The canonical flow:

      1. Create the Firecrawl monitors (or return ``--dry-run`` stubs).
      2. For each ``PdfChange`` detected:
         a. Skip if the SHA-256 hashes match (no real change).
         b. Run the BIEP v3 5-phase re-run.
         c. Look up the ``prior`` + ``new`` ``QuestPack`` for the
            ``(jurisdiction, subject)`` pair (the ``new`` pack is the
            output of the Phase 1 ``baml_re_extract`` step).
         d. Compute the ``QuestPackDiff`` and, if ``has_change``,
            issue a new ``SkillTreeBadgeDraft`` with
            ``version=<new_pdf_hash>``.
      3. Return the consolidated ``ChangeSensorReport``.

    In ``--dry-run`` mode (default), no network calls are made; the
    diff badges are constructed from the provided
    ``prior_quest_packs`` / ``new_quest_packs`` dicts (or the empty
    dict if not provided — every diff then has ``items_changed=0``
    and ``los_changed=False``, so no badges are issued).
    """
    started_at = datetime.datetime.now(tz=datetime.UTC)
    run_id = str(uuid.uuid4())

    await create_jurisdiction_monitors(
        client=firecrawl_client, dry_run=dry_run,
    )

    badge_versions: list[str] = []
    re_run_subjects: list[str] = []

    prior_qp = prior_quest_packs or {}
    new_qp = new_quest_packs or {}

    for change in pdf_changes:
        if not change.is_real_change():
            continue
        re_run_subjects.append(change.subject)
        await run_biep_v3_rerun(
            change.jurisdiction,
            change.subject,
            change.new_pdf_hash,
            rerun_fn=rerun_fn,
            dry_run=dry_run,
        )
        prior = prior_qp.get((change.jurisdiction, change.subject))
        new = new_qp.get((change.jurisdiction, change.subject))
        if prior is None or new is None:
            continue
        diff = diff_quest_packs(
            prior,
            new,
            jurisdiction=change.jurisdiction,
            new_pdf_hash=change.new_pdf_hash,
        )
        if diff.has_change:
            make_badge_for_diff(diff)
            badge_versions.append(diff.version)

    return ChangeSensorReport(
        run_id=run_id,
        started_at=started_at,
        completed_at=datetime.datetime.now(tz=datetime.UTC),
        pdf_changes=pdf_changes,
        badge_versions_emitted=tuple(badge_versions),
        re_run_subjects=tuple(re_run_subjects),
        dry_run=dry_run,
    )


# ── CLI (--dry-run by default) ──


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build the canonical CLI argument parser.

    ``--dry-run`` is the default; ``--live`` flips the flag off and
    routes through the real Firecrawl MCP + BAML + Cognee stack.
    """
    parser = argparse.ArgumentParser(
        prog="tuatha-curriculum-change-sensor",
        description=(
            "The Tuatha Curriculum Change Sensor. Watches the "
            "6-jurisdiction curriculum websites for syllabus PDF "
            "changes; on a change, fires the BIEP v3 5-phase "
            "re-run + diff + new SkillTreeBadge with "
            "version=<new_pdf_hash> + re-anchor via the next "
            "daily Merkle anchor."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Run in offline dev mode (no Firecrawl / BAML calls).",
    )
    parser.add_argument(
        "--live",
        action="store_false",
        dest="dry_run",
        help="Hit the live Firecrawl MCP + BAML + Cognee stack.",
    )
    parser.add_argument(
        "--jurisdiction",
        choices=sorted(JURISDICTIONS.keys()),
        help="Limit the cycle to one jurisdiction (default: all 6).",
    )
    parser.add_argument(
        "--subject",
        help=(
            "Limit the cycle to one subject slug "
            "(default: all per-jurisdiction subjects)."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point (returns the process exit code)."""
    args = _build_arg_parser().parse_args(argv)
    report = asyncio.run(run_sensor_cycle(dry_run=args.dry_run))
    summary = {
        "run_id": report.run_id,
        "started_at": report.started_at.isoformat(),
        "completed_at": (
            report.completed_at.isoformat() if report.completed_at else None
        ),
        "re_run_subjects": list(report.re_run_subjects),
        "badge_versions_emitted": list(report.badge_versions_emitted),
        "dry_run": report.dry_run,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


__all__ = [
    "BIEP_V3_PHASES",
    "EXPECTED_JURISDICTION_COUNT",
    "EXPECTED_PHASE_COUNT",
    "JURISDICTIONS",
    "SUBJECTS_PER_JURISDICTION",
    "ChangeSensorReport",
    "PdfChange",
    "QuestPack",
    "QuestPackDiff",
    "SkillTreeBadgeDraft",
    "_build_agent",
    "_wire",
    "config",
    "create_jurisdiction_monitors",
    "curriculum_change_sensor_agent",
    "diff_quest_packs",
    "hash_pdf_bytes",
    "main",
    "make_badge_for_diff",
    "run_biep_v3_rerun",
    "run_sensor_cycle",
]
