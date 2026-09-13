"""Dagster asset definitions for the ANAM capture pipeline.

4 asset groups:
  - tuatha_capture    (3 assets — ingest raw frames per source)
  - tuatha_embed      (3 assets — drive the CocoIndex flows)
  - tuatha_join       (1 asset — cross-source AnamParticle join)
  - tuatha_quality    (1 asset_check — RAGAS anam_color_anchor metric)

All assets are RAGAS-gated; the embed/join assets are `blocking=True`
on their quality gates.

Follows the BIEP v3 pattern (orchestration/defs/2_materials/) per the
BIEP v2 asset conventions + the agent-observability skill.

NOTE: this module must not use ``from __future__ import annotations``.
Dagster resolves an asset's ``config`` type by inspecting the
annotation, and postponed evaluation leaves it as a string that Dagster
reports as "Unable to resolve config type 'CaptureConfig'". Python 3.11
handles the remaining annotations here natively.
"""

import os
import pathlib
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import structlog
from pydantic import Field

from dagster import (
    AssetCheckResult,
    AssetCheckSeverity,
    AssetExecutionContext,
    Config,
    MetadataValue,
    asset,
    asset_check,
)

from .anam_observability import mlflow_log_metric

log = structlog.get_logger("tuatha.anam")


def _repo_root() -> str:
    """Return the directory the `cocoindex` CLI should run from.

    The CocoIndex apps now live in this repository, so the default is
    the tuatha checkout. It used to be a hardcoded absolute path to
    the cianfhoghlaim monorepo.
    """
    return os.environ.get(
        "TUATHA_REPO_ROOT", str(pathlib.Path(__file__).resolve().parents[2])
    )


# -- Configs --------------------------------------------------------------------


class CaptureConfig(Config):
    source: str = Field(description="hades | comic | gba | manual")
    run_id: str = Field(description="Unique run identifier")
    manifest_path: str = Field(description="Local path to the capture manifest.jsonl")


# -- Assets ---------------------------------------------------------------------


@asset(group_name="tuatha_capture", compute_kind="python")
def hades_raw_captures(
    context: AssetExecutionContext, config: CaptureConfig
) -> dict[str, Any]:
    """Ingest a manual Hades capture run.

    Reads the manifest.jsonl written by the Swift tuatha-capture daemon
    + uploads the raw keyframes + bursts to the Pangolin-private
    s3://cianfhoghlaim-tuatha-raw/hades/<run_id>/ bucket.

    Returns a dict with `frame_count`, `burst_count`, `bytes_written`.
    """
    if config.source != "hades":
        return {"skipped": True, "reason": "wrong source"}

    manifest = Path(config.manifest_path)
    if not manifest.exists():
        log.warning("hades_manifest_missing", path=config.manifest_path)
        context.log.warning(f"manifest missing: {config.manifest_path}")
        return {"skipped": True}

    frames = 0
    bursts = 0
    bytes_written = 0
    with manifest.open() as f:
        for line in f:
            event = _safe_json(line)
            if "frame" in event:
                frames += 1
                bytes_written += _safe_filesize(event.get("path"))
            if event.get("event") == "burst_started":
                bursts += 1

    context.add_metadata(
        {
            "frame_count": frames,
            "burst_count": bursts,
            "bytes_written": MetadataValue.md(
                f"{bytes_written:,} bytes ({bytes_written / 1e6:.1f} MB)"
            ),
            "run_id": MetadataValue.text(config.run_id),
        }
    )
    log.info(
        "hades_raw_captures_done",
        frames=frames,
        bursts=bursts,
        bytes_written=bytes_written,
        run_id=config.run_id,
    )
    return {
        "run_id": config.run_id,
        "frame_count": frames,
        "burst_count": bursts,
        "bytes_written": bytes_written,
    }


@asset(group_name="tuatha_capture", compute_kind="python")
def comic_raw_pages(
    context: AssetExecutionContext, config: CaptureConfig
) -> dict[str, Any]:
    """Ingest comic book pages (CBZ → per-page PNG + metadata JSONL)."""
    if config.source != "comic":
        return {"skipped": True}
    # The comic ingest happens in `tuatha-capture comic` (the Python CLI).
    # This asset just records the result.
    manifest = Path(config.manifest_path)
    if not manifest.exists():
        return {"skipped": True}
    pages = sum(1 for _ in manifest.open())
    context.add_metadata({"pages": pages, "run_id": config.run_id})
    return {"run_id": config.run_id, "pages": pages}


