// tuatha/baml/qpack_irish.baml — canonical BAML contracts for the NCCA Irish subject.

client minimax

class IrishSyllabusTopic {
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

class IrishPastPaper {
  year         int
  level        string
  paper        int
  paper_url    string
  provenance_sha256 string
}

class IrishMarkingScheme {
  lo_code       string
  level         string
  year          int
  scheme_url    string
  criteria      list<string>
  provenance_sha256 string
}

class IrishFormativeItem {
  lo_code       string
  difficulty    int
  level         string
  topic         string
  multiple_choice    string
  short_answer       string
  extended_response  string
  evidence_pdfs        list<string>
}

class IrishFormativeResponse {
  item_id           string
  student_response  string
  grade             float
  feedback_en       string
  feedback_ga       string
  badge_emitted     bool
  rubric_evidence   list<string>
}


function GenerateIrishSyllabus(
  lo_code: string,
  level: string,
  language: string,
  pdf_pages: string,
) -> IrishSyllabusTopic {
  client minimax
  prompt #"
    Generate the canonical Irish syllabus topic for LO code { lo_code }
    at level { level } in language { language } from these PDF pages:
    { pdf_pages }
    return a IrishSyllabusTopic.
  "#
}

function GenerateIrishPastPaper(
  year: int,
  level: string,
  paper: int,
  pdf_pages: string,
) -> IrishPastPaper {
  client minimax
  prompt #"
    Generate the canonical Irish past paper for year { year }
    at level { level } paper { paper } from these PDF pages:
    { pdf_pages }
    return a IrishPastPaper.
  "#
}

function GenerateIrishMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
  pdf_pages: string,
) -> IrishMarkingScheme {
  client minimax
  prompt #"
    Generate the canonical Irish marking scheme for LO code
    { lo_code } at level { level } year { year } from these PDF pages:
    { pdf_pages }
    return a IrishMarkingScheme.
  "#
}

function GenerateIrishFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  pdf_pages: string,
) -> IrishFormativeItem {
  client minimax
  prompt #"
    Generate the canonical Irish formative item for LO code
    { lo_code } at difficulty { difficulty } at level { level } topic
    { topic } from these PDF pages:
    { pdf_pages }
    return a IrishFormativeItem.
  "#
}

function ScoreIrishFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
  rubric_text: string,
) -> IrishFormativeResponse {
  client minimax
  prompt #"
    Score the Irish response for item_id { item_id } student_response
    { student_response } in format { response_format } with time
    { time_taken_seconds }s and hints { hints_used } against the rubric:
    { rubric_text }
    return a IrishFormativeResponse.
  "#
}
