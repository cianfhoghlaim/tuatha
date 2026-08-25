// tuatha/baml/qpack_computer_science.baml — canonical BAML contracts for the NCCA Computer Science subject.

client minimax

class CSSyllabusTopic {
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

class CSPastPaper {
  year         int
  level        string
  paper        int
  paper_url    string
  provenance_sha256 string
}

class CSMarkingScheme {
  lo_code       string
  level         string
  year          int
  scheme_url    string
  criteria      list<string>
  provenance_sha256 string
}

class CSFormativeItem {
  lo_code       string
  difficulty    int
  level         string
  topic         string
  multiple_choice    string
  short_answer       string
  extended_response  string
  evidence_pdfs        list<string>
}

class CSFormativeResponse {
  item_id           string
  student_response  string
  grade             float
  feedback_en       string
  feedback_ga       string
  badge_emitted     bool
  rubric_evidence   list<string>
}


function GenerateCSSyllabus(
  lo_code: string,
  level: string,
  language: string,
  pdf_pages: string,
) -> CSSyllabusTopic {
  client minimax
  prompt #"
    Generate the canonical Computer Science syllabus topic for LO code { lo_code }
    at level { level } in language { language } from these PDF pages:
    { pdf_pages }
    return a CSSyllabusTopic.
  "#
}

function GenerateCSPastPaper(
  year: int,
  level: string,
  paper: int,
  pdf_pages: string,
) -> CSPastPaper {
  client minimax
  prompt #"
    Generate the canonical Computer Science past paper for year { year }
    at level { level } paper { paper } from these PDF pages:
    { pdf_pages }
    return a CSPastPaper.
  "#
}

function GenerateCSMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
  pdf_pages: string,
) -> CSMarkingScheme {
  client minimax
  prompt #"
    Generate the canonical Computer Science marking scheme for LO code
    { lo_code } at level { level } year { year } from these PDF pages:
    { pdf_pages }
    return a CSMarkingScheme.
  "#
}

function GenerateCSFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  pdf_pages: string,
) -> CSFormativeItem {
  client minimax
  prompt #"
    Generate the canonical Computer Science formative item for LO code
    { lo_code } at difficulty { difficulty } at level { level } topic
    { topic } from these PDF pages:
    { pdf_pages }
    return a CSFormativeItem.
  "#
}

function ScoreCSFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
  rubric_text: string,
) -> CSFormativeResponse {
  client minimax
  prompt #"
    Score the Computer Science response for item_id { item_id } student_response
    { student_response } in format { response_format } with time
    { time_taken_seconds }s and hints { hints_used } against the rubric:
    { rubric_text }
    return a CSFormativeResponse.
  "#
}