@asset(group_name="tuatha_capture", compute_kind="python")
def gba_raw_frames(
    context: AssetExecutionContext, config: CaptureConfig
) -> dict[str, Any]:
    """Ingest GBA frames (mgba-py → per-frame PNG)."""
    if config.source != "gba":
        return {"skipped": True}
    out_dir = Path(config.manifest_path).parent
    frames = sum(1 for _ in out_dir.glob("frame-*.png"))
    context.add_metadata({"frames": frames, "run_id": config.run_id})
    return {"run_id": config.run_id, "frames": frames}


# -- Embed group (drive the CocoIndex flows) -----------------------------------


@asset(group_name="tuatha_embed", compute_kind="cocoindex", deps=["hades_raw_captures"])
def hades_boons_embedded(context: AssetExecutionContext) -> dict[str, Any]:
    """Drive the hades_boons_app CocoIndex v1 flow.

    Runs `cocoindex update tuatha_hades_boons` and returns the row count
    in the Lance table cianfhoghlaim.tuatha.hades.boons.
    """
    import subprocess

    proc = subprocess.run(
        ["cocoindex", "update", "tuatha_hades_boons"],
        capture_output=True,
        text=True,
        cwd=_repo_root(),
    )
    if proc.returncode != 0:
        context.log.error(f"cocoindex failed: {proc.stderr}")
        return {"rows": 0, "error": proc.stderr}
    context.add_metadata({"stdout": MetadataValue.md(f"```\n{proc.stdout}\n```")})
    rows = _extract_row_count(proc.stdout)
    return {"rows": rows}


@asset(group_name="tuatha_embed", compute_kind="cocoindex", deps=["comic_raw_pages"])
def comic_particles_embedded(context: AssetExecutionContext) -> dict[str, Any]:
    import subprocess

    proc = subprocess.run(
        ["cocoindex", "update", "tuatha_comic_particles"],
        capture_output=True,
        text=True,
        cwd=_repo_root(),
    )
    if proc.returncode != 0:
        return {"rows": 0, "error": proc.stderr}
    return {"rows": _extract_row_count(proc.stdout)}


@asset(group_name="tuatha_embed", compute_kind="cocoindex", deps=["gba_raw_frames"])
def gba_magic_embedded(context: AssetExecutionContext) -> dict[str, Any]:
    import subprocess

    proc = subprocess.run(
        ["cocoindex", "update", "tuatha_gba_magic"],
        capture_output=True,
        text=True,
        cwd=_repo_root(),
    )
    if proc.returncode != 0:
        return {"rows": 0, "error": proc.stderr}
    return {"rows": _extract_row_count(proc.stdout)}


# -- Join group -----------------------------------------------------------------


@asset(
    group_name="tuatha_join",
    compute_kind="cocoindex",
    deps=["hades_boons_embedded", "comic_particles_embedded", "gba_magic_embedded"],
)
def anam_particles_v1(context: AssetExecutionContext) -> dict[str, Any]:
    """Drive the anam_particles_app CocoIndex v1 cross-source join."""
    import subprocess

    proc = subprocess.run(
        ["cocoindex", "update", "tuatha_anam_particles"],
        capture_output=True,
        text=True,
        cwd=_repo_root(),
    )
    if proc.returncode != 0:
        return {"rows": 0, "error": proc.stderr}
    return {"rows": _extract_row_count(proc.stdout)}


# -- RAGAS asset_check ----------------------------------------------------------


#: Maximum perceptual drift a derived ANAM colour may have from the
#: source colour it was mapped from.
#:
#: On the CIE76 scale: <1 is imperceptible, 1-2 perceptible only on
#: close inspection, 2-10 perceptible at a glance, 11-49 "more similar
#: than opposite". 8 means the ANAM colour is allowed to move
#: noticeably toward the turquoise palette while staying recognisably
#: derived from its source, rather than being freely invented.
ANAM_DELTA_E_THRESHOLD = 8.0

#: The fraction of rows that must be within the threshold to pass.
ANAM_COLOR_ANCHOR_MIN_SCORE = 0.85


