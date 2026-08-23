// tuatha.baml.qpack_english — the canonical BAML functions for the English subject.

client<llm> litellm_proxy

class EnglSyllabusTopic {
  ncca_code string
  title_en string
  title_ga string
  description_en string
  description_ga string
  source_pdf string
  source_page int
}

class EnglPastPaper {
  year int
  level string
  paper int
  paper_url string
}

class EnglMarkingScheme {
  lo_code string
  level string
  year int
  scheme_url string
  criteria list<string>
}

class EnglFormativeItem {
  lo_code string
  difficulty int
  level string
  multiple_choice string
  short_answer string
  extended_response string
  evidence string?
}

class EnglFormativeResponse {
  item_id string
  student_response string
  grade float
  feedback_en string
  feedback_ga string
  badge_emitted bool
}

function GenerateEnglSyllabus(
  lo_code: string,
  level: string,
  language: string,
) -> EnglSyllabusTopic {
  client minimax
  prompt #"
    You are the English syllabus specialist for the NCCA Leaving
    Certificate curriculum.

    Given the LO code { lo_code } at level { level } in
    language { language }, generate the canonical
    EnglSyllabusTopic record.
  "#
}

function GenerateEnglPastPaper(
  year: int,
  level: string,
  paper: int,
) -> EnglPastPaper {
  client minimax
  prompt #"
    You are the English past paper specialist.
  "#
}

function GenerateEnglMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
) -> EnglMarkingScheme {
  client minimax
  prompt #"
    You are the English marking scheme specialist.
  "#
}

function GenerateEnglFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  evidence: string?,
) -> EnglFormativeItem {
  client minimax
  prompt #"
    You are the English formative item specialist.
  "#
}

function ScoreEnglFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
) -> EnglFormativeResponse {
  client minimax
  prompt #"
    You are the English formative response scoring specialist.
  "#
}
