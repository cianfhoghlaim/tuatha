"""Refactor the 8 NCCA subject agents to use bind_subject_tools.

Per the 2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1
T1.7: collapse the 5-stub-module pattern (40 stub files in
tuatha/tools/) into the single `bind_subject_tools(<subject>)`
pattern from corpus_tools.py.
"""

from __future__ import annotations

import re
from pathlib import Path

AGENTS_DIR = Path("/Users/cianmacandeisigh/dev/tuatha/tuatha/subjects")


# Subject slugs → variable prefix used in FunctionTool names + tool imports.
SUBJECT_TOOLS = {
    "mathematics": (
        "math",
        [
            "from ..tools.mathematics_syllabus_lookup import lookup_math_lo",
            "from ..tools.mathematics_past_paper_lookup import lookup_math_paper",
            "from ..tools.mathematics_marking_scheme_lookup import lookup_math_marking_scheme",
            "from ..tools.mathematics_formative_item_generate import generate_math_item",
            "from ..tools.mathematics_response_score import score_math_response",
        ],
    ),
    "applied_mathematics": (
        "appm",
        [
            "from ..tools.applied_mathematics_syllabus_lookup import lookup_appm_lo",
            "from ..tools.applied_mathematics_past_paper_lookup import lookup_appm_paper",
            "from ..tools.applied_mathematics_marking_scheme_lookup import lookup_appm_marking_scheme",
            "from ..tools.applied_mathematics_formative_item_generate import generate_appm_item",
            "from ..tools.applied_mathematics_response_score import score_appm_response",
        ],
    ),
    "chemistry": (
        "chem",
        [
            "from ..tools.chemistry_syllabus_lookup import lookup_chem_lo",
            "from ..tools.chemistry_past_paper_lookup import lookup_chem_paper",
            "from ..tools.chemistry_marking_scheme_lookup import lookup_chem_marking_scheme",
            "from ..tools.chemistry_formative_item_generate import generate_chem_item",
            "from ..tools.chemistry_response_score import score_chem_response",
        ],
    ),
    "computer_science": (
        "comp",
        [
            "from ..tools.computer_science_syllabus_lookup import lookup_comp_lo",
            "from ..tools.computer_science_past_paper_lookup import lookup_comp_paper",
            "from ..tools.computer_science_marking_scheme_lookup import lookup_comp_marking_scheme",
            "from ..tools.computer_science_formative_item_generate import generate_comp_item",
            "from ..tools.computer_science_response_score import score_comp_response",
        ],
    ),
    "english": (
        "engl",
        [
            "from ..tools.english_syllabus_lookup import lookup_engl_lo",
            "from ..tools.english_past_paper_lookup import lookup_engl_paper",
            "from ..tools.english_marking_scheme_lookup import lookup_engl_marking_scheme",
            "from ..tools.english_formative_item_generate import generate_engl_item",
            "from ..tools.english_response_score import score_engl_response",
        ],
    ),
    "gaeilge": (
        "gael",
        [
            "from ..tools.gaeilge_syllabus_lookup import lookup_gael_lo",
            "from ..tools.gaeilge_past_paper_lookup import lookup_gael_paper",
            "from ..tools.gaeilge_marking_scheme_lookup import lookup_gael_marking_scheme",
            "from ..tools.gaeilge_formative_item_generate import generate_gael_item",
            "from ..tools.gaeilge_response_score import score_gael_response",
        ],
    ),
    "geography": (
        "geog",
        [
            "from ..tools.geography_syllabus_lookup import lookup_geog_lo",
            "from ..tools.geography_past_paper_lookup import lookup_geog_paper",
            "from ..tools.geography_marking_scheme_lookup import lookup_geog_marking_scheme",
            "from ..tools.geography_formative_item_generate import generate_geog_item",
            "from ..tools.geography_response_score import score_geog_response",
        ],
    ),
    "history": (
        "hist",
        [
            "from ..tools.history_syllabus_lookup import lookup_hist_lo",
            "from ..tools.history_past_paper_lookup import lookup_hist_paper",
            "from ..tools.history_marking_scheme_lookup import lookup_hist_marking_scheme",
            "from ..tools.history_formative_item_generate import generate_hist_item",
            "from ..tools.history_response_score import score_hist_response",
        ],
    ),
}


