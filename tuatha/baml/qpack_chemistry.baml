// tuatha/baml/qpack_chemistry.baml — canonical BAML contracts for the NCCA Chemistry subject.

client minimax

class ChemistrySyllabusTopic {
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

class ChemistryPastPaper {
  year         int
  level        string
  paper        int
  paper_url    string
  provenance_sha256 string
}

class ChemistryMarkingScheme {
  lo_code       string
  level         string
  year          int
  scheme_url    string
  criteria      list<string>
  provenance_sha256 string
}

class ChemistryFormativeItem {
  lo_code       string
  difficulty    int
  level         string
  topic         string
  multiple_choice    string
  short_answer       string
  extended_response  string
  evidence_pdfs        list<string>
}

class ChemistryFormativeResponse {
  item_id           string
  student_response  string
  grade             float
  feedback_en       string
  feedback_ga       string
  badge_emitted     bool
  rubric_evidence   list<string>
}


function GenerateChemistrySyllabus(
  lo_code: string,
  level: string,
  language: string,
  pdf_pages: string,
) -> ChemistrySyllabusTopic {
  client minimax
  prompt #"
    Generate the canonical Chemistry syllabus topic for LO code { lo_code }
    at level { level } in language { language } from these PDF pages:
    { pdf_pages }
    return a ChemistrySyllabusTopic.
  "#
}

function GenerateChemistryPastPaper(
  year: int,
  level: string,
  paper: int,
  pdf_pages: string,
) -> ChemistryPastPaper {
  client minimax
  prompt #"
    Generate the canonical Chemistry past paper for year { year }
    at level { level } paper { paper } from these PDF pages:
    { pdf_pages }
    return a ChemistryPastPaper.
  "#
}

function GenerateChemistryMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
  pdf_pages: string,
) -> ChemistryMarkingScheme {
  client minimax
  prompt #"
    Generate the canonical Chemistry marking scheme for LO code
    { lo_code } at level { level } year { year } from these PDF pages:
    { pdf_pages }
    return a ChemistryMarkingScheme.
  "#
}

function GenerateChemistryFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  pdf_pages: string,
) -> ChemistryFormativeItem {
  client minimax
  prompt #"
    Generate the canonical Chemistry formative item for LO code
    { lo_code } at difficulty { difficulty } at level { level } topic
    { topic } from these PDF pages:
    { pdf_pages }
    return a ChemistryFormativeItem.
  "#
}

function ScoreChemistryFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
  rubric_text: string,
) -> ChemistryFormativeResponse {
  client minimax
  prompt #"
    Score the Chemistry response for item_id { item_id } student_response
    { student_response } in format { response_format } with time
    { time_taken_seconds }s and hints { hints_used } against the rubric:
    { rubric_text }
    return a ChemistryFormativeResponse.
  "#
}
