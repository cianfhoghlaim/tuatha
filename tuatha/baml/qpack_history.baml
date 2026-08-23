// tuatha.baml.qpack_history — the canonical BAML functions for the History subject.

client<llm> litellm_proxy

class HistSyllabusTopic {
  ncca_code string
  title_en string
  title_ga string
  description_en string
  description_ga string
  source_pdf string
  source_page int
}

class HistPastPaper {
  year int
  level string
  paper int
  paper_url string
}

class HistMarkingScheme {
  lo_code string
  level string
  year int
  scheme_url string
  criteria list<string>
}

class HistFormativeItem {
  lo_code string
  difficulty int
  level string
  multiple_choice string
  short_answer string
  extended_response string
  evidence string?
}

class HistFormativeResponse {
  item_id string
  student_response string
  grade float
  feedback_en string
  feedback_ga string
  badge_emitted bool
}

function GenerateHistSyllabus(
  lo_code: string,
  level: string,
  language: string,
) -> HistSyllabusTopic {
  client minimax
  prompt #"
    You are the History syllabus specialist for the NCCA Leaving
    Certificate curriculum.

    Given the LO code { lo_code } at level { level } in
    language { language }, generate the canonical
    HistSyllabusTopic record.
  "#
}

function GenerateHistPastPaper(
  year: int,
  level: string,
  paper: int,
) -> HistPastPaper {
  client minimax
  prompt #"
    You are the History past paper specialist.
  "#
}

function GenerateHistMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
) -> HistMarkingScheme {
  client minimax
  prompt #"
    You are the History marking scheme specialist.
  "#
}

function GenerateHistFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  evidence: string?,
) -> HistFormativeItem {
  client minimax
  prompt #"
    You are the History formative item specialist.
  "#
}

function ScoreHistFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
) -> HistFormativeResponse {
  client minimax
  prompt #"
    You are the History formative response scoring specialist.
  "#
}
