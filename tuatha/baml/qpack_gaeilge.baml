// tuatha.baml.qpack_gaeilge — the canonical BAML functions for the Gaeilge subject.

client<llm> litellm_proxy

class GaelSyllabusTopic {
  ncca_code string
  title_en string
  title_ga string
  description_en string
  description_ga string
  source_pdf string
  source_page int
}

class GaelPastPaper {
  year int
  level string
  paper int
  paper_url string
}

class GaelMarkingScheme {
  lo_code string
  level string
  year int
  scheme_url string
  criteria list<string>
}

class GaelFormativeItem {
  lo_code string
  difficulty int
  level string
  multiple_choice string
  short_answer string
  extended_response string
  evidence string?
}

class GaelFormativeResponse {
  item_id string
  student_response string
  grade float
  feedback_en string
  feedback_ga string
  badge_emitted bool
}

function GenerateGaelSyllabus(
  lo_code: string,
  level: string,
  language: string,
) -> GaelSyllabusTopic {
  client minimax
  prompt #"
    You are the Gaeilge syllabus specialist for the NCCA Leaving
    Certificate curriculum.

    Given the LO code { lo_code } at level { level } in
    language { language }, generate the canonical
    GaelSyllabusTopic record.
  "#
}

function GenerateGaelPastPaper(
  year: int,
  level: string,
  paper: int,
) -> GaelPastPaper {
  client minimax
  prompt #"
    You are the Gaeilge past paper specialist.
  "#
}

function GenerateGaelMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
) -> GaelMarkingScheme {
  client minimax
  prompt #"
    You are the Gaeilge marking scheme specialist.
  "#
}

function GenerateGaelFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  evidence: string?,
) -> GaelFormativeItem {
  client minimax
  prompt #"
    You are the Gaeilge formative item specialist.
  "#
}

function ScoreGaelFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
) -> GaelFormativeResponse {
  client minimax
  prompt #"
    You are the Gaeilge formative response scoring specialist.
  "#
}
