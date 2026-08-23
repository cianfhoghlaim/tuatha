// tuatha.baml.qpack_chemistry — the canonical BAML functions for the Chemistry subject.

client<llm> litellm_proxy

class ChemSyllabusTopic {
  ncca_code string
  title_en string
  title_ga string
  description_en string
  description_ga string
  source_pdf string
  source_page int
}

class ChemPastPaper {
  year int
  level string
  paper int
  paper_url string
}

class ChemMarkingScheme {
  lo_code string
  level string
  year int
  scheme_url string
  criteria list<string>
}

class ChemFormativeItem {
  lo_code string
  difficulty int
  level string
  multiple_choice string
  short_answer string
  extended_response string
  evidence string?
}

class ChemFormativeResponse {
  item_id string
  student_response string
  grade float
  feedback_en string
  feedback_ga string
  badge_emitted bool
}

function GenerateChemSyllabus(
  lo_code: string,
  level: string,
  language: string,
) -> ChemSyllabusTopic {
  client minimax
  prompt #"
    You are the Chemistry syllabus specialist for the NCCA Leaving
    Certificate curriculum.

    Given the LO code { lo_code } at level { level } in
    language { language }, generate the canonical
    ChemSyllabusTopic record.
  "#
}

function GenerateChemPastPaper(
  year: int,
  level: string,
  paper: int,
) -> ChemPastPaper {
  client minimax
  prompt #"
    You are the Chemistry past paper specialist.
  "#
}

function GenerateChemMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
) -> ChemMarkingScheme {
  client minimax
  prompt #"
    You are the Chemistry marking scheme specialist.
  "#
}

function GenerateChemFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  evidence: string?,
) -> ChemFormativeItem {
  client minimax
  prompt #"
    You are the Chemistry formative item specialist.
  "#
}

function ScoreChemFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
) -> ChemFormativeResponse {
  client minimax
  prompt #"
    You are the Chemistry formative response scoring specialist.
  "#
}
