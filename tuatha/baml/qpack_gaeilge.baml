// tuatha/baml/qpack_gaeilge.baml — canonical BAML contracts for the NCCA Gaeilge subject.

client minimax

class GaeilgeSyllabusTopic {
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

class GaeilgePastPaper {
  year         int
  level        string
  paper        int
  paper_url    string
  provenance_sha256 string
}

class GaeilgeMarkingScheme {
  lo_code       string
  level         string
  year          int
  scheme_url    string
  criteria      list<string>
  provenance_sha256 string
}

class GaeilgeFormativeItem {
  lo_code       string
  difficulty    int
  level         string
  topic         string
  multiple_choice    string
  short_answer       string
  extended_response  string
  evidence_pdfs        list<string>
}

class GaeilgeFormativeResponse {
  item_id           string
  student_response  string
  grade             float
  feedback_en       string
  feedback_ga       string
  badge_emitted     bool
  rubric_evidence   list<string>
}


function GenerateGaeilgeSyllabus(
  lo_code: string,
  level: string,
  language: string,
  pdf_pages: string,
) -> GaeilgeSyllabusTopic {
  client minimax
  prompt #"
    Generate the canonical Gaeilge syllabus topic for LO code { lo_code }
    at level { level } in language { language } from these PDF pages:
    { pdf_pages }
    return a GaeilgeSyllabusTopic.
  "#
}

function GenerateGaeilgePastPaper(
  year: int,
  level: string,
  paper: int,
  pdf_pages: string,
) -> GaeilgePastPaper {
  client minimax
  prompt #"
    Generate the canonical Gaeilge past paper for year { year }
    at level { level } paper { paper } from these PDF pages:
    { pdf_pages }
    return a GaeilgePastPaper.
  "#
}

function GenerateGaeilgeMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
  pdf_pages: string,
) -> GaeilgeMarkingScheme {
  client minimax
  prompt #"
    Generate the canonical Gaeilge marking scheme for LO code
    { lo_code } at level { level } year { year } from these PDF pages:
    { pdf_pages }
    return a GaeilgeMarkingScheme.
  "#
}

function GenerateGaeilgeFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  pdf_pages: string,
) -> GaeilgeFormativeItem {
  client minimax
  prompt #"
    Generate the canonical Gaeilge formative item for LO code
    { lo_code } at difficulty { difficulty } at level { level } topic
    { topic } from these PDF pages:
    { pdf_pages }
    return a GaeilgeFormativeItem.
  "#
}

function ScoreGaeilgeFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
  rubric_text: string,
) -> GaeilgeFormativeResponse {
  client minimax
  prompt #"
    Score the Gaeilge response for item_id { item_id } student_response
    { student_response } in format { response_format } with time
    { time_taken_seconds }s and hints { hints_used } against the rubric:
    { rubric_text }
    return a GaeilgeFormativeResponse.
  "#
}
