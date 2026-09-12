"""Tab 4 — X-Men Scenes (added 2026-08-27).

Searchable table of X-Men: Evolution (2000-2003) scene
extractions → ANAM Celtic-deity mapping. Parallels the
existing `boons.py` tab for Hades boons.

Per the 2026-08-27 change: the 3rd ANAM corpus is X-Men:
Evolution animation. The default VLM is `molmo2-8b`
(animation specialist, multi-image reasoning + grounding).
The Lance table is `cianfhoghlaim.tuatha.xmen.scenes`.
"""
from __future__ import annotations

import marimo as mo
import polars as pl

from ..helpers import TABLE_ANAM, open_db, query_via_lance_scan

TABLE_XMEN = "cianfhoghlaim.tuatha.xmen.scenes"


def render() -> mo.Html:
    db = open_db()
    try:
        scenes_t = query_via_lance_scan(db, TABLE_XMEN)
        anam_t = query_via_lance_scan(db, TABLE_ANAM)
    except Exception as exc:
        return mo.md(f"**Error loading tables:** `{exc}`")

    scenes = pl.from_arrow(scenes_t)
    anam = pl.from_arrow(anam_t).filter(pl.col("source") == "xmen.scenes")

    joined = scenes.join(
        anam.select(["source_id", "celtic_deity", "anam_color_hex", "anam_motion"]),
        left_on="scene_id",
        right_on="source_id",
        how="left",
    )

    rows_html = "".join(
        f"<tr><td>{r['character']}</td><td>{r['team']}</td>"
        f"<td>{r['ability_name']}</td><td>{r['power_class']}</td>"
        f"<td>{r['episode']} @ {r['timestamp']}</td>"
        f"<td><code>{r['color_hex']}</code></td>"
        f"<td>{r.get('celtic_deity', '—')}</td>"
        f"<td><code>{r.get('anam_color_hex', '—')}</code></td></tr>"
        for r in joined.head(50).to_dicts()
    )
    return mo.md(
        f"""
## X-Men: Evolution Scenes

Showing the first 50 X-Men: Evolution scenes from the
`xmen_scenes` Lance table joined to the `anam_particles_v1`
table (where source = `xmen.scenes`).

VLM: `molmo2-8b` (animation specialist). The Celtic-deity
mapping is derived per character — Cyclops → Taranis,
Storm → Manannán/Taranis, Jean Grey → Danu, Wolverine →
Cernunnos, Mystique → TheMorrígan, etc. (see the full map
in `tuatha/sources/anam/xmen_evolution/source.yaml`).

<table>
<tr><th>Character</th><th>Team</th><th>Ability</th><th>Class</th>
<th>Episode</th><th>Source color</th><th>Tuatha counterpart</th>
<th>ANAM color</th></tr>
{rows_html}
</table>
        """
    )