def measure_color_anchor(
    pairs: "Iterator[tuple[str, str]] | list[tuple[str, str]]",
    *,
    threshold: float = ANAM_DELTA_E_THRESHOLD,
) -> dict[str, Any]:
    """Measure how well derived ANAM colours stay anchored to their source.

    Args:
        pairs: ``(source_color_hex, anam_color_hex)`` for each row.
        threshold: maximum permitted CIE76 ΔE.

    Returns:
        ``score`` (fraction within threshold), ``evaluated``,
        ``within``, ``max_delta_e``, ``mean_delta_e`` and ``malformed``.

    An empty input scores 0.0, not 1.0. "No rows" is a pipeline failure,
    and a vacuous pass is how a broken join gets promoted.
    """
    from tuatha.theming.color import delta_e

    deltas: list[float] = []
    malformed = 0
    for source_hex, anam_hex in pairs:
        try:
            deltas.append(delta_e(source_hex, anam_hex))
        except (ValueError, TypeError):
            malformed += 1

    evaluated = len(deltas)
    if not evaluated:
        return {
            "score": 0.0,
            "evaluated": 0,
            "within": 0,
            "max_delta_e": None,
            "mean_delta_e": None,
            "malformed": malformed,
        }

    within = sum(1 for d in deltas if d <= threshold)
    return {
        "score": within / (evaluated + malformed),
        "evaluated": evaluated,
        "within": within,
        "max_delta_e": max(deltas),
        "mean_delta_e": sum(deltas) / evaluated,
        "malformed": malformed,
    }


def _read_anam_color_pairs() -> list[tuple[str, str]]:
    """Read ``(source_color_hex, anam_color_hex)`` from the ANAM table."""
    import lancedb

    uri = os.environ.get("TUATHA_LANCE_URI")
    if not uri:
        raise RuntimeError(
            "TUATHA_LANCE_URI is not set, so the colour anchor cannot be "
            "measured. See tuatha/corpus/CONTRACT.md."
        )
    table = lancedb.connect(uri).open_table("cianfhoghlaim.tuatha.anam_particles")
    return [
        (row.get("source_color_hex", ""), row.get("anam_color_hex", ""))
        for row in table.search().limit(100_000).to_list()
    ]


@asset_check(
    asset=anam_particles_v1,
    blocking=True,
    description=(
        "Does each derived ANAM colour stay within ΔE ≤ 8 (CIE76) of the "
        "source colour it was mapped from?"
    ),
)
def ragas_anam_color_anchor(context, anam_particles_v1) -> AssetCheckResult:
    """Measure ANAM colour drift against the source colours.

    The ANAM palette is derived from real sources — a Hades boon, a comic
    panel, a Golden Sun sprite — rather than chosen. This check is what
    makes that claim falsifiable: it computes the CIE76 ΔE between each
    row's source colour and its derived ANAM colour, and fails when too
    many rows have drifted past the threshold.

    This previously returned a hardcoded ``score = 0.92`` and set
    ``severity`` to ``WARN`` on both branches of its conditional, so the
    gate reported an invented number and could never fail.
    """
    rows = anam_particles_v1.get("rows", 0)
    context.log.info(f"measuring colour anchor over {rows} ANAM rows")

    try:
        pairs = _read_anam_color_pairs()
    except Exception as exc:
        # Unmeasurable is not the same as passing.
        context.log.error(f"colour anchor unmeasurable: {exc}")
        return AssetCheckResult(
            passed=False,
            severity=AssetCheckSeverity.ERROR,
            metadata={
                "error": str(exc),
                "rows_reported_by_asset": rows,
                "metric_kind": "color_anchor_v1",
            },
        )

    result = measure_color_anchor(pairs)
    passed = result["score"] >= ANAM_COLOR_ANCHOR_MIN_SCORE
    mlflow_log_metric("ragas_anam_color_anchor", result["score"])

    return AssetCheckResult(
        passed=passed,
        severity=AssetCheckSeverity.ERROR if not passed else AssetCheckSeverity.WARN,
        metadata={
            "score": result["score"],
            "min_score": ANAM_COLOR_ANCHOR_MIN_SCORE,
            "threshold_delta_e": ANAM_DELTA_E_THRESHOLD,
            "rows_evaluated": result["evaluated"],
            "rows_within_threshold": result["within"],
            "rows_malformed": result["malformed"],
            "max_delta_e": result["max_delta_e"],
            "mean_delta_e": result["mean_delta_e"],
            "metric_kind": "color_anchor_v1",
        },
    )


# -- Helpers --------------------------------------------------------------------


def _safe_json(line: str) -> dict[str, Any]:
    import json

    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return {}


def _safe_filesize(path: str | None) -> int:
    if not path:
        return 0
    try:
        return Path(path).stat().st_size
    except OSError:
        return 0


def _extract_row_count(stdout: str) -> int:
    """Best-effort parse of cocoindex `update` stdout for the row count."""
    import re

    m = re.search(r"(\d+)\s+rows?\s+(?:added|upserted|reconciled)", stdout)
    return int(m.group(1)) if m else 0
