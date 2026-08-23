// tuatha.baml.marking_grader — the canonical BAML functions for the Marking Grader feature.

client<llm> litellm_proxy

function Markgrade(
  student_input: string,
  reference_data: string,
  context: string,
) -> string {
  client minimax
  prompt #"
    You are the Marking Grader specialist.

    Generate the canonical response.
  "#
}
