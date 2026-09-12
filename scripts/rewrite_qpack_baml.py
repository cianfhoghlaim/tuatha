"""Generate canonical qpack_<subject>.baml files for all 14 subjects.

Per the 2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1
T2.4: rewrite the 14 qpack_<subject>.baml files using the canonical
prompt template from qpack_mathematics.baml.

Pattern:
- BAML prefix: PascalCase subject name (e.g., Chemistry, AppliedMath)
- Class names: <Subject>SyllabusTopic, <Subject>PastPaper, etc.
- Function names: Generate<Subject>Syllabus, etc.
- Client: subject_agent (routes via MODEL_REGISTRY.resolve("text_llm", "subject_agent"))
- LANGUAGE: English only (gaeilge and irish subjects emit bilingual EN + GA)
"""

from __future__ import annotations

import os
from pathlib import Path

BAML_DIR = Path("/Users/cianmacandeisigh/dev/tuatha/tuatha/baml")

# Subject metadata: (slug, display_name, baml_prefix, lo_prefix, gaeilge_flag)
SUBJECTS = [
    ("applied_mathematics", "Applied Mathematics", "AppM", "APPM", False),
    ("chemistry", "Chemistry", "Chemistry", "CHEM", False),
    ("computer_science", "Computer Science", "ComputerScience", "COMP", False),
    ("english", "English", "English", "ENGL", False),
    ("gaeilge", "Gaeilge", "Gaeilge", "GA", True),       # bilingual EN+GA
    ("geography", "Geography", "Geography", "GEOG", False),
    ("history", "History", "History", "HIST", False),
    ("accounting", "Accounting", "Accounting", "ACCT", False),
    ("biology", "Biology", "Biology", "BIOL", False),
    ("business", "Business", "Business", "BUS", False),
    ("french", "French", "French", "FR", False),
    ("irish", "Irish", "Irish", "IR", True),             # bilingual EN+GA
    ("physics", "Physics", "Physics", "PHYS", False),
]


