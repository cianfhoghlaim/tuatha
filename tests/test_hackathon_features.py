"""The 4 BIEP hackathon features tests."""
import pytest

from tuatha.agents.hackathon import (
    marking_grader_agent, adaptive_tutor_agent,
    equivalency_generator_agent, curriculum_change_sensor_agent,
)


HACKATHONS = [
    ("marking_grader", marking_grader_agent),
    ("adaptive_tutor", adaptive_tutor_agent),
    ("equivalency_generator", equivalency_generator_agent),
    ("curriculum_change_sensor", curriculum_change_sensor_agent),
]

@pytest.mark.parametrize("name,agent", HACKATHONS)
def test_hackathon_has_name(name, agent):
    assert agent.name == f"{name}_agent"

@pytest.mark.parametrize("name,agent", HACKATHONS)
def test_hackathon_has_model(agent, name):
    assert agent.model is not None
