// tuatha.baml.qpack_computer_science — the canonical BAML functions for the Computer Science subject.

client<llm> litellm_proxy

class CompSyllabusTopic {
  ncca_code string
  title_en string
  title_ga string
  description_en string
  description_ga string
  source_pdf string
  source_page int
}

class CompPastPaper {
  year int
  level string
  paper int
  paper_url string
}

class CompMarkingScheme {
  lo_code string
  level string
  year int
  scheme_url string
  criteria list<string>
}

class CompFormativeItem {
  lo_code string
  difficulty int
  level string
  multiple_choice string
  short_answer string
  extended_response string
  evidence string?
}

class CompFormativeResponse {
  item_id string
  student_response string
  grade float
  feedback_en string
  feedback_ga string
  badge_emitted bool
}

function GenerateCompSyllabus(
  lo_code: string,
  level: string,
  language: string,
) -> CompSyllabusTopic {
  client minimax
  prompt #"
    You are the Computer Science syllabus specialist for the NCCA Leaving
    Certificate curriculum.

    Given the LO code { lo_code } at level { level } in
    language { language }, generate the canonical
    CompSyllabusTopic record.
  "#
}

function GenerateCompPastPaper(
  year: int,
  level: string,
  paper: int,
) -> CompPastPaper {
  client minimax
  prompt #"
    You are the Computer Science past paper specialist.
  "#
}

function GenerateCompMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
) -> CompMarkingScheme {
  client minimax
  prompt #"
    You are the Computer Science marking scheme specialist.
  "#
}

function GenerateCompFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  evidence: string?,
) -> CompFormativeItem {
  client minimax
  prompt #"
    You are the Computer Science formative item specialist.
  "#
}

function ScoreCompFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
) -> CompFormativeResponse {
  client minimax
  prompt #"
    You are the Computer Science formative response scoring specialist.
  "#
}
