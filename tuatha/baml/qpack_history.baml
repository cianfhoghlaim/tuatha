// tuatha/baml/qpack_history.baml — canonical BAML contracts for the NCCA History subject.

client minimax

class HistorySyllabusTopic {
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

class HistoryPastPaper {
  year         int
  level        string
  paper        int
  paper_url    string
  provenance_sha256 string
}

class HistoryMarkingScheme {
  lo_code       string
  level         string
  year          int
  scheme_url    string
  criteria      list<string>
  provenance_sha256 string
}

class HistoryFormativeItem {
  lo_code       string
  difficulty    int
  level         string
  topic         string
  multiple_choice    string
  short_answer       string
  extended_response  string
  evidence_pdfs        list<string>
}

class HistoryFormativeResponse {
  item_id           string
  student_response  string
  grade             float
  feedback_en       string
  feedback_ga       string
  badge_emitted     bool
  rubric_evidence   list<string>
}


function GenerateHistorySyllabus(
  lo_code: string,
  level: string,
  language: string,
  pdf_pages: string,
) -> HistorySyllabusTopic {
  client minimax
  prompt #"
    Generate the canonical History syllabus topic for LO code { lo_code }
    at level { level } in language { language } from these PDF pages:
    { pdf_pages }
    return a HistorySyllabusTopic.
  "#
}

function GenerateHistoryPastPaper(
  year: int,
  level: string,
  paper: int,
  pdf_pages: string,
) -> HistoryPastPaper {
  client minimax
  prompt #"
    Generate the canonical History past paper for year { year }
    at level { level } paper { paper } from these PDF pages:
    { pdf_pages }
    return a HistoryPastPaper.
  "#
}

function GenerateHistoryMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
  pdf_pages: string,
) -> HistoryMarkingScheme {
  client minimax
  prompt #"
    Generate the canonical History marking scheme for LO code
    { lo_code } at level { level } year { year } from these PDF pages:
    { pdf_pages }
    return a HistoryMarkingScheme.
  "#
}

function GenerateHistoryFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  pdf_pages: string,
) -> HistoryFormativeItem {
  client minimax
  prompt #"
    Generate the canonical History formative item for LO code
    { lo_code } at difficulty { difficulty } at level { level } topic
    { topic } from these PDF pages:
    { pdf_pages }
    return a HistoryFormativeItem.
  "#
}

function ScoreHistoryFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
  rubric_text: string,
) -> HistoryFormativeResponse {
  client minimax
  prompt #"
    Score the History response for item_id { item_id } student_response
    { student_response } in format { response_format } with time
    { time_taken_seconds }s and hints { hints_used } against the rubric:
    { rubric_text }
    return a HistoryFormativeResponse.
  "#
}
