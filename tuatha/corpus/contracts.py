"""tuatha.corpus.contracts — the frozen read-side row schemas.

These mirror what cianfhoghlaim writes into the shared Lance namespace.
tuatha treats them as frozen: cianfhoghlaim may add columns, but a
removal or rename breaks the game. See CONTRACT.md.

Every model carries its provenance fields through unchanged. The G7
gate says nothing renders unless it can name its source, and tuatha
does not generate provenance — it propagates what the corpus already
attached.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "SUBJECTS",
    "Competency",
    "DocKind",
    "SubjectChunk",
    "lc_table_name",
]

#: The subject slugs with LC corpus tables in the shared namespace.
#: Sourced from `cocoindex_flows/subjects/lc_subject_config.yaml`.
SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "chemistry",
    "geography",
    "english",
    "gaeilge",
    "computer_science",
)


class DocKind:
    """The kind of source document a chunk came from.

    The LC embedding flow writes syllabuses, exam papers and marking
    schemes into one table per (subject, level, language) and
    distinguishes them only by ``filename``. There is no ``doc_kind``
    column, so tuatha infers the kind from the filename and keeps the
    inference in one place rather than scattering substring tests
    through the tools.
    """

    SYLLABUS = "syllabus"
    PAST_PAPER = "past_paper"
    MARKING_SCHEME = "marking_scheme"
    UNKNOWN = "unknown"

    #: Ordered most-specific first. "marking scheme" must be tested
    #: before "paper", because marking-scheme filenames often contain
    #: both words.
    _PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
        (MARKING_SCHEME, ("marking", "ms_", "-ms-", "scheme")),
        (PAST_PAPER, ("exam", "paper", "_ep_", "sec")),
        (SYLLABUS, ("syllabus", "specification", "spec_", "curriculum")),
    )

    @classmethod
    def infer(cls, filename: str) -> str:
        """Infer the document kind from a filename.

        Returns :attr:`UNKNOWN` rather than guessing when nothing
        matches, so a caller can tell "not a syllabus" from "we could
        not tell".
        """
        lowered = filename.lower()
        for kind, needles in cls._PATTERNS:
            if any(needle in lowered for needle in needles):
                return kind
        return cls.UNKNOWN

    @classmethod
    def all(cls) -> tuple[str, ...]:
        return (cls.SYLLABUS, cls.PAST_PAPER, cls.MARKING_SCHEME, cls.UNKNOWN)


class SubjectChunk(BaseModel):
    """One chunked paragraph from an LC subject document.

    Mirrors ``SubjectChunk`` in
    ``cocoindex_flows/subjects/lc_subject_embedding.py``.

    The ``embedding`` column is deliberately not modelled: tuatha reads
    text and provenance, and a 1024-float vector per row is pure weight
    on the game side.
    """

    model_config = ConfigDict(frozen=True, extra="ignore")

    chunk_id: str = Field(description="'{path}#{index}', unique per chunk")
    subject: str
    level: str = Field(description="hl / ol / fl")
    language: str = Field(description="en / ga")
    filename: str = Field(description="the source document this chunk came from")
    chunk_index: int
    text: str

    @property
    def doc_kind(self) -> str:
        """The inferred kind of the source document."""
        return DocKind.infer(self.filename)

    def provenance(self) -> dict[str, str | int]:
        """Return the fields that must survive to render time.

        A boon derived from this chunk carries this dict through. If it
        is dropped in an intermediate transform the G7 provenance gate
        breaks silently — the artefact still renders, it just can no
        longer name its source.
        """
        return {
            "chunk_id": self.chunk_id,
            "filename": self.filename,
            "chunk_index": self.chunk_index,
            "subject": self.subject,
            "level": self.level,
            "language": self.language,
        }


class Competency(BaseModel):
    """One NCCA key competency from the cross-subject table."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    competency_id: str
    name: str
    description: str = ""


def lc_table_name(subject: str, level: str = "hl", language: str = "en") -> str:
    """Build the LC corpus table name for a (subject, level, language).

    Args:
        subject: a member of :data:`SUBJECTS`.
        level: ``hl``, ``ol`` or ``fl``.
        language: ``en`` or ``ga``.

    Raises:
        ValueError: if the subject has no corpus table. The alternative
            is a table-not-found error deep inside LanceDB that does not
            say which subjects are actually available.
    """
    if subject not in SUBJECTS:
        raise ValueError(
            f"No LC corpus table for subject {subject!r}. "
            f"Subjects with corpus coverage: {', '.join(SUBJECTS)}. "
            "Coverage is added in cianfhoghlaim, not here."
        )
    return f"cianfhoghlaim.lc.{subject}.{level}_{language}"
