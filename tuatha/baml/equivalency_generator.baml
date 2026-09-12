// tuatha/baml/equivalency_generator.baml — the canonical BAML contracts for the Cross-Jurisdiction Equivalency Generator.
//
// Rewritten 2026-08-27 to add EquivalencyRow + EquivalencyTable
// classes + the Equivgen function with a 3-step ALIGN → CLASSIFY
// → FLAG-GAPS loop. Enables the EquivalencyConsistencyTrajectoryEvaluator
// observation eval.
//
// Routes through `MODEL_REGISTRY.resolve("text_llm", "hackathon_agent")`.

client<llm> hackathon_agent {
  provider "openai-generic"
  base_url env.LITELLM_URL
  api_key  env.LITELLM_API_KEY
  model_name env.TEXT_MODEL_HACKATHON_AGENT
}

enum Jurisdiction {
  NCCA
  AQA
  SQA
  WJEC
  CCEA
  IoM
}

enum DepthEstimate {
  Introductory
  Intermediate
  Advanced
  Unknown
}

enum AssessmentStyle {
  ExamOnly
  Coursework
  Both
  Unknown
}

class EquivalencyRow {
  jurisdiction        Jurisdiction
  level               string                  // "LC" | "GCSE" | "A-Level" | "Higher"
  lo_code             string                  // jurisdiction-native LO code
  lo_title_en         string
  lo_title_ga         string?
  topics              string[]
  depth_estimate      DepthEstimate
  assessment_style    AssessmentStyle
}

class EquivalencyTable {
  subject             string
  rows                EquivalencyRow[]
  gaps                string[]                // topics covered in <3 of 6 jurisdictions
  notes_en            string
  notes_ga            string?
  confidence          float                   // 0.0-1.0
}

function Equivgen(
  subject: string,
  jurisdictions: Jurisdiction[],
  level: string,                                 // "LC" | "GCSE" | "A-Level"
  syllabus_corpus: string,                       // JSON-encoded dict of jurisdiction → syllabus text
) -> EquivalencyTable {
  client hackathon_agent
  prompt #"
    You are the canonical Cross-Jurisdiction Equivalency Generator.

    Subject: {{ subject }} at level {{ level }}.
    Jurisdictions to compare: {{ jurisdictions }}.

    Syllabus corpus (per jurisdiction):
    {{ syllabus_corpus }}

    For each jurisdiction, list the 5-15 closest Learning Outcomes.
    Identify the cross-jurisdiction mapping.

    Apply the 3-STEP COMPARISON:

    1. ALIGN: for each LC NCCA LO, find the closest AQA + SQA +
       WJEC + CCEA + IoM LO.

    2. CLASSIFY: depth_estimate + assessment_style per row.

    3. FLAG GAPS: topics covered in < 3 of 6 jurisdictions are
       gaps (list them in `gaps`).

    LANGUAGE: English only (unless subject="gaeilge", then emit
    bilingual EN + GA notes_ga).

    Return an EquivalencyTable matching the schema.
  "#
}

test equivgen_mathematics_lc_vs_a_level {
  functions [Equivgen]
  input {
    subject "mathematics"
    jurisdictions [Jurisdiction::NCCA, Jurisdiction::AQA]
    level "LC"
    syllabus_corpus "{...}"
  }
  output {
    subject "mathematics"
    confidence 0.85
  }
}
