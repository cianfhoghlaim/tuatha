// tuatha/baml/adaptive_tutor.baml — the canonical BAML contracts for the Adaptive Tutor.
//
// Rewritten 2026-08-27 to add TutorState + TutorAction + TutorResponse
// classes + the Adapttutor function with a 5-step CLASSIFY →
// DIAGNOSE → ADAPT → GENERATE → CITE loop. Enables the
// AdaptiveTutorRelevanceTrajectoryEvaluator observation eval.
//
// Routes through `MODEL_REGISTRY.resolve("text_llm", "hackathon_agent")`.

client<llm> hackathon_agent {
  provider "openai-generic"
  base_url env.LITELLM_URL
  api_key  env.LITELLM_API_KEY
  model_name env.TEXT_MODEL_HACKATHON_AGENT
}

// The 6 canonical jurisdictions (per the 2026-08-27 fix).
// Standardised from DESC (deprecated) → IoM (per the
// curriculum_change_sensor.py + the 2026-08-26 openspec change).

enum Jurisdiction {
  NCCA   // Ireland — National Council for Curriculum and Assessment
  AQA    // England — Assessment and Qualifications Alliance
  SQA    // Scotland — Scottish Qualifications Authority
  WJEC   // Wales — Welsh Joint Education Committee
  CCEA   // Northern Ireland — Council for the Curriculum, Examinations and Assessment
  IoM    // Isle of Man — Manx Examinations Board
}

// The 6 tutor action types — the canonical action taxonomy.

enum TutorActionType {
  ExplainConcept
  GiveExample
  DrillProblem
  ReviewPastPaper
  Summarise
  SwitchJurisdiction
}

class Attempt {
  item_id             string
  marks_awarded       float
  marks_available     float
  timestamp           string                    // ISO-8601 UTC
  feedback            string
}

class TutorState {
  student_id              string
  jurisdiction            Jurisdiction
  subject                 string
  topic                   string
  current_difficulty      int                     // 1-5
  mastery_score           float                   // 0.0-1.0 (EMA over recent attempts)
  recent_attempts         Attempt[]
  blocked_lo              string[]                // LOs where mastery_score < 0.5
}

class TutorAction {
  action_type             TutorActionType
  target_lo               string?
  difficulty              int?                    // 1-5
  payload_en              string
  payload_ga              string?
  source_evidence         string[]                // source_pdf_page references
}

class TutorResponse {
  state                   TutorState
  next_action             TutorAction
  reasoning               string                  // bilingual: why this action
  alternative_actions     TutorAction[]
}

function Adapttutor(
  student_input: string,
  tutor_state: TutorState,
  jurisdiction: Jurisdiction,
  reference_data: string,                         // the jurisdiction's syllabus content
) -> TutorResponse {
  client hackathon_agent
  prompt #"
    You are the canonical Adaptive Tutor for the British Isles MMO.
    The student is in jurisdiction={{ jurisdiction }} working on
    {{ tutor_state.subject }}.

    Current state:
    - Topic: {{ tutor_state.topic }}
    - Difficulty: {{ tutor_state.current_difficulty }}/5
    - Mastery: {{ tutor_state.mastery_score:.2f }}
    - Blocked LOs: {{ tutor_state.blocked_lo }}

    Recent attempts: {{ tutor_state.recent_attempts }}

    Student input: "{{ student_input }}"

    Reference (the {{ jurisdiction }} syllabus content): {{ reference_data }}

    LANGUAGE: English by default; Irish when jurisdiction=NCCA AND subject=gaeilge.

    Apply the 5-STEP TUTOR LOOP:

    1. CLASSIFY: is this a question, an attempt, a request for
       review, or a meta-question about progress?

    2. DIAGNOSE: if it's an attempt, run MarkGrade against the
       reference_data rubric (cite source PDF + page).

    3. ADAPT: if mastery < 0.5, lower difficulty by 1 and switch
       action_type to "ExplainConcept".
       If mastery > 0.8, raise difficulty by 1 and switch to
       "DrillProblem".
       Otherwise maintain.

    4. GENERATE: produce the next action with full payload
       (English by default; Irish when jurisdiction=NCCA AND
       subject=gaeilge). Cite the source PDF + page for every
       payload claim.

    5. CITE: every payload MUST reference source PDF + page from
       the reference_data.

    STATE PERSISTENCE: return the new TutorState so the
    orchestrator can persist it.

    Return a TutorResponse matching the schema.
  "#
}

test adapttutor_math_mastery_low {
  functions [Adapttutor]
  input {
    student_input "I don't understand quadratic equations"
    tutor_state {
      student_id "test-001"
      jurisdiction Jurisdiction::NCCA
      subject "mathematics"
      topic "quadratic equations"
      current_difficulty 3
      mastery_score 0.35
      recent_attempts []
      blocked_lo ["LC-MATHS-LO-2.4"]
    }
    jurisdiction Jurisdiction::NCCA
    reference_data "LC Mathematics syllabus — Strand 2: Complex numbers; LO 2.4: solve quadratic equations..."
  }
  output {
    next_action {
      action_type TutorActionType::ExplainConcept
      difficulty 2
      payload_en "Let's break down quadratic equations..."
    }
  }
}
