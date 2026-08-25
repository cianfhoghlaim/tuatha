"""
Agent configuration for Tuath.

Configures LLM models with Celtic language support.

Ported from cianfhoghlaim ``agents/adk/tuatha_config.py``. Model
defaults previously came from ``meaisinfhoghlaim.models.MODEL_REGISTRY``
behind a bare ``except``, so in this checkout the hardcoded
``gemini-2.0-flash`` fallback was always what ran. They now resolve
through tuatha's own role registry — see ``tuatha/models/registry.py``
and ``tuatha/corpus/CONTRACT.md``.
"""

import os
from dataclasses import dataclass

from tuatha.models import resolve as _resolve_role

_DEFAULT_TEXT_LLM = _resolve_role("subject_agent")
_DEFAULT_IRISH = _resolve_role("subject_agent")
#: The corpus embedder. Fixed rather than resolved: a query vector must
#: come from the same model the corpus was built with, or it is not
#: comparable. See tuatha.corpus.client.CORPUS_EMBEDDER.
_DEFAULT_EMBEDDER = "BAAI/bge-m3"


@dataclass
class AgentConfig:
    """Configuration for Tuath agents (DEPRECATED — use agents.adk.config.AgentConfig)."""

    # Primary orchestrator model (high capability, multilingual)
    orchestrator_model: str = _DEFAULT_TEXT_LLM

    # Worker model for specialized tasks
    worker_model: str = _DEFAULT_TEXT_LLM

    # Fast model for simple routing/classification
    fast_model: str = _DEFAULT_TEXT_LLM

    # Irish language model (resolved via MODEL_REGISTRY.resolve(
    # family="text_llm", role="irish") — migrates the legacy
    # uccix/uccix-llama2-13b to the registry's Irish path)
    irish_model: str = _DEFAULT_IRISH

    # Multilingual reasoning model (resolved via MODEL_REGISTRY at
    # runtime; falls back to gemini-2.0-flash if import fails)
    multilingual_model: str = _DEFAULT_TEXT_LLM

    # Embedding model for semantic search (resolved via MODEL_REGISTRY)
    embedding_model: str = _DEFAULT_EMBEDDER

    # Max tokens for responses
    max_output_tokens: int = 4096

    # Temperature for generation
    temperature: float = 0.7

    # Search result limits
    default_search_limit: int = 10
    max_search_limit: int = 50

    # x402 Payment settings
    enable_payments: bool = True
    free_daily_messages: int = 5
    free_daily_searches: int = 3
    message_price_usd: float = 0.01
    search_price_usd: float = 0.02
    premium_quest_price_usd: float = 0.05

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load configuration from environment variables."""
        return cls(
            orchestrator_model=os.environ.get(
                "TUATH_ORCHESTRATOR_MODEL", cls.orchestrator_model
            ),
            worker_model=os.environ.get("TUATH_WORKER_MODEL", cls.worker_model),
            fast_model=os.environ.get("TUATH_FAST_MODEL", cls.fast_model),
            max_output_tokens=int(
                os.environ.get("TUATH_MAX_TOKENS", cls.max_output_tokens)
            ),
            temperature=float(
                os.environ.get("TUATH_TEMPERATURE", cls.temperature)
            ),
            enable_payments=os.environ.get("TUATH_ENABLE_PAYMENTS", "true").lower() == "true",
        )


# Global config instance
config = AgentConfig.from_env()
