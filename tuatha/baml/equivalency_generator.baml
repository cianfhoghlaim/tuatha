// tuatha.baml.equivalency_generator — the canonical BAML functions for the Equivalency Generator feature.

client<llm> litellm_proxy

function Equivgen(
  student_input: string,
  reference_data: string,
  context: string,
) -> string {
  client minimax
  prompt #"
    You are the Equivalency Generator specialist.

    Generate the canonical response.
  "#
}
