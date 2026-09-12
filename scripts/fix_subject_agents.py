"""Fix the remaining 7 subject agents where the refactor missed the
FunctionTool block replacement.

The first refactor pass:
- Removed the imports (✅ for all 8)
- Removed the @trace_agent wrappers (✅ for all 8)
- Replaced the FunctionTool block (✅ only for mathematics — the others
  had different comment text "# Per-tool extraction wrappers emit the
  canonical `agent.<subject>.extract` Langfuse trace. The wrappers..."
  instead of "# The 5 per-subject tools.")

This script does the FunctionTool block replacement as a separate pass
that doesn't require a comment prefix.
"""

from __future__ import annotations

import re
from pathlib import Path

AGENTS_DIR = Path("/Users/cianmacandeisigh/dev/tuatha/tuatha/subjects")

SUBJECTS = {
    "applied_mathematics": "appm",
    "chemistry": "chem",
    "computer_science": "comp",
    "english": "engl",
    "gaeilge": "gael",
    "geography": "geog",
    "history": "hist",
}


def fix_subject_agent(slug: str, var_prefix: str) -> str:
    """Fix one subject agent by replacing the 5 FunctionTool definitions."""
    path = AGENTS_DIR / f"{slug}.py"
    content = path.read_text()

    new_block = (
        f"# The 5 per-subject tools, bound via bind_subject_tools.\n"
        f"_bound_tools = bind_subject_tools(\"{slug}\")\n"
        f"{var_prefix}_syllabus_lookup_tool = FunctionTool(func=_bound_tools[0])\n"
        f"{var_prefix}_past_paper_lookup_tool = FunctionTool(func=_bound_tools[1])\n"
        f"{var_prefix}_marking_scheme_lookup_tool = FunctionTool(func=_bound_tools[2])\n"
        f"{var_prefix}_formative_item_generate_tool = FunctionTool(func=_bound_tools[3])\n"
        f"{var_prefix}_response_score_tool = FunctionTool(func=_bound_tools[4])\n"
    )

    # Match the 5 FunctionTool definitions, regardless of preceding comment.
    pattern = re.compile(
        rf"{var_prefix}_syllabus_lookup_tool = FunctionTool\(func=lookup_{var_prefix}_lo\)\n"
        rf"{var_prefix}_past_paper_lookup_tool = FunctionTool\(func=lookup_{var_prefix}_paper\)\n"
        rf"{var_prefix}_marking_scheme_lookup_tool = FunctionTool\(func=lookup_{var_prefix}_marking_scheme\)\n"
        rf"{var_prefix}_formative_item_generate_tool = FunctionTool\(func=generate_{var_prefix}_item\)\n"
        rf"{var_prefix}_response_score_tool = FunctionTool\(func=score_{var_prefix}_response\)\n",
        re.MULTILINE,
    )
    new_content, n_subs = pattern.subn(new_block, content)
    return new_content, n_subs


def main() -> None:
    for slug, var_prefix in SUBJECTS.items():
        path = AGENTS_DIR / f"{slug}.py"
        original = path.read_text()
        refactored, n_subs = fix_subject_agent(slug, var_prefix)
        if n_subs == 0:
            print(f"NO MATCH: {path}")
        else:
            path.write_text(refactored)
            print(f"FIXED ({n_subs} subs): {path}")


if __name__ == "__main__":
    main()
