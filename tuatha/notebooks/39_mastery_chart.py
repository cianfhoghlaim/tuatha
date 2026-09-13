# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.10.0",
#     "pandas>=2.0",
# ]
# ///

"""tuatha.notebooks.39_mastery_chart — marimo notebook for per-subject mastery over time.

The Phase-2 P4 mastery visualisation. Reads a student's
``SkillTreeBadge`` rows (the per-subject mastery events) and
renders:

1. A per-subject mastery timeline (one trace per NCCA subject)
   showing the cumulative ``SkillTreeBadge`` count over time.
2. The 8-axis spider chart (the ``tuatha/web/packages/
   mastery-chart`` package output) for the *current* mastery
   state.
3. The student's top subject + the FIBO emblem cache key
   (mirrors the ``/student/<id>/mastery`` route's emblem logic).

The notebook is fully offline: it falls back to a small synthetic
``SkillTreeBadge`` dataset when ``CONVEX_URL`` is unset, so the
visualisation can be exercised in any environment.

Run with:
    marimo edit notebooks/39_mastery_chart.py
    # or
    uv run marimo run notebooks/39_mastery_chart.py

Per ``2026-08-26-tuatha-multimodel-2d-graphics-and-earn-pipeline-v1``,
Layer 3 (P4).
"""
import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Per-Subject Mastery Over Time

        Visualise the cumulative ``SkillTreeBadge`` count per
        NCCA subject for one student. The notebook renders:

        1. A timeline (one line per subject) showing when each
           subject's mastery events were recorded.
        2. The 8-axis spider chart for the student's *current*
           mastery profile.
        3. The top-subject + FIBO emblem cache key for the
           ``/student/<id>/mastery`` route.

        ## Inputs

        | Field | Description | Example |
        |:--|:--|:--|
        | `student_id` | The student pseudonym UUID | `stu_e2e_001` |
        | `source` | Where the badges come from (`convex`, `synthetic`) | `convex` |
        | `language` | EN or GA label set for the axes | `en` |
        """
    )
    return (mo,)


@app.cell
def _():
    import hashlib
    import os
    from datetime import datetime, timedelta, timezone
    return datetime, hashlib, os, timedelta, timezone


@app.cell
def _(mo):
    student_id_input = mo.ui.text(
        value="stu_e2e_001",
        label="Student ID",
        placeholder="stu_e2e_001",
    )
    source_input = mo.ui.dropdown(
        options=["convex", "synthetic"],
        value="synthetic",
        label="Data source",
    )
    language_input = mo.ui.dropdown(
        options=["en", "ga"],
        value="en",
        label="Label language",
    )
    mo.vstack(
        [
            mo.md("## Inputs"),
            student_id_input,
            source_input,
            language_input,
        ]
    )
    return language_input, source_input, student_id_input


@app.cell
def _():
    SUBJECT_AXES = [
        ("mathematics", "Mathematics", "Matamaitic"),
        ("applied_mathematics", "Applied Maths", "Matamaitic Fheidhmeach"),
        ("chemistry", "Chemistry", "Ceimic"),
        ("geography", "Geography", "Tíreolaíocht"),
        ("history", "History", "Stair"),
        ("english", "English", "Béarla"),
        ("gaeilge", "Gaeilge", "Gaeilge"),
        ("computer_science", "Computer Science", "Ríomheolaíocht"),
    ]
    return (SUBJECT_AXES,)


@app.cell
def _(
    SUBJECT_AXES,
    datetime,
    hashlib,
    source_input,
    student_id_input,
    timedelta,
    timezone,
):
    import pandas as pd

    badges: list[dict] = []
    source = source_input.value
    student_id = student_id_input.value.strip() or "stu_default"

    if source == "convex":
        # The live path: read from the Convex `badges` table.
        # When CONVEX_URL is unset we still fall back to the
        # synthetic dataset (the offline-dev path) so the
        # notebook always renders something.
        try:
            from convex import ConvexClient  # type: ignore

            client = ConvexClient(
                os.environ.get("CONVEX_URL", "http://localhost:3210")
            )
            rows = client.query(
                "badges:listByStudent", {"studentId": student_id}
            )
            for r in rows or []:
                badges.append({
                    "subject": r.get("subject", "unknown"),
                    "date_earned": datetime.fromtimestamp(
                        r.get("dateEarned", 0) / 1000,
                        tz=timezone.utc,
                    ),
                })
        except Exception:
            badges = []

    if not badges:
        # Synthetic dataset: 1 event per subject over the last
        # 8 days, with deterministic ordering so the timeline
        # renders consistently across runs.
        for i, (slug, _en, _ga) in enumerate(SUBJECT_AXES):
            days_ago = 8 - i
            badges.append({
                "subject": slug,
                "date_earned": datetime.now(tz=timezone.utc)
                - timedelta(days=days_ago),
            })
        # A second event for mathematics 2 days ago.
        badges.append({
            "subject": "mathematics",
            "date_earned": datetime.now(tz=timezone.utc)
            - timedelta(days=2),
        })

    df = pd.DataFrame(badges)
    if df.empty:
        df = pd.DataFrame({
            "subject": [s[0] for s in SUBJECT_AXES],
            "date_earned": [datetime.now(tz=timezone.utc)] * len(SUBJECT_AXES),
        })
    df = df.sort_values("date_earned")
    # Cumulative count per subject.
    df["cumulative_count"] = (
        df.groupby("subject").cumcount() + 1
    )
    df
    return df, pd, student_id


@app.cell
def _(mo):
    mo.md("## Per-subject mastery timeline (cumulative count)")
    return (mo,)


@app.cell
def _(SUBJECT_AXES, df, mo, pd, language_input, student_id):
    import altair as alt

    label_field = "ga_label" if language_input.value == "ga" else "en_label"
    subject_labels = {
        slug: {"en_label": en, "ga_label": ga}
        for slug, en, ga in SUBJECT_AXES
    }
    plot_df = df.copy()
    plot_df["label"] = plot_df["subject"].map(
        lambda s: subject_labels.get(s, {}).get(label_field, s)
    )

    chart = (
        alt.Chart(plot_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("date_earned:T", title="Date"),
            y=alt.Y(
                "cumulative_count:Q",
                title="Cumulative badges",
                scale=alt.Scale(domain=[0, 10]),
            ),
            color=alt.Color("label:N", title="Subject"),
            tooltip=["label", "date_earned:T", "cumulative_count:Q"],
        )
        .properties(
            title=f"Per-subject mastery timeline · {student_id}",
            width=720,
            height=320,
        )
        .interactive()
    )
    chart
    return alt, chart, plot_df, subject_labels, label_field


@app.cell
def _(mo):
    mo.md("## Current mastery profile (8-axis spider)")
    return (mo,)


@app.cell
def _(SUBJECT_AXES, df, language_input):
    import math

    axes = SUBJECT_AXES
    label_field = "ga_label" if language_input.value == "ga" else "en_label"
    counts_by_subject = (
        df.groupby("subject").size().to_dict()
    )
    points = []
    for slug, en, ga in axes:
        count = counts_by_subject.get(slug, 0)
        # Mastery score in [0, 100]: 20 per badge, capped at 100.
        score = min(100, count * 20)
        points.append({
            "subject": slug,
            "label": (ga if label_field == "ga_label" else en),
            "score": score,
        })

    n = len(points)
    # Spider chart path: a polygon for the radar.
    angle_step = 2 * math.pi / n
    polygon_pts = []
    for i, p in enumerate(points):
        angle = -math.pi / 2 + i * angle_step
        r = p["score"] / 100.0
        x = 0.5 + 0.4 * r * math.cos(angle)
        y = 0.5 + 0.4 * r * math.sin(angle)
        polygon_pts.append(f"{x:.3f},{y:.3f}")

    spider_svg = (
        f'<svg viewBox="0 0 1 1" width="360" height="360" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'style="background:#0b0f14;color:#e6edf3;">'
    )
    # Concentric grid circles.
    for ring_r in (0.2, 0.4, 0.6, 0.8, 1.0):
        spider_svg += (
            f'<circle cx="0.5" cy="0.5" r="{0.4 * ring_r:.3f}" '
            f'fill="none" stroke="rgba(255,255,255,0.18)" />'
        )
    # Axis labels.
    for i, p in enumerate(points):
        angle = -math.pi / 2 + i * angle_step
        x = 0.5 + 0.46 * math.cos(angle)
        y = 0.5 + 0.46 * math.sin(angle)
        spider_svg += (
            f'<text x="{x:.3f}" y="{y:.3f}" '
            f'font-size="0.04" fill="currentColor" '
            f'text-anchor="middle" alignment-baseline="middle" '
            f'transform="rotate({math.degrees(angle) + 90:.1f} {x:.3f} {y:.3f})">'
            f'{p["label"]}</text>'
        )
    # Polygon.
    spider_svg += (
        f'<polygon points="{" ".join(polygon_pts)}" '
        f'fill="#36d6c0" fill-opacity="0.35" stroke="#36d6c0" />'
    )
    spider_svg += "</svg>"
    spider_svg
    return (
        angle_step,
        axes,
        counts_by_subject,
        label_field,
        math,
        n,
        points,
        polygon_pts,
        spider_svg,
    )


@app.cell
def _(mo, points):
    top = max(points, key=lambda p: p["score"])
    mo.md(
        f"""
        ## Top subject + FIBO emblem cache key

        - **Top subject**: `{top["subject"]}`
        - **Mastery score**: `{top["score"]}`
        - **Emblem cache key** (`top_subject + student_id + seed`):
          see ``/student/<id>/mastery`` route for the real
          Convex-backed lookup.

        The cache key is `(student_id, top["subject"], seed)` where
        ``seed = defaultEmblemSeed(student_id)`` — a stable hash
        that survives SSR/hydration.
        """
    )
    return (top,)


@app.cell
def _(hashlib, student_id, top):
    seed = abs(hash(student_id)) % (10 ** 8) or 1
    emblem_key_hash = hashlib.sha256(
        f"{student_id}|{top['subject']}|{seed}".encode()
    ).hexdigest()[:16]
    emblem_key_hash
    return emblem_key_hash, seed


@app.cell
def _(mo):
    mo.md(
        """
        ## Algorithm reference

        - The cumulative timeline uses
          ``pandas.DataFrame.groupby(...).cumcount()`` — the
          canonical Python implementation of the same logic the
          TypeScript ``/student/<id>/mastery`` route uses
          (the route uses an `O(n)` single-pass loop instead).
        - The spider chart is a static SVG (no Recharts here) so
          the notebook renders standalone without React.
        - The Fibonacci-style mastery ramp (20 per badge, capped
          at 100) is the same curve the React component uses;
          see ``tuatha/web/packages/mastery-chart/src/index.tsx``.
        """
    )
    return (mo,)


if __name__ == "__main__":
    app.run()