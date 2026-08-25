"""tuatha.dlt.response_score.applied_mathematics — thin re-export of the per_subject template.

Replaces the inert stub (yield {}) with a real DLT source
that reads from the rung-1 DuckDB table.
"""
from __future__ import annotations

from functools import partial

from tuatha.dlt.per_subject import ncca_response_score_source


applied_mathematics_response_score_source = partial(ncca_response_score_source, subject="applied_mathematics")
