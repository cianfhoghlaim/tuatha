// tuatha/baml/marking_grader.baml — the canonical BAML contracts for the Marking Grader.
//
// Rewritten 2026-08-27 to add RubricBand + MarkingCriterion + GradingResult
// classes + the MarkGrade function with a 4-step CITE → BAND →
// SUMMARISE → FEEDBACK loop. Enables the
// MarkingAccuracyTrajectoryEvaluator + FeedbackQualityTrajectoryEvaluator
// observation evals.
//
// Routes through `MODEL_REGISTRY.resolve("text_llm", "hackathon_agent")`.

client<llm> hackathon_agent {
  provider "openai-generic"
  base_url env.LITELLM_URL
  api_key  env.LITELLM_API_KEY
  model_name env.TEXT_MODEL_HACKATHON_AGENT
}

// The canonical NCCA + adjacent grade bands.
// HL = Higher Level, OL = Ordinary Level, FL = Foundation Level.

enum GradeBand {
  HL1   // 90-100% — Exceptional
  HL2   // 80-89%  — Very Strong
  HL3   // 70-79%  — Strong
  HL4   // 60-69%  — Above Average
  HL5   // 50-59%  — Average
  HL6   // 40-49%  — Below Average
  HL7   // 30-39%  — Weak
  HL8   // 0-29%   — Very Weak
  OL1
  OL2
  OL3
  OL4
  OL5
  OL6
  OL7
  OL8
  FL1
  FL2
  FL3
  Unknown
}

class RubricBand {
  band_code           GradeBand
  min_marks           float
  max_marks           float
  descriptor_en       string
  descriptor_ga       string?
  typical_evidence    string[]
}

class MarkingCriterion {
  criterion_id        string
  lo_code             string                       // NCCA LO numbering scheme (e.g. LC-MATHS-LO-2.4)
  marks               float
  band_description    string                       // what earns full / partial / zero marks
  evidence_pdfs       string[]                     // source_pdf + source_page citations
}

class CriterionScore {
  criterion_id            string
  marks_awarded           float
  marks_available         float
  justification_en        string
  justification_ga        string?
  evidence_source_pdfs    string[]
}

class GradingResult {
  student_response_id    string
  lo_code                string
  total_marks            float
  max_marks              float
  band_code              GradeBand
  per_criterion          CriterionScore[]
  feedback_en            string
  feedback_ga            string?
  rubric_evidence        string[]                // source_pdf_page references
  confidence             float                   // 0.0 - 1.0
  flagged_for_review     bool                    // true if confidence < 0.7 OR discrepancy > 0.2
}

function MarkGrade(
  student_response: string,
  marking_scheme: MarkingCriterion[],
  rubric_bands: RubricBand[],
  level: string,                                // "hl" | "ol" | "fl"
  language: string,                             // "en" | "ga"
  lo_code: string,                              // NCCA LO numbering
) -> GradingResult {
  client hackathon_agent
  prompt #"
    You are the canonical Marking Grader for the {{ level }} {{ lo_code }}
    formative item (NCCA Leaving Certificate / Junior Cycle / Foundation).

    Student response:
    {{ student_response }}

    Marking scheme (NCCA {{ level }} {{ lo_code }}):
    {{ marking_scheme }}

    Rubric bands (HL1-HL8 + OL1-OL8 + FL1-FL3):
    {{ rubric_bands }}

    LANGUAGE: {{ language }} — emit feedback in English if "en", Irish if "ga".
    For gaeilge, preserve Irish diacritics (síneadh fada).

    Apply the rubric in 4 STEPS:

    1. CITE: identify which marking criteria are met by the response
       (cite source PDF + page from the marking_scheme).

    2. BAND: assign each criterion a mark from 0 to marks_available
       based on the band descriptors.

    3. SUMMARISE: total marks + band code + per-criterion breakdown.

    4. FEEDBACK: write personalised feedback that
       - names what the student did well (cite criterion)
       - names what they missed (cite criterion)
       - gives 1-2 next steps

    CONFIDENCE GATE: if any criterion's evidence is ambiguous, set
    flagged_for_review=true and confidence < 0.7.

    RULES:
    - Do NOT invent evidence. Every per_criterion.evidence_source_pdfs
      entry MUST come from marking_scheme.
    - Do NOT exceed max_marks. Total marks <= sum of marks_available.
    - Use the canonical NCCA grade band code (HL1-HL8 for Higher Level,
      OL1-OL8 for Ordinary Level, FL1-FL3 for Foundation Level).

    Return a GradingResult matching the schema.
  "#
}

test markgrade_math_hl1 {
  functions [MarkGrade]
  input {
    student_response "x = (-b ± √(b²-4ac)) / 2a — derived via completing the square from ax² + bx + c = 0"
    marking_scheme []
    rubric_bands []
    level "hl"
    language "en"
    lo_code "LC-MATHS-LO-2.4"
  }
  output {
    student_response_id "test-math-hl1-001"
    lo_code "LC-MATHS-LO-2.4"
    band_code GradeBand::HL1
    confidence 0.95
    flagged_for_review false
  }
}
