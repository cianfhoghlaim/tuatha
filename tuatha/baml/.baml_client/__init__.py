"""baml_client — the baml_client Python package init.

Exports the canonical `b` singleton for `from baml_client import b`.
"""
from .sync_client import b

__all__ = ["b"]
