# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "marimo>=0.9.0",
#   "lancedb>=0.13.0",
#   "pyarrow>=16.0.0",
#   "duckdb>=1.0.0",
#   "polars>=1.0.0",
#   "altair>=5.0.0",
#   "Pillow>=10.4.0",
# ]
# ///

"""notebooks/tuatha_anam_dashboard.py — the design surface for the British Isles MMO.

4 tabs:
  1. Sources   — per-source capture health + raw asset counts (no thumbnails)
  2. Boons     — searchable table of Hades boons → ANAM mapping
  3. Particles — color palette histogram across all 3 sources, scatter plot in LAB space
  4. Join      — the anam_particles_v1 table; flag rows as priority_for_v1

Reads from the Lance fat tables via lance_scan() (per the lancedb
skill); writes back to DuckLake via the BIEP v3 marimo_patterns helper.
"""

import marimo

__generated_with_marimo__ = "0.9.0"

app = marimo.App(width="medium", app_title="Tuatha ANAM Dashboard")


@app.cell
def _intro():
    import marimo as mo

    mo.md(
        """
        # 🜂 Tuatha ANAM Dashboard

        The design surface for the British Isles Formative Assessment MMO.

        Tabs:
        - **Sources** — per-source capture health
        - **Boons** — Hades boon → ANAM mapping
        - **Particles** — color palette across all 3 sources
        - **Join** — the `anam_particles_v1` table
        """
    )
    return (mo,)


@app.cell
def _tab_switcher(mo):
    # Each tab module exposes render() -> mo.Html. These used to be the
    # literal strings "tab_sources.py" etc., so the dashboard displayed
    # four filenames instead of four tabs.
    from tuatha.notebooks.anam.tabs import boons, join, particles, sources

    def _safe(label, module):
        """Render a tab, showing the failure rather than breaking the page.

        A tab whose Lance table has no rows yet should not take the other
        three down with it.
        """
        try:
            return module.render()
        except Exception as exc:
            return mo.md(f"**{label} unavailable:** `{exc}`")

    tabs = mo.ui.tabs(
        {
            "Sources": _safe("Sources", sources),
            "Boons": _safe("Boons", boons),
            "Particles": _safe("Particles", particles),
            "Join": _safe("Join", join),
        }
    )
    tabs
    return (tabs,)


if __name__ == "__main__":
    app.run()
