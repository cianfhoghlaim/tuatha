"""tuatha.dlt.syllabus.accounting — thin re-export of the per_subject template.

Replaces the inert stub (yield {}) with a real DLT source
that reads from the rung-1 DuckDB table.
"""
from __future__ import annotations

from functools import partial

from tuatha.dlt.per_subject import ncca_syllabus_source


accounting_syllabus_source = partial(ncca_syllabus_source, subject="accounting")
