// tuatha/baml/qpack_english.baml — canonical BAML contracts for the NCCA English subject.

client minimax

class EnglishSyllabusTopic {
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

class EnglishPastPaper {
  year         int
  level        string
  paper        int
  paper_url    string
  provenance_sha256 string
}

class EnglishMarkingScheme {
  lo_code       string
  level         string
  year          int
  scheme_url    string
  criteria      list<string>
  provenance_sha256 string
}

class EnglishFormativeItem {
  lo_code       string
  difficulty    int
  level         string
  topic         string
  multiple_choice    string
  short_answer       string
  extended_response  string
  evidence_pdfs        list<string>
}

class EnglishFormativeResponse {
  item_id           string
  student_response  string
  grade             float
  feedback_en       string
  feedback_ga       string
  badge_emitted     bool
  rubric_evidence   list<string>
}


function GenerateEnglishSyllabus(
  lo_code: string,
  level: string,
  language: string,
  pdf_pages: string,
) -> EnglishSyllabusTopic {
  client minimax
  prompt #"
    Generate the canonical English syllabus topic for LO code { lo_code }
    at level { level } in language { language } from these PDF pages:
    { pdf_pages }
    return a EnglishSyllabusTopic.
  "#
}

function GenerateEnglishPastPaper(
  year: int,
  level: string,
  paper: int,
  pdf_pages: string,
) -> EnglishPastPaper {
  client minimax
  prompt #"
    Generate the canonical English past paper for year { year }
    at level { level } paper { paper } from these PDF pages:
    { pdf_pages }
    return a EnglishPastPaper.
  "#
}

function GenerateEnglishMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
  pdf_pages: string,
) -> EnglishMarkingScheme {
  client minimax
  prompt #"
    Generate the canonical English marking scheme for LO code
    { lo_code } at level { level } year { year } from these PDF pages:
    { pdf_pages }
    return a EnglishMarkingScheme.
  "#
}

function GenerateEnglishFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  pdf_pages: string,
) -> EnglishFormativeItem {
  client minimax
  prompt #"
    Generate the canonical English formative item for LO code
    { lo_code } at difficulty { difficulty } at level { level } topic
    { topic } from these PDF pages:
    { pdf_pages }
    return a EnglishFormativeItem.
  "#
}

function ScoreEnglishFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
  rubric_text: string,
) -> EnglishFormativeResponse {
  client minimax
  prompt #"
    Score the English response for item_id { item_id } student_response
    { student_response } in format { response_format } with time
    { time_taken_seconds }s and hints { hints_used } against the rubric:
    { rubric_text }
    return a EnglishFormativeResponse.
  "#
}
