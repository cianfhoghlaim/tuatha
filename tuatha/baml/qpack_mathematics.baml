// tuatha/baml/qpack_mathematics.baml — canonical BAML contracts for the NCCA Mathematics subject.

client minimax

class MathsSyllabusTopic {
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

class MathsPastPaper {
  year         int
  level        string
  paper        int
  paper_url    string
  provenance_sha256 string
}

class MathsMarkingScheme {
  lo_code       string
  level         string
  year          int
  scheme_url    string
  criteria      list<string>
  provenance_sha256 string
}

class MathsFormativeItem {
  lo_code       string
  difficulty    int
  level         string
  topic         string
  multiple_choice    string
  short_answer       string
  extended_response  string
  evidence_pdfs        list<string>
}

class MathsFormativeResponse {
  item_id           string
  student_response  string
  grade             float
  feedback_en       string
  feedback_ga       string
  badge_emitted     bool
  rubric_evidence   list<string>
}


function GenerateMathsSyllabus(
  lo_code: string,
  level: string,
  language: string,
  pdf_pages: string,
) -> MathsSyllabusTopic {
  client minimax
  prompt #"
    Generate the canonical Mathematics syllabus topic for LO code { lo_code }
    at level { level } in language { language } from these PDF pages:
    { pdf_pages }
    return a MathsSyllabusTopic.
  "#
}

function GenerateMathsPastPaper(
  year: int,
  level: string,
  paper: int,
  pdf_pages: string,
) -> MathsPastPaper {
  client minimax
  prompt #"
    Generate the canonical Mathematics past paper for year { year }
    at level { level } paper { paper } from these PDF pages:
    { pdf_pages }
    return a MathsPastPaper.
  "#
}

function GenerateMathsMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
  pdf_pages: string,
) -> MathsMarkingScheme {
  client minimax
  prompt #"
    Generate the canonical Mathematics marking scheme for LO code
    { lo_code } at level { level } year { year } from these PDF pages:
    { pdf_pages }
    return a MathsMarkingScheme.
  "#
}

function GenerateMathsFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  pdf_pages: string,
) -> MathsFormativeItem {
  client minimax
  prompt #"
    Generate the canonical Mathematics formative item for LO code
    { lo_code } at difficulty { difficulty } at level { level } topic
    { topic } from these PDF pages:
    { pdf_pages }
    return a MathsFormativeItem.
  "#
}

function ScoreMathsFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
  rubric_text: string,
) -> MathsFormativeResponse {
  client minimax
  prompt #"
    Score the Mathematics response for item_id { item_id } student_response
    { student_response } in format { response_format } with time
    { time_taken_seconds }s and hints { hints_used } against the rubric:
    { rubric_text }
    return a MathsFormativeResponse.
  "#
}
