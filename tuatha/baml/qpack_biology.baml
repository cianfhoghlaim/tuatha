// tuatha/baml/qpack_biology.baml — canonical BAML contracts for the NCCA Biology subject.

client minimax

class BiologySyllabusTopic {
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

class BiologyPastPaper {
  year         int
  level        string
  paper        int
  paper_url    string
  provenance_sha256 string
}

class BiologyMarkingScheme {
  lo_code       string
  level         string
  year          int
  scheme_url    string
  criteria      list<string>
  provenance_sha256 string
}

class BiologyFormativeItem {
  lo_code       string
  difficulty    int
  level         string
  topic         string
  multiple_choice    string
  short_answer       string
  extended_response  string
  evidence_pdfs        list<string>
}

class BiologyFormativeResponse {
  item_id           string
  student_response  string
  grade             float
  feedback_en       string
  feedback_ga       string
  badge_emitted     bool
  rubric_evidence   list<string>
}


function GenerateBiologySyllabus(
  lo_code: string,
  level: string,
  language: string,
  pdf_pages: string,
) -> BiologySyllabusTopic {
  client minimax
  prompt #"
    Generate the canonical Biology syllabus topic for LO code { lo_code }
    at level { level } in language { language } from these PDF pages:
    { pdf_pages }
    return a BiologySyllabusTopic.
  "#
}

function GenerateBiologyPastPaper(
  year: int,
  level: string,
  paper: int,
  pdf_pages: string,
) -> BiologyPastPaper {
  client minimax
  prompt #"
    Generate the canonical Biology past paper for year { year }
    at level { level } paper { paper } from these PDF pages:
    { pdf_pages }
    return a BiologyPastPaper.
  "#
}

function GenerateBiologyMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
  pdf_pages: string,
) -> BiologyMarkingScheme {
  client minimax
  prompt #"
    Generate the canonical Biology marking scheme for LO code
    { lo_code } at level { level } year { year } from these PDF pages:
    { pdf_pages }
    return a BiologyMarkingScheme.
  "#
}

function GenerateBiologyFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  pdf_pages: string,
) -> BiologyFormativeItem {
  client minimax
  prompt #"
    Generate the canonical Biology formative item for LO code
    { lo_code } at difficulty { difficulty } at level { level } topic
    { topic } from these PDF pages:
    { pdf_pages }
    return a BiologyFormativeItem.
  "#
}

function ScoreBiologyFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
  rubric_text: string,
) -> BiologyFormativeResponse {
  client minimax
  prompt #"
    Score the Biology response for item_id { item_id } student_response
    { student_response } in format { response_format } with time
    { time_taken_seconds }s and hints { hints_used } against the rubric:
    { rubric_text }
    return a BiologyFormativeResponse.
  "#
}