def refactor_subject_agent(slug: str) -> str:
    """Return the refactored content for one subject agent."""
    var_prefix, old_imports = SUBJECT_TOOLS[slug]
    path = AGENTS_DIR / f"{slug}.py"
    with path.open() as f:
        content = f.read()

    # Step 1: strip the 5 tool imports.
    for old_import in old_imports:
        content = content.replace(f"{old_import}\n", "")

    # Step 2: add the corpus_tools import (if not already present).
    corpus_import = "from ..tools.corpus_tools import bind_subject_tools"
    if corpus_import not in content:
        last_import_idx = max(
            content.rfind("from .."),
            content.rfind("from google"),
        )
        end_of_imports = content.find("\n\n", last_import_idx)
        content = (
            content[:end_of_imports]
            + f"\n{corpus_import}"
            + content[end_of_imports:]
        )

    # Step 3: replace the 5 FunctionTool definitions with a single block.
    new_block = (
        f"# The 5 per-subject tools, bound via bind_subject_tools.\n"
        f"_bound_tools = bind_subject_tools(\"{slug}\")\n"
        f"{var_prefix}_syllabus_lookup_tool = FunctionTool(func=_bound_tools[0])\n"
        f"{var_prefix}_past_paper_lookup_tool = FunctionTool(func=_bound_tools[1])\n"
        f"{var_prefix}_marking_scheme_lookup_tool = FunctionTool(func=_bound_tools[2])\n"
        f"{var_prefix}_formative_item_generate_tool = FunctionTool(func=_bound_tools[3])\n"
        f"{var_prefix}_response_score_tool = FunctionTool(func=_bound_tools[4])\n"
    )

    # Find and replace the 5 FunctionTool definitions (one block).
    pattern = re.compile(
        rf"# The 5 per-subject tools\.\n"
        rf"{var_prefix}_syllabus_lookup_tool = FunctionTool\(func=lookup_{var_prefix}_lo\)\n"
        rf"{var_prefix}_past_paper_lookup_tool = FunctionTool\(func=lookup_{var_prefix}_paper\)\n"
        rf"{var_prefix}_marking_scheme_lookup_tool = FunctionTool\(func=lookup_{var_prefix}_marking_scheme\)\n"
        rf"{var_prefix}_formative_item_generate_tool = FunctionTool\(func=generate_{var_prefix}_item\)\n"
        rf"{var_prefix}_response_score_tool = FunctionTool\(func=score_{var_prefix}_response\)\n",
        re.MULTILINE,
    )
    content = pattern.sub(new_block, content)

    # Step 4: remove the unused per-tool @trace_agent wrappers
    # (they were duplicating the canonical tool calls).
    wrapper_pattern = re.compile(
        rf"@trace_agent\(\"{slug}\"\)\n"
        rf"async def _{var_prefix}_extract_\w+\(\*args: Any, \*\*kwargs: Any\) -> Any:\n"
        rf"    return await \w+\(\*args, \*\*kwargs\)\n\n",
        re.MULTILINE,
    )
    content = wrapper_pattern.sub("", content)
    return content


def main() -> None:
    """Refactor all 8 subject agents."""
    for slug in SUBJECT_TOOLS:
        path = AGENTS_DIR / f"{slug}.py"
        original = path.read_text()
        refactored = refactor_subject_agent(slug)
        if refactored == original:
            print(f"NO CHANGE: {path}")
        else:
            path.write_text(refactored)
            print(f"REFACTORED: {path}")


if __name__ == "__main__":
    main()
