"""Quest Guide Agent for Tuath.

Quest objectives, hints, learning outcome tracking, and progress guidance.

Status: STUB. The real implementation is tracked under
`openspec/changes/2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1/`
follow-up work. This stub preserves the module-load contract so that
`tuatha_root_agent.sub_agents=[...]` continues to work.
"""

import datetime

from google.adk.agents import LlmAgent

from .tuatha_config import config


# Real quest tools are added when the quest-tracking DLT pipeline ships.
# Until then, `quest_guide_agent` answers via direct LLM reasoning only.
quest_guide_agent = LlmAgent(
    name="quest_guide_agent",
    model=config.worker_model,
    description="Quest objectives, hints, learning-outcome tracking, and progress guidance for the Celtic Educational MMO.",
    instruction=f"""
    You are the Quest Guide for the Tuath educational MMO. You help
    players understand their current quest objectives, hint at the next
    chamber, and tie progress to NCCA / SEC learning outcomes.

    **YOUR ROLE:**
    - Surface the player's current quest state.
    - Suggest the next chamber based on the learning outcomes it trains.
    - Connect each quest step to the curriculum syllabus page that
      supports it (cite the source).

    **STATUS:** This is a stub agent pending the quest-tracking DLT
    pipeline + BAML extraction contracts (see
    `openspec/changes/2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1/`
    follow-up tasks).

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    output_key="quest_response",
)
