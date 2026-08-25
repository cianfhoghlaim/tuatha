"""Tests for the corpus boundary — tuatha's read-only view of the corpus.

The behaviour under test is mostly about *how things fail*. A corpus
client that returns an empty list for "no coverage" is worse than one
that raises, because an empty game world and an empty query result look
identical to the caller.
"""

from __future__ import annotations

import pytest
from tuatha.corpus import (
    CORPUS_EMBEDDER,
    CORPUS_EMBEDDING_DIM,
    SUBJECTS,
    CorpusClient,
    CorpusUnavailableError,
    DocKind,
    SubjectChunk,
    lc_table_name,
)
from tuatha.models import ROLES, resolve, vision_env
from tuatha.tools import TOOLS, bind_subject_tools


class TestTableNaming:
    def test_matches_the_upstream_convention(self):
        assert lc_table_name("chemistry", "hl", "en") == "cianfhoghlaim.lc.chemistry.hl_en"

    def test_gaeilge_table_is_addressable_in_irish(self):
        assert lc_table_name("gaeilge", "ol", "ga") == "cianfhoghlaim.lc.gaeilge.ol_ga"

    def test_subject_without_coverage_raises_and_names_the_alternatives(self):
        # history and applied_mathematics have subject agents but no
        # corpus table. That must be loud, not an empty result.
        with pytest.raises(ValueError) as exc:
            lc_table_name("history")
        assert "history" in str(exc.value)
        assert "chemistry" in str(exc.value), "the error should list what IS available"


class TestDocKind:
    @pytest.mark.parametrize(
        ("filename", "expected"),
        [
            ("LC_Chemistry_MarkingScheme_2023.pdf", DocKind.MARKING_SCHEME),
            ("ncca_chemistry_specification.pdf", DocKind.SYLLABUS),
            ("SEC_2019_Chemistry_Exam_Paper1.pdf", DocKind.PAST_PAPER),
            ("random_attachment.pdf", DocKind.UNKNOWN),
        ],
    )
    def test_infers_kind_from_filename(self, filename, expected):
        assert DocKind.infer(filename) == expected

    def test_marking_scheme_wins_over_paper(self):
        # Marking-scheme filenames routinely contain "paper" too; if the
        # paper pattern matched first, every marking scheme would be
        # misfiled as an exam paper.
        assert DocKind.infer("2019_Chemistry_Paper1_MarkingScheme.pdf") == DocKind.MARKING_SCHEME

    def test_unknown_is_distinct_from_not_matching(self):
        assert DocKind.UNKNOWN in DocKind.all()


class TestSubjectChunk:
    def _chunk(self, **kw):
        base = {
            "chunk_id": "/corpus/spec.pdf#3",
            "subject": "chemistry",
            "level": "hl",
            "language": "en",
            "filename": "ncca_chemistry_specification.pdf",
            "chunk_index": 3,
            "text": "Students should be able to describe ionic bonding.",
        }
        return SubjectChunk(**{**base, **kw})

    def test_ignores_columns_it_does_not_model(self):
        # cianfhoghlaim may add columns; that must not break the read side.
        chunk = self._chunk()
        extra = SubjectChunk.model_validate(
            {**chunk.model_dump(), "embedding": [0.0] * 1024, "some_new_column": 1}
        )
        assert extra.text == chunk.text

    def test_provenance_carries_every_field_needed_to_cite_the_source(self):
        prov = self._chunk().provenance()
        # G7: nothing renders unless it can name its source.
        for required in ("chunk_id", "filename", "chunk_index", "subject"):
            assert required in prov

    def test_doc_kind_is_derived_not_stored(self):
        assert self._chunk().doc_kind == DocKind.SYLLABUS


class TestCorpusClientFailureModes:
    def test_unset_uri_raises_with_actionable_guidance(self):
        client = CorpusClient(uri="")
        with pytest.raises(CorpusUnavailableError) as exc:
            _ = client.uri
        assert "TUATHA_LANCE_URI" in str(exc.value)

    def test_coverage_reports_rather_than_raising(self, tmp_path):
        # A preflight must be safe to call before anything is wired up.
        coverage = CorpusClient(uri=str(tmp_path)).coverage()
        assert set(coverage) == set(SUBJECTS)
        assert not any(coverage.values())

    def test_wrong_width_query_vector_is_rejected(self, tmp_path):
        # A vector from another model would return plausible nonsense
        # rather than an obvious failure, so the width is checked first.
        client = CorpusClient(uri=str(tmp_path))
        with pytest.raises(ValueError) as exc:
            client.search_vector("chemistry", [0.1] * 768)
        assert CORPUS_EMBEDDER in str(exc.value)
        assert str(CORPUS_EMBEDDING_DIM) in str(exc.value)


class TestModelRegistry:
    def test_every_declared_role_resolves(self):
        assert ROLES
        for role in ROLES:
            assert resolve(role)

    def test_unknown_role_raises_and_lists_the_declared_ones(self):
        with pytest.raises(KeyError) as exc:
            resolve("no_such_role")
        assert "anam_map" in str(exc.value)

    def test_role_env_var_overrides_the_default(self, monkeypatch):
        monkeypatch.setenv(ROLES["hades_boon"].env_var, "some/other-model")
        assert resolve("hades_boon") == "some/other-model"

    def test_vision_env_covers_every_role(self):
        env = vision_env()
        assert {spec.env_var for spec in ROLES.values()} == set(env)

    def test_every_role_records_why_it_was_chosen(self):
        for role, spec in ROLES.items():
            assert spec.why.strip(), f"role {role} has no rationale"


class TestCorpusTools:
    def test_five_tools_replace_the_forty(self):
        assert set(TOOLS) == {
            "syllabus_lookup",
            "past_paper_lookup",
            "marking_scheme_lookup",
            "formative_item_generate",
            "response_score",
        }

    def test_bound_tools_are_named_for_their_subject(self):
        names = [f.__name__ for f in bind_subject_tools("gaeilge")]
        assert names == [
            "gaeilge_syllabus_lookup",
            "gaeilge_past_paper_lookup",
            "gaeilge_marking_scheme_lookup",
            "gaeilge_formative_item_generate",
            "gaeilge_response_score",
        ]

    def test_bound_tools_carry_descriptions_for_adk(self):
        # ADK derives each tool's description from __doc__.
        assert all(f.__doc__ for f in bind_subject_tools("chemistry"))

    async def test_missing_coverage_surfaces_as_an_error_not_silence(self, monkeypatch):
        monkeypatch.delenv("TUATHA_LANCE_URI", raising=False)
        from tuatha.corpus.client import corpus
        from tuatha.tools import syllabus_lookup

        corpus.cache_clear()
        result = await syllabus_lookup("history", "the Treaty")
        assert result["results"] == []
        assert result["error"], "an empty result must be distinguishable from no coverage"
        corpus.cache_clear()
