"""The 20 canonical smoke tests for the 8 NCCA subject agents + 3 educational agents + 4 BIEP hackathon features + the 10-tool media_descriptor_agent."""
import pytest

from tuatha.subjects import (
    math_agent, appm_agent, chem_agent, geog_agent,
    hist_agent, engl_agent, gael_agent, comp_agent,
)
from tuatha.agents.educational import (
    academic_history_agent, celtic_grammar_agent, celtic_morphology_agent,
)
from tuatha.agents.hackathon import (
    marking_grader_agent, adaptive_tutor_agent,
    equivalency_generator_agent, curriculum_change_sensor_agent,
)
from tuatha.agents.media_intel import (
    TOOLS, media_descriptor_agent,
    classify_medium, per_medium_coverage, cross_medium_consistency,
)

AGENTS = [
    ("math", math_agent), ("appm", appm_agent), ("chem", chem_agent),
    ("geog", geog_agent), ("hist", hist_agent), ("engl", engl_agent),
    ("gael", gael_agent), ("comp", comp_agent),
    ("academic_history", academic_history_agent),
    ("celtic_grammar", celtic_grammar_agent),
    ("celtic_morphology", celtic_morphology_agent),
    ("marking_grader", marking_grader_agent),
    ("adaptive_tutor", adaptive_tutor_agent),
    ("equivalency_generator", equivalency_generator_agent),
    ("curriculum_change_sensor", curriculum_change_sensor_agent),
    ("media_descriptor", media_descriptor_agent),
]

@pytest.mark.parametrize("name,agent", AGENTS)
def test_agent_has_name(name, agent):
    assert agent.name == f"{name}_agent"

@pytest.mark.parametrize("name,agent", AGENTS)
def test_agent_has_model(agent, name):
    assert agent.model is not None

def test_media_intel_has_10_tools():
    assert len(TOOLS) == 10

def test_classify_medium():
    assert classify_medium({"medium": "comic"}) == "comic_descriptor"
    assert classify_medium({"medium": "prose"}) == "prose_descriptor"
    assert classify_medium({"medium": "animation"}) == "animation_descriptor"
    assert classify_medium({"medium": "gameplay"}) == "gameplay_descriptor"
    assert classify_medium({"medium": "official"}) == "official_document_descriptor"
