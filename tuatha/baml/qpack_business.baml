// tuatha/baml/qpack_business.baml — canonical BAML contracts for the NCCA Business subject.

client minimax

class BusinessSyllabusTopic {
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

class BusinessPastPaper {
  year         int
  level        string
  paper        int
  paper_url    string
  provenance_sha256 string
}

class BusinessMarkingScheme {
  lo_code       string
  level         string
  year          int
  scheme_url    string
  criteria      list<string>
  provenance_sha256 string
}

class BusinessFormativeItem {
  lo_code       string
  difficulty    int
  level         string
  topic         string
  multiple_choice    string
  short_answer       string
  extended_response  string
  evidence_pdfs        list<string>
}

class BusinessFormativeResponse {
  item_id           string
  student_response  string
  grade             float
  feedback_en       string
  feedback_ga       string
  badge_emitted     bool
  rubric_evidence   list<string>
}


function GenerateBusinessSyllabus(
  lo_code: string,
  level: string,
  language: string,
  pdf_pages: string,
) -> BusinessSyllabusTopic {
  client minimax
  prompt #"
    Generate the canonical Business syllabus topic for LO code { lo_code }
    at level { level } in language { language } from these PDF pages:
    { pdf_pages }
    return a BusinessSyllabusTopic.
  "#
}

function GenerateBusinessPastPaper(
  year: int,
  level: string,
  paper: int,
  pdf_pages: string,
) -> BusinessPastPaper {
  client minimax
  prompt #"
    Generate the canonical Business past paper for year { year }
    at level { level } paper { paper } from these PDF pages:
    { pdf_pages }
    return a BusinessPastPaper.
  "#
}

function GenerateBusinessMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
  pdf_pages: string,
) -> BusinessMarkingScheme {
  client minimax
  prompt #"
    Generate the canonical Business marking scheme for LO code
    { lo_code } at level { level } year { year } from these PDF pages:
    { pdf_pages }
    return a BusinessMarkingScheme.
  "#
}

function GenerateBusinessFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  pdf_pages: string,
) -> BusinessFormativeItem {
  client minimax
  prompt #"
    Generate the canonical Business formative item for LO code
    { lo_code } at difficulty { difficulty } at level { level } topic
    { topic } from these PDF pages:
    { pdf_pages }
    return a BusinessFormativeItem.
  "#
}

function ScoreBusinessFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
  rubric_text: string,
) -> BusinessFormativeResponse {
  client minimax
  prompt #"
    Score the Business response for item_id { item_id } student_response
    { student_response } in format { response_format } with time
    { time_taken_seconds }s and hints { hints_used } against the rubric:
    { rubric_text }
    return a BusinessFormativeResponse.
  "#
}
