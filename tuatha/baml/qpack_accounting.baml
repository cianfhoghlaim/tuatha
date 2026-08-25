// tuatha/baml/qpack_accounting.baml — canonical BAML contracts for the NCCA Accounting subject.

client minimax

class AccountingSyllabusTopic {
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

class AccountingPastPaper {
  year         int
  level        string
  paper        int
  paper_url    string
  provenance_sha256 string
}

class AccountingMarkingScheme {
  lo_code       string
  level         string
  year          int
  scheme_url    string
  criteria      list<string>
  provenance_sha256 string
}

class AccountingFormativeItem {
  lo_code       string
  difficulty    int
  level         string
  topic         string
  multiple_choice    string
  short_answer       string
  extended_response  string
  evidence_pdfs        list<string>
}

class AccountingFormativeResponse {
  item_id           string
  student_response  string
  grade             float
  feedback_en       string
  feedback_ga       string
  badge_emitted     bool
  rubric_evidence   list<string>
}


function GenerateAccountingSyllabus(
  lo_code: string,
  level: string,
  language: string,
  pdf_pages: string,
) -> AccountingSyllabusTopic {
  client minimax
  prompt #"
    Generate the canonical Accounting syllabus topic for LO code { lo_code }
    at level { level } in language { language } from these PDF pages:
    { pdf_pages }
    return a AccountingSyllabusTopic.
  "#
}

function GenerateAccountingPastPaper(
  year: int,
  level: string,
  paper: int,
  pdf_pages: string,
) -> AccountingPastPaper {
  client minimax
  prompt #"
    Generate the canonical Accounting past paper for year { year }
    at level { level } paper { paper } from these PDF pages:
    { pdf_pages }
    return a AccountingPastPaper.
  "#
}

function GenerateAccountingMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
  pdf_pages: string,
) -> AccountingMarkingScheme {
  client minimax
  prompt #"
    Generate the canonical Accounting marking scheme for LO code
    { lo_code } at level { level } year { year } from these PDF pages:
    { pdf_pages }
    return a AccountingMarkingScheme.
  "#
}

function GenerateAccountingFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  pdf_pages: string,
) -> AccountingFormativeItem {
  client minimax
  prompt #"
    Generate the canonical Accounting formative item for LO code
    { lo_code } at difficulty { difficulty } at level { level } topic
    { topic } from these PDF pages:
    { pdf_pages }
    return a AccountingFormativeItem.
  "#
}

function ScoreAccountingFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
  rubric_text: string,
) -> AccountingFormativeResponse {
  client minimax
  prompt #"
    Score the Accounting response for item_id { item_id } student_response
    { student_response } in format { response_format } with time
    { time_taken_seconds }s and hints { hints_used } against the rubric:
    { rubric_text }
    return a AccountingFormativeResponse.
  "#
}
