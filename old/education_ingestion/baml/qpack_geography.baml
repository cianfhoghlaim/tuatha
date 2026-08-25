// tuatha.baml.qpack_geography — the canonical BAML functions for the Geography subject.

client<llm> litellm_proxy

class GeogSyllabusTopic {
  ncca_code string
  title_en string
  title_ga string
  description_en string
  description_ga string
  source_pdf string
  source_page int
}

class GeogPastPaper {
  year int
  level string
  paper int
  paper_url string
}

class GeogMarkingScheme {
  lo_code string
  level string
  year int
  scheme_url string
  criteria list<string>
}

class GeogFormativeItem {
  lo_code string
  difficulty int
  level string
  multiple_choice string
  short_answer string
  extended_response string
  evidence string?
}

class GeogFormativeResponse {
  item_id string
  student_response string
  grade float
  feedback_en string
  feedback_ga string
  badge_emitted bool
}

function GenerateGeogSyllabus(
  lo_code: string,
  level: string,
  language: string,
) -> GeogSyllabusTopic {
  client minimax
  prompt #"
    You are the Geography syllabus specialist for the NCCA Leaving
    Certificate curriculum.

    Given the LO code { lo_code } at level { level } in
    language { language }, generate the canonical
    GeogSyllabusTopic record.
  "#
}

function GenerateGeogPastPaper(
  year: int,
  level: string,
  paper: int,
) -> GeogPastPaper {
  client minimax
  prompt #"
    You are the Geography past paper specialist.
  "#
}

function GenerateGeogMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
) -> GeogMarkingScheme {
  client minimax
  prompt #"
    You are the Geography marking scheme specialist.
  "#
}

function GenerateGeogFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  evidence: string?,
) -> GeogFormativeItem {
  client minimax
  prompt #"
    You are the Geography formative item specialist.
  "#
}

function ScoreGeogFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
) -> GeogFormativeResponse {
  client minimax
  prompt #"
    You are the Geography formative response scoring specialist.
  "#
}
