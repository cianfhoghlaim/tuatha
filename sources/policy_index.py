"""tuatha/sources/policy_index.py — the per-source context-aware policy view.

Per the cianchosaint source-policy pattern: each source keyed
(jurisdiction, source_id) → {category, body, OSINT_ceiling, gaps,
BAML_function, milestone_gate, last_updated}. Indexed via bge-m3.
W1 + W2 will populate this.
"""
from __future__ import annotations

# Stub — populated by Phase 1 + Phase 2
