"""tuatha.dagster — the Dagster asset group surface.

- ``anam.py`` — the ANAM capture pipeline: three capture assets, three
  embed assets, the cross-source join, and the ``ragas_anam_color_anchor``
  asset check.
- ``anam_observability.py`` — the Langfuse / MLflow / structlog wrappers
  the ANAM assets are decorated with.
- ``educational.py`` — the three educational agents.
- ``hackathon.py`` — the four BIEP hackathon features.

``per_subject.py`` moved to ``old/education_ingestion/`` when corpus
ingestion became cianfhoghlaim's responsibility. See
``tuatha/corpus/CONTRACT.md``.
"""
