// tuatha/baml/qpack_physics.baml — canonical BAML contracts for the NCCA Physics subject.

client minimax

class PhysicsSyllabusTopic {
  ncca_code       string
  title_en        string
  title_ga        string
  description_en  string
  description_ga  string
  level           string
  source_pdf      string
  source_page     int
  provenance_sha256 string
}

class PhysicsPastPaper {
  year         int
  level        string
  paper        int
  paper_url    string
  provenance_sha256 string
}

class PhysicsMarkingScheme {
  lo_code       string
  level         string
  year          int
  scheme_url    string
  criteria      list<string>
  provenance_sha256 string
}

class PhysicsFormativeItem {
  lo_code       string
  difficulty    int
  level         string
  topic         string
  multiple_choice    string
  short_answer       string
  extended_response  string
  evidence_pdfs        list<string>
}

class PhysicsFormativeResponse {
  item_id           string
  student_response  string
  grade             float
  feedback_en       string
  feedback_ga       string
  badge_emitted     bool
  rubric_evidence   list<string>
}


function GeneratePhysicsSyllabus(
  lo_code: string,
  level: string,
  language: string,
  pdf_pages: string,
) -> PhysicsSyllabusTopic {
  client minimax
  prompt #"
    Generate the canonical Physics syllabus topic for LO code { lo_code }
    at level { level } in language { language } from these PDF pages:
    { pdf_pages }
    return a PhysicsSyllabusTopic.
  "#
}

function GeneratePhysicsPastPaper(
  year: int,
  level: string,
  paper: int,
  pdf_pages: string,
) -> PhysicsPastPaper {
  client minimax
  prompt #"
    Generate the canonical Physics past paper for year { year }
    at level { level } paper { paper } from these PDF pages:
    { pdf_pages }
    return a PhysicsPastPaper.
  "#
}

function GeneratePhysicsMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
  pdf_pages: string,
) -> PhysicsMarkingScheme {
  client minimax
  prompt #"
    Generate the canonical Physics marking scheme for LO code
    { lo_code } at level { level } year { year } from these PDF pages:
    { pdf_pages }
    return a PhysicsMarkingScheme.
  "#
}

function GeneratePhysicsFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  pdf_pages: string,
) -> PhysicsFormativeItem {
  client minimax
  prompt #"
    Generate the canonical Physics formative item for LO code
    { lo_code } at difficulty { difficulty } at level { level } topic
    { topic } from these PDF pages:
    { pdf_pages }
    return a PhysicsFormativeItem.
  "#
}

function ScorePhysicsFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
  rubric_text: string,
) -> PhysicsFormativeResponse {
  client minimax
  prompt #"
    Score the Physics response for item_id { item_id } student_response
    { student_response } in format { response_format } with time
    { time_taken_seconds }s and hints { hints_used } against the rubric:
    { rubric_text }
    return a PhysicsFormativeResponse.
  "#
}
