"""tuatha.cocoindex.anam — the ANAM capture CocoIndex v1 Apps.

Four Apps turn captured media into ANAM particle rows:

===================== ========================================
App                    Lance table
===================== ========================================
``tuatha_hades_boons``   ``cianfhoghlaim.tuatha.hades.boons``
``tuatha_comic_particles`` ``cianfhoghlaim.tuatha.comic.particles``
``tuatha_gba_magic``     ``cianfhoghlaim.tuatha.gba.magic``
``tuatha_anam_particles`` ``cianfhoghlaim.tuatha.anam_particles``
===================== ========================================

The first three extract per-source descriptors; the fourth joins them
into the canonical ANAM particle corpus that the theming and asset
layers read.

These tables sit under ``cianfhoghlaim.tuatha.*``, which is tuatha's to
write — see ``tuatha/corpus/CONTRACT.md``. Everything else in the
``cianfhoghlaim.*`` namespace is read-only from here.

This package replaces ``tuatha/cocoindex/media_intel.py``, whose
indexer body was ``pass``.

Importing the Apps requires ``cocoindex``; the module-level import is
deliberate so a missing dependency fails loudly rather than leaving a
silently disabled pipeline.
"""

from ._shared import EMBED_MODEL, EMBEDDER, LANCE_DB, S3_LANCE_URI, shared_lifespan

#: The Lance tables this package owns, App name -> table name.
ANAM_TABLES: dict[str, str] = {
    "tuatha_hades_boons": "cianfhoghlaim.tuatha.hades.boons",
    "tuatha_comic_particles": "cianfhoghlaim.tuatha.comic.particles",
    "tuatha_gba_magic": "cianfhoghlaim.tuatha.gba.magic",
    "tuatha_anam_particles": "cianfhoghlaim.tuatha.anam_particles",
}

#: The join App reads from these three and writes the ANAM corpus.
ANAM_SOURCE_TABLES: tuple[str, ...] = (
    "cianfhoghlaim.tuatha.hades.boons",
    "cianfhoghlaim.tuatha.comic.particles",
    "cianfhoghlaim.tuatha.gba.magic",
)

__all__ = [
    "ANAM_SOURCE_TABLES",
    "ANAM_TABLES",
    "EMBEDDER",
    "EMBED_MODEL",
    "LANCE_DB",
    "S3_LANCE_URI",
    "shared_lifespan",
]
