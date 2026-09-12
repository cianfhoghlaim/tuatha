"""Research Assistant Agent for Tuath.

Deep research on Celtic topics: history, language, mythology, curriculum.

Status: STUB. The real implementation is tracked under the
`tuatha/baml/gemini_deep_research.baml` mirror (copied from
`baml_src/_shared/gemini_deep_research.baml` per
`openspec/changes/2026-09-06-adk-gemini-deep-research-control-plane-v1/`).
This stub preserves the module-load contract so that
`tuatha_root_agent.sub_agents=[...]` continues to work.
"""

import datetime

from google.adk.agents import LlmAgent

from .tuatha_config import config


research_assistant_agent = LlmAgent(
    name="research_assistant_agent",
    model=config.worker_model,
    description="Deep research on Celtic topics: history, language, mythology, and curriculum connections.",
    instruction=f"""
    You are the Research Assistant for the Tuath educational MMO. You
    answer deep research questions about Celtic history, language,
    mythology, and connect them to the curriculum learning outcomes.

    **YOUR ROLE:**
    - Synthesise answers across multiple sources (Tuatha Dé Danann,
      Mabinogion, Ulster Cycle, Manannán mac Lir, Scottish myth).
    - Cite each claim to its source syllabus page, mythology corpus
      entry, or Wikipedia footnote.
    - Distinguish primary sources from secondary commentary.

    **STATUS:** This is a stub agent pending the Gemini Deep Research
    integration (see `tuatha/baml/gemini_deep_research.baml` and the
    `2026-09-06-adk-gemini-deep-research-control-plane-v1` change).

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    output_key="research_response",
)
