"""Unit test for the Phase 5 5-agent dispatcher."""
import sys
sys.path.insert(0, '/Users/cianmacadeisigh/dev/tuatha')

from tuatha.education import (
    AgentKind, Phase5AgentQuery, query_agent, dispatch_agent,
)


def test_subject_route():
    q = Phase5AgentQuery(student_id="self", prompt="what is LC-MATHS-LO-2.4?")
    assert dispatch_agent(q) == AgentKind.SUBJECT


def test_cross_subject_route():
    q = Phase5AgentQuery(student_id="self", prompt="compare between LC-MATHS and LC-PHYSICS")
    assert dispatch_agent(q) == AgentKind.CROSS_SUBJECT


def test_mythology_route():
    q = Phase5AgentQuery(student_id="self", prompt="tell me about Tuatha Dé Danann")
    assert dispatch_agent(q) == AgentKind.MYTHOLOGY


def test_history_route():
    q = Phase5AgentQuery(student_id="self", prompt="what happened at the 1916 Rising?")
    assert dispatch_agent(q) == AgentKind.ACADEMIC_HISTORY


def test_grammar_route():
    q = Phase5AgentQuery(student_id="self", prompt="explain eclips + lenition grammar")
    assert dispatch_agent(q) == AgentKind.CELTIC_GRAMMAR
