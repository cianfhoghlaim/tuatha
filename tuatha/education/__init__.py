"""tuatha.education — Phase 5 education surface.

The persistent tutor session + cross-app routing + UI components
that span the British Isles MMO app, the docs surface, and the
mastery dashboard.

Re-exports:
- AgentKind / Phase5AgentQuery / Phase5AgentResponse / query_agent (from agents.agent)
- Phase5PersistentState / make_phase5_state (from state.persistent_state)
- Phase5RoutingDecision / Phase5CrossAppRouter / make_phase5_router (from routing.cross_app_routing)
- Lesson / Tutor / Mastery / Retention (from components)
"""
from .agents.agent import (
    AgentKind, Phase5AgentQuery, Phase5AgentResponse, query_agent,
)
from .state.persistent_state import (
    Phase5PersistentState, make_phase5_state,
)
from .routing.cross_app_routing import (
    Phase5RoutingDecision, Phase5CrossAppRouter, make_phase5_router,
)
from .components import Lesson, Tutor, Mastery, Retention

__all__ = [
    "AgentKind", "Phase5AgentQuery", "Phase5AgentResponse", "query_agent",
    "Phase5PersistentState", "make_phase5_state",
    "Phase5RoutingDecision", "Phase5CrossAppRouter", "make_phase5_router",
    "Lesson", "Tutor", "Mastery", "Retention",
]
