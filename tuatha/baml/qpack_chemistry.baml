// tuatha/baml/qpack_chemistry.baml — canonical BAML contracts for the NCCA Chemistry subject.
//
// Rewritten 2026-08-27 to add the canonical prompt template:
// - NCCA LO numbering scheme (LC-CHEM-LO-<strand>.<index>)
// - Bilingual invariant (English by default; gaeilge/irish keep bilingual)
// - Difficulty 1-5 calibration
// - Evidence_pdfs citation
//
// Routes through `MODEL_REGISTRY.resolve("text_llm", "subject_agent")`.

client<llm> subject_agent {
  provider "openai-generic"
  base_url env.LITELLM_URL
  api_key  env.LITELLM_API_KEY
  model_name env.TEXT_MODEL_SUBJECT_AGENT
}

class ChemistrySyllabusTopic {
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
}

class ChemistryPastPaper {
  year         int
  level        string
  paper        int
  paper_url    string
  questions    string[]?
  lo_tags      string[]?
  provenance_sha256 string
}

class ChemistryMarkingCriterion {
  criterion_id     string
  marks            float
  band_description string
  evidence_pdfs    string[]
}

class ChemistryMarkingScheme {
  lo_code       string
  level         string
  year          int
  scheme_url    string
  criteria      ChemistryMarkingCriterion[]
  provenance_sha256 string
}

class ChemistryFormativeItem {
  lo_code       string
  difficulty    int
  level         string
  topic         string
  prompt_en     string
  prompt_ga     string?
  expected_answer string
  marking_scheme  ChemistryMarkingCriterion[]
  evidence_pdfs   string[]
}

class ChemistryFormativeResponse {
  item_id           string
  student_response  string
  grade             float
  feedback_en       string
  feedback_ga       string?
  badge_emitted     bool
  rubric_evidence   string[]
  flagged_for_review bool
}


function GenerateChemistrySyllabus(
  lo_code: string,
  level: string,
  language: string,
  pdf_pages: string,
) -> ChemistrySyllabusTopic {
  client subject_agent
  prompt #"
    You are the canonical Chemistry syllabus topic generator for the
    NCCA Leaving Certificate + Junior Cycle.

    Target Learning Outcome: { lo_code }
    Level: { level }
    LANGUAGE: English only. The title_ga / description_ga fields are populated when language="ga" AND subject="gaeilge" (or irish); for {{ subject }}, English-only.

    PDF pages (cite source_pdf + source_page in your evidence):
    { pdf_pages }

    NCCA LO NUMBERING: LC-CHEM-LO-<strand>.<index>
    Junior Cycle: JC-CHEM-LO-<strand>.<index>

    Return a ChemistrySyllabusTopic matching the schema.
  "#
}

function GenerateChemistryPastPaper(
  year: int,
  level: string,
  paper: int,
  pdf_pages: string,
) -> ChemistryPastPaper {
  client subject_agent
  prompt #"
    You are the canonical Chemistry past paper extractor.

    Year: { year }, Level: { level }, Paper: { paper }.

    PDF pages:
    { pdf_pages }

    For each question, tag with: topic + NCCA LO code
    (LC-CHEM-LO-<strand>.<index>).

    LANGUAGE: English only.

    Return a ChemistryPastPaper matching the schema.
  "#
}

function GenerateChemistryMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
  pdf_pages: string,
) -> ChemistryMarkingScheme {
  client subject_agent
  prompt #"
    You are the canonical Chemistry marking scheme generator.

    Target Learning Outcome: { lo_code }
    Level: { level }, Year: { year }.

    PDF pages (cite source_pdf + source_page for each criterion):
    { pdf_pages }

    Per-criterion breakdown:
    - criterion_id
    - marks (float)
    - band_description (what earns full / partial / zero marks)
    - evidence_pdfs (source_pdf + source_page citations)

    LANGUAGE: English only.

    Return a ChemistryMarkingScheme matching the schema.
  "#
}

function GenerateChemistryFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  marking_scheme: string,
  prior_items: string[],
  language: string,
  pdf_pages: string,
) -> ChemistryFormativeItem {
  client subject_agent
  prompt #"
    You are the canonical formative item generator for the NCCA
    { level } Chemistry syllabus.

    Target Learning Outcome: { lo_code } — "{ topic }"
    Difficulty: { difficulty }/5
      1 = recall (definitions, formulas)
      2 = 1-step application
      3 = 2-3 step analysis
      4 = multi-step synthesis
      5 = evaluation / proof / extended response

    Available marking scheme (cite this):
    { marking_scheme }

    Prior items (avoid duplicating):
    { prior_items }

    PDF pages (cite source_pdf + source_page in your evidence_pdfs):
    { pdf_pages }

    LANGUAGE: English only. The title_ga / description_ga fields are populated when language="ga" AND subject="gaeilge" (or irish); for {{ subject }}, English-only.

    Generate the item in 4 PARTS:
    1. PROMPT: a single self-contained question that can be
       answered in 10-15 minutes.
    2. EXPECTED ANSWER: a worked solution + the answer's
       mark-bearing steps.
    3. MARKING SCHEME: mirror the marking_scheme above; per-criterion
       marks; cite source PDF + page.
    4. EVIDENCE: every part MUST cite source_pdf + source_page
       from the PDF pages.

    Return a ChemistryFormativeItem matching the schema.
  "#
}

function ScoreChemistryFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
  rubric_text: string,
) -> ChemistryFormativeResponse {
  client subject_agent
  prompt #"
    You are the canonical Chemistry response scorer.

    item_id: { item_id }
    student_response: { student_response }
    format: { response_format }
    time_taken: { time_taken_seconds }s
    hints_used: { hints_used }

    Rubric:
    { rubric_text }

    Apply the 4-STEP scoring:
    1. CITE: identify which marking criteria are met.
    2. BAND: assign marks per criterion.
    3. SUMMARISE: total marks + feedback.
    4. FLAG: set flagged_for_review=true if confidence < 0.7.

    LANGUAGE: English only.

    Return a ChemistryFormativeResponse matching the schema.
  "#
}
