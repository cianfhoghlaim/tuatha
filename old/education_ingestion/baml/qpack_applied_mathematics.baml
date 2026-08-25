// tuatha.baml.qpack_applied_mathematics — the canonical BAML functions for the Applied Mathematics subject.

client<llm> litellm_proxy

class AppMSyllabusTopic {
  ncca_code string
  title_en string
  title_ga string
  description_en string
  description_ga string
  source_pdf string
  source_page int
}

class AppMPastPaper {
  year int
  level string
  paper int
  paper_url string
}

class AppMMarkingScheme {
  lo_code string
  level string
  year int
  scheme_url string
  criteria list<string>
}

class AppMFormativeItem {
  lo_code string
  difficulty int
  level string
  multiple_choice string
  short_answer string
  extended_response string
  evidence string?
}

class AppMFormativeResponse {
  item_id string
  student_response string
  grade float
  feedback_en string
  feedback_ga string
  badge_emitted bool
}

function GenerateAppMSyllabus(
  lo_code: string,
  level: string,
  language: string,
) -> AppMSyllabusTopic {
  client minimax
  prompt #"
    You are the Applied Mathematics syllabus specialist for the NCCA Leaving
    Certificate curriculum.

    Given the LO code { lo_code } at level { level } in
    language { language }, generate the canonical
    AppMSyllabusTopic record.
  "#
}

function GenerateAppMPastPaper(
  year: int,
  level: string,
  paper: int,
) -> AppMPastPaper {
  client minimax
  prompt #"
    You are the Applied Mathematics past paper specialist.
  "#
}

function GenerateAppMMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
) -> AppMMarkingScheme {
  client minimax
  prompt #"
    You are the Applied Mathematics marking scheme specialist.
  "#
}

function GenerateAppMFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  evidence: string?,
) -> AppMFormativeItem {
  client minimax
  prompt #"
    You are the Applied Mathematics formative item specialist.
  "#
}

function ScoreAppMFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
) -> AppMFormativeResponse {
  client minimax
  prompt #"
    You are the Applied Mathematics formative response scoring specialist.
  "#
}