def generate_qpack_baml(
    slug: str, display: str, prefix: str, lo_prefix: str, is_gaeilge: bool
) -> str:
    """Generate the canonical qpack_<subject>.baml content."""
    if is_gaeilge:
        language_guard = (
            "LANGUAGE: {{ language }} — emit feedback in English if "
            '"en", Irish if "ga". For gaeilge/irish subjects, preserve '
            "Irish diacritics (síneadh fada)."
        )
    else:
        language_guard = (
            "LANGUAGE: English only. The title_ga / description_ga "
            "fields are populated when language=\"ga\" AND "
            "subject=\"gaeilge\" (or irish); for {{ subject }}, "
            "English-only."
        )

    return f"""// tuatha/baml/qpack_{slug}.baml — canonical BAML contracts for the NCCA {display} subject.
//
// Rewritten 2026-08-27 to add the canonical prompt template:
// - NCCA LO numbering scheme (LC-{lo_prefix}-LO-<strand>.<index>)
// - Bilingual invariant (English by default; gaeilge/irish keep bilingual)
// - Difficulty 1-5 calibration
// - Evidence_pdfs citation
//
// Routes through `MODEL_REGISTRY.resolve("text_llm", "subject_agent")`.

client<llm> subject_agent {{
  provider "openai-generic"
  base_url env.LITELLM_URL
  api_key  env.LITELLM_API_KEY
  model_name env.TEXT_MODEL_SUBJECT_AGENT
}}

class {prefix}SyllabusTopic {{
  ncca_code       string
  title_en        string
  title_ga        string?
  description_en  string
  description_ga  string?
  level           string                          // "hl" | "ol" | "fl" | "jc"
  strand          string?
  source_pdf      string
  source_page     int
  provenance_sha256 string
}}

class {prefix}PastPaper {{
  year         int
  level        string
  paper        int
  paper_url    string
  questions    string[]?
  lo_tags      string[]?
  provenance_sha256 string
}}

class {prefix}MarkingCriterion {{
  criterion_id     string
  marks            float
  band_description string
  evidence_pdfs    string[]
}}

class {prefix}MarkingScheme {{
  lo_code       string
  level         string
  year          int
  scheme_url    string
  criteria      {prefix}MarkingCriterion[]
  provenance_sha256 string
}}

class {prefix}FormativeItem {{
  lo_code       string
  difficulty    int
  level         string
  topic         string
  prompt_en     string
  prompt_ga     string?
  expected_answer string
  marking_scheme  {prefix}MarkingCriterion[]
  evidence_pdfs   string[]
}}

class {prefix}FormativeResponse {{
  item_id           string
  student_response  string
  grade             float
  feedback_en       string
  feedback_ga       string?
  badge_emitted     bool
  rubric_evidence   string[]
  flagged_for_review bool
}}


function Generate{prefix}Syllabus(
  lo_code: string,
  level: string,
  language: string,
  pdf_pages: string,
) -> {prefix}SyllabusTopic {{
  client subject_agent
  prompt #"
    You are the canonical {display} syllabus topic generator for the
    NCCA Leaving Certificate + Junior Cycle.

    Target Learning Outcome: {{ lo_code }}
    Level: {{ level }}
    {language_guard}

    PDF pages (cite source_pdf + source_page in your evidence):
    {{ pdf_pages }}

    NCCA LO NUMBERING: LC-{lo_prefix}-LO-<strand>.<index>
    Junior Cycle: JC-{lo_prefix}-LO-<strand>.<index>

    Return a {prefix}SyllabusTopic matching the schema.
  "#
}}

function Generate{prefix}PastPaper(
  year: int,
  level: string,
  paper: int,
  pdf_pages: string,
) -> {prefix}PastPaper {{
  client subject_agent
  prompt #"
    You are the canonical {display} past paper extractor.

    Year: {{ year }}, Level: {{ level }}, Paper: {{ paper }}.

    PDF pages:
    {{ pdf_pages }}

    For each question, tag with: topic + NCCA LO code
    (LC-{lo_prefix}-LO-<strand>.<index>).

    LANGUAGE: English only.

    Return a {prefix}PastPaper matching the schema.
  "#
}}

function Generate{prefix}MarkingScheme(
  lo_code: string,
  level: string,
  year: int,
  pdf_pages: string,
) -> {prefix}MarkingScheme {{
  client subject_agent
  prompt #"
    You are the canonical {display} marking scheme generator.

    Target Learning Outcome: {{ lo_code }}
    Level: {{ level }}, Year: {{ year }}.

    PDF pages (cite source_pdf + source_page for each criterion):
    {{ pdf_pages }}

    Per-criterion breakdown:
    - criterion_id
    - marks (float)
    - band_description (what earns full / partial / zero marks)
    - evidence_pdfs (source_pdf + source_page citations)

    LANGUAGE: English only.

    Return a {prefix}MarkingScheme matching the schema.
  "#
}}

function Generate{prefix}FormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  marking_scheme: string,
  prior_items: string[],
  language: string,
  pdf_pages: string,
) -> {prefix}FormativeItem {{
  client subject_agent
  prompt #"
    You are the canonical formative item generator for the NCCA
    {{ level }} {display} syllabus.

    Target Learning Outcome: {{ lo_code }} — "{{ topic }}"
    Difficulty: {{ difficulty }}/5
      1 = recall (definitions, formulas)
      2 = 1-step application
      3 = 2-3 step analysis
      4 = multi-step synthesis
      5 = evaluation / proof / extended response

    Available marking scheme (cite this):
    {{ marking_scheme }}

    Prior items (avoid duplicating):
    {{ prior_items }}

    PDF pages (cite source_pdf + source_page in your evidence_pdfs):
    {{ pdf_pages }}

    {language_guard}

    Generate the item in 4 PARTS:
    1. PROMPT: a single self-contained question that can be
       answered in 10-15 minutes.
    2. EXPECTED ANSWER: a worked solution + the answer's
       mark-bearing steps.
    3. MARKING SCHEME: mirror the marking_scheme above; per-criterion
       marks; cite source PDF + page.
    4. EVIDENCE: every part MUST cite source_pdf + source_page
       from the PDF pages.

    Return a {prefix}FormativeItem matching the schema.
  "#
}}

function Score{prefix}FormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
  rubric_text: string,
) -> {prefix}FormativeResponse {{
  client subject_agent
  prompt #"
    You are the canonical {display} response scorer.

    item_id: {{ item_id }}
    student_response: {{ student_response }}
    format: {{ response_format }}
    time_taken: {{ time_taken_seconds }}s
    hints_used: {{ hints_used }}

    Rubric:
    {{ rubric_text }}

    Apply the 4-STEP scoring:
    1. CITE: identify which marking criteria are met.
    2. BAND: assign marks per criterion.
    3. SUMMARISE: total marks + feedback.
    4. FLAG: set flagged_for_review=true if confidence < 0.7.

    LANGUAGE: English only.

    Return a {prefix}FormativeResponse matching the schema.
  "#
}}
"""


def main() -> None:
    """Generate all 13 qpack_<subject>.baml files (skip mathematics, already done)."""
    written: list[str] = []
    for slug, display, prefix, lo_prefix, is_gaeilge in SUBJECTS:
        target = BAML_DIR / f"qpack_{slug}.baml"
        content = generate_qpack_baml(slug, display, prefix, lo_prefix, is_gaeilge)
        target.write_text(content)
        written.append(str(target))
        print(f"Wrote {target}")
    print(f"\nTotal: {len(written)} files rewritten.")


if __name__ == "__main__":
    main()
