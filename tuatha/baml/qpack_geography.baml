// tuatha/baml/qpack_geography.baml — canonical BAML contracts for the NCCA Geography subject.

client minimax

class GeographySyllabusTopic {
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

class GeographyPastPaper {
  year         int
  level        string
  paper        int
  paper_url    string
  provenance_sha256 string
}

class GeographyMarkingScheme {
  lo_code       string
  level         string
  year          int
  scheme_url    string
  criteria      list<string>
  provenance_sha256 string
}

class GeographyFormativeItem {
  lo_code       string
  difficulty    int
  level         string
  topic         string
  multiple_choice    string
  short_answer       string
  extended_response  string
  evidence_pdfs        list<string>
}

class GeographyFormativeResponse {
  item_id           string
  student_response  string
  grade             float
  feedback_en       string
  feedback_ga       string
  badge_emitted     bool
  rubric_evidence   list<string>
}


function GenerateGeographySyllabus(
  lo_code: string,
  level: string,
  language: string,
  pdf_pages: string,
) -> GeographySyllabusTopic {
  client minimax
  prompt #"
    Generate the canonical Geography syllabus topic for LO code { lo_code }
    at level { level } in language { language } from these PDF pages:
    { pdf_pages }
    return a GeographySyllabusTopic.
  "#
}

function GenerateGeographyPastPaper(
  year: int,
  level: string,
  paper: int,
  pdf_pages: string,
) -> GeographyPastPaper {
  client minimax
  prompt #"
    Generate the canonical Geography past paper for year { year }
    at level { level } paper { paper } from these PDF pages:
    { pdf_pages }
    return a GeographyPastPaper.
  "#
}

function GenerateGeographyMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
  pdf_pages: string,
) -> GeographyMarkingScheme {
  client minimax
  prompt #"
    Generate the canonical Geography marking scheme for LO code
    { lo_code } at level { level } year { year } from these PDF pages:
    { pdf_pages }
    return a GeographyMarkingScheme.
  "#
}

function GenerateGeographyFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  pdf_pages: string,
) -> GeographyFormativeItem {
  client minimax
  prompt #"
    Generate the canonical Geography formative item for LO code
    { lo_code } at difficulty { difficulty } at level { level } topic
    { topic } from these PDF pages:
    { pdf_pages }
    return a GeographyFormativeItem.
  "#
}

function ScoreGeographyFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
  rubric_text: string,
) -> GeographyFormativeResponse {
  client minimax
  prompt #"
    Score the Geography response for item_id { item_id } student_response
    { student_response } in format { response_format } with time
    { time_taken_seconds }s and hints { hints_used } against the rubric:
    { rubric_text }
    return a GeographyFormativeResponse.
  "#
}
