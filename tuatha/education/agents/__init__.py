"""tuatha.education.agents — the Phase 5 5-agent dispatcher."""
from .agent import (
    AgentKind,
    Phase5AgentQuery,
    Phase5AgentResponse,
    dispatch_agent,
    query_agent,
)
__all__ = ["AgentKind", "Phase5AgentQuery", "Phase5AgentResponse",
           "dispatch_agent", "query_agent"]
