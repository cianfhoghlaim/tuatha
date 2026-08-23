// tuatha.baml.adaptive_tutor — the canonical BAML functions for the Adaptive Tutor feature.

client<llm> litellm_proxy

function Adapttutor(
  student_input: string,
  reference_data: string,
  context: string,
) -> string {
  client minimax
  prompt #"
    You are the Adaptive Tutor specialist.

    Generate the canonical response.
  "#
}
