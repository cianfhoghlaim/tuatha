// tuatha.baml.qpack_mathematics — the canonical BAML functions for the
Mathematics NCCA Leaving Certificate subject.
//
// The 5 functions mirror the 5 per-subject tools
// (syllabus_lookup + past_paper_lookup + marking_scheme_lookup
// + formative_item_generate + response_score). All 5 functions
// emit typed BAML classes that codegen to Pydantic + Zod + Convex +
// DuckLake DDL.
*/
client<llm> litellm_proxy

class MathSyllabusTopic {
  ncca_code string
  title_en string
  title_ga string
  description_en string
  description_ga string
  source_pdf string
  source_page int
}

class MathPastPaper {
  year int
  level string
  paper int
  paper_url string
}

class MathMarkingScheme {
  lo_code string
  level string
  year int
  scheme_url string
  criteria list<string>
}

class MathFormativeItem {
  lo_code string
  difficulty int
  level string
  multiple_choice string
  short_answer string
  extended_response string
  evidence string?
}

class MathFormativeResponse {
  item_id string
  student_response string
  grade float
  feedback_en string
  feedback_ga string
  badge_emitted bool
}

function GenerateMathSyllabus(
  lo_code: string,
  level: string,
  language: string,
) -> MathSyllabusTopic {
  client minimax
  prompt #"
    You are the Mathematics syllabus specialist for the NCCA
    Leaving Certificate curriculum.

    Given the LO code {{ lo_code }} at level {{ level }} in
    language {{ language }}, generate the canonical
    MathSyllabusTopic record with the ncca_code + the title
    (en + ga) + the description (en + ga) + the source_pdf
    path + the source_page.

    The result must be a valid MathSyllabusTopic BAML class.
  "#
}

function GenerateMathPastPaper(
  year: int,
  level: string,
  paper: int,
) -> MathPastPaper {
  client minimax
  prompt #"
    You are the Mathematics past paper specialist.

    Given year {{ year }} at level {{ level }} paper {{ paper }},
    generate the canonical MathPastPaper record with the
    year + level + paper + paper_url.

    The result must be a valid MathPastPaper BAML class.
  "#
}

function GenerateMathMarkingScheme(
  lo_code: string,
  level: string,
  year: int,
) -> MathMarkingScheme {
  client minimax
  prompt #"
    You are the Mathematics marking scheme specialist.

    Given the LO code {{ lo_code }} at level {{ level }} for year
    {{ year }}, generate the canonical MathMarkingScheme record
    with the lo_code + level + year + scheme_url + criteria.

    The result must be a valid MathMarkingScheme BAML class.
  "#
}

function GenerateMathFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  evidence: string?,
) -> MathFormativeItem {
  client minimax
  prompt #"
    You are the Mathematics formative item specialist.

    Given the LO code {{ lo_code }} at difficulty {{ difficulty }}
    at level {{ level }} for topic {{ topic }} with evidence
    {{ evidence }}, generate the canonical MathFormativeItem
    record with the lo_code + difficulty + level + the
    multiple_choice + short_answer + extended_response.

    The result must be a valid MathFormativeItem BAML class.
  "#
}

function ScoreMathFormativeResponse(
  item_id: string,
  student_response: string,
  response_format: string,
  time_taken_seconds: int,
  hints_used: int,
) -> MathFormativeResponse {
  client minimax
  prompt #"
    You are the Mathematics formative response scoring
    specialist.

    Given the item_id {{ item_id }} with student_response
    {{ student_response }} in response_format
    {{ response_format }} with time_taken_seconds
    {{ time_taken_seconds }} and hints_used {{ hints_used }},
    generate the canonical MathFormativeResponse record with
    the grade (0-1) + the bilingual feedback (en + ga) +
    the badge_emitted flag.

    The result must be a valid MathFormativeResponse BAML class.
  "#
}
