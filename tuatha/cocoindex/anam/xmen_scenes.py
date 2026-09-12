"""X-Men: Evolution scene extractor — CocoIndex v1 App.

Watches s3://cianfhoghlaim-tuatha-raw/xmen/<episode>/keyframes/ emitted
by the Hermes Agent computer-use client (Phase-2 capture path,
replacing the deprecated Swift daemon). Downscales frames to 1024px,
extracts typed XmenScene via BAML `ExtractXmenScene`, embeds the
description, writes the multimodal fat row to the Lance table.

Phase 1 (per the 2026-08-27 change): Hermes Agent observes the
window of an episode stream + captures keyframes on demand.
Phase 2: Hermes Agent autonomously navigates the episode + extracts
the most iconic power-saturated scenes.

Per the shippable=false invariant: the original animation frame
never enters the repo. Only the ≤1024px JPEG thumb + the typed
BAML description ship.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Annotated, Any

from cocoindex.connectors import lancedb
from cocoindex.ops.text import RecursiveSplitter
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from numpy.typing import NDArray

import cocoindex as coco

from ._shared import EMBEDDER, LANCE_DB, shared_lifespan

TABLE_NAME = "cianfhoghlaim.tuatha.xmen.scenes"
RAW_BUCKET = os.environ.get(
    "TUATHA_RAW_XMEN_BUCKET", "s3://cianfhoghlaim-tuatha-raw/xmen"
)


@dataclass
class XmenSceneRow:
    scene_id: str
    character: str
    team: str
    ability_name: str
    power_class: str
    episode: str
    timestamp: str
    work: str
    medium: str
    language: str
    effect_text: str
    color_hex: str
    particle_motion: str
    trigger: str
    consequence: str
    visual_grammar: str
    palette: str
    vfx_vocabulary: str
    narrative_beat: str
    transferability: str
    provenance_sha256: str
    captured_at: str
    embedding: Annotated[NDArray, EMBEDDER]
    thumb_blob: bytes  # ≤1024px JPEG, stored in the Lance fat table


_splitter = RecursiveSplitter()


async def _downscale(raw: bytes, max_side: int = 1024) -> bytes:
    """Resize any image to ≤max_side and return as JPEG bytes."""
    from io import BytesIO

    from PIL import Image

    img = Image.open(BytesIO(raw))
    img.thumbnail((max_side, max_side))
    buf = BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=85)
    return buf.getvalue()


async def _baml_extract_xmen_scene(thumb: bytes) -> dict[str, Any]:
    """Run the BAML ExtractXmenScene function. Imported lazily so the
    CocoIndex build step doesn't require the baml_client to be installed
    in CI environments that only want to lint the graph.

    The default VLM is `molmo2-8b` (the animation specialist with
    multi-image reasoning + grounding). Routes via
    `MODEL_REGISTRY.resolve("ocr_vision", "xmen_scene")` →
    `qwen3-vl-8b-xmen-scene` entry per the 2026-08-27
    centralized-model-registry delta.
    """
    from baml_client.sync_client import b  # type: ignore[import-not-found]

    result = b.ExtractXmenScene(image=thumb)
    return {
        "scene_id": result.scene_id,
        "character": result.character,
        "team": result.team.value if hasattr(result.team, "value") else str(result.team),
        "ability_name": result.ability_name,
        "power_class": result.power_class.value if hasattr(result.power_class, "value") else str(result.power_class),
        "episode": result.episode,
        "timestamp": result.timestamp,
        "work": result.work,
        "medium": result.medium,
        "language": result.language,
        "effect_text": result.powers[0].effect_text if result.powers else "",
        "color_hex": result.powers[0].color_hex if result.powers else "",
        "particle_motion": result.powers[0].particle_motion.value if result.powers and hasattr(result.powers[0].particle_motion, "value") else str(result.powers[0].particle_motion) if result.powers else "",
        "trigger": result.powers[0].trigger if result.powers else "",
        "consequence": result.powers[0].consequence if result.powers else "",
        "visual_grammar": result.visual_grammar or "",
        "palette": result.palette or "",
        "vfx_vocabulary": result.vfx_vocabulary or "",
        "narrative_beat": result.narrative_beat or "",
        "transferability": result.transferability or "",
        "provenance_sha256": result.provenance_sha256,
        "captured_at": result.captured_at,
    }


@coco.fn(memo=True)
async def process_xmen_keyframe(
    file: FileLike,
    table: lancedb.TableTarget,
) -> None:
    """Per-keyframe: downscale → BAML extract → embed → row."""
    raw = await file.read_bytes()
    thumb = await _downscale(raw)
    scene = await _baml_extract_xmen_scene(thumb)
    desc_text = (
        f"{scene['character']} ({scene['team']}) — "
        f"{scene['ability_name']} ({scene['power_class']}) — "
        f"{scene['effect_text']} — {scene['particle_motion']} — "
        f"Episode {scene['episode']} @ {scene['timestamp']}"
    )
    vec = await coco.use_context(EMBEDDER).embed(desc_text)
    table.declare_row(
        row=XmenSceneRow(
            scene_id=scene["scene_id"],
            character=scene["character"],
            team=scene["team"],
            ability_name=scene["ability_name"],
            power_class=scene["power_class"],
            episode=scene["episode"],
            timestamp=scene["timestamp"],
            work=scene["work"],
            medium=scene["medium"],
            language=scene["language"],
            effect_text=scene["effect_text"],
            color_hex=scene["color_hex"],
            particle_motion=scene["particle_motion"],
            trigger=scene["trigger"],
            consequence=scene["consequence"],
            visual_grammar=scene["visual_grammar"],
            palette=scene["palette"],
            vfx_vocabulary=scene["vfx_vocabulary"],
            narrative_beat=scene["narrative_beat"],
            transferability=scene["transferability"],
            provenance_sha256=scene["provenance_sha256"],
            captured_at=scene["captured_at"],
            embedding=vec,
            thumb_blob=thumb,
        )
    )


@coco.fn
async def app_main() -> None:
    table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name=TABLE_NAME,
        table_schema=await lancedb.TableSchema.from_class(
            XmenSceneRow, primary_key=["scene_id"]
        ),
    )
    table.declare_vector_index(column="embedding")
    table.declare_fts_index(
        column="effect_text", language="English", with_position=True
    )
    # Walk the raw capture bucket. The pattern matches keyframes
    # (jpegs) per episode. The full-resolution blobs never enter
    # the CocoIndex state path — only the downsampled thumb_blob
    # row.
    files = await lancedb.s3_walk_dir(
        RAW_BUCKET,
        path_matcher=PatternFilePathMatcher(
            included_patterns=["**/*.jpg", "**/*.jpeg"],
            excluded_patterns=["**/thumbs", "**/.tmp"],
        ),
        live=True,  # cocoindex update -L
    )
    await coco.mount_each(process_xmen_keyframe, files.items(), table)


xmen_scenes_app = coco.App(
    coco.AppConfig(name="tuatha_xmen_scenes"),
    app_main,
    lifespan=shared_lifespan,
)


if __name__ == "__main__":
    import cocoindex as _ci

    _ci.init()
    xmen_scenes_app.update()
