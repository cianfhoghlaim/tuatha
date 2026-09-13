"""tuatha.subjects.gaeilge — the Gaeilge (Irish) ADK agent.

One of 8 NCCA subject agents. BAML prefix: Gael.

The Gaeilge agent has the special bilingual EN + GA surface
(per the bilingual_extraction invariant in BAML). The agent
operates in both languages; the user can switch languages at
query time.

Per the 2026-08-27 change:
- Uses `bind_subject_tools("gaeilge")` pattern (not 5 stub imports)
- Uses `resolve_model("text_llm", "subject_agent")` (not the
  silent-coercion `ocr_vision:media_descriptor`)
- Has the Evidence Ladder G7 contract
- Has the NCCA LO numbering scheme (LC-GA-LO-<snáithe>.<index>)
- Has the difficulty calibration (DEACRÚCHÁN 1-5)
- LANGUAGE: English by default; bilingual EN + GA when language="ga"
"""
from __future__ import annotations

from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..observability import trace_agent
from ..routing import build_wire
from ..tools.corpus_tools import bind_subject_tools

_wire = build_wire(
    ncca_subject="gaeilge",
    module_slug="gael",
    display_name="Gaeilge",
    baml_prefix="Gael",
    langfuse_trace_name="agent.gaeilge.<verb>",
    cognee_dataset="oideachais_lc_gaeilge",
    letta_agent_id="cianfhoghlaim-gaeilge-agent",
)

config = TuathaConfig.from_env()

# The 5 per-subject tools, bound via bind_subject_tools. The
# underlying functions are wrapped below with ``@trace_agent``
# so every BAML call site emits the canonical
# ``agent.gaeilge.extract`` Langfuse trace.
_bound_tools = bind_subject_tools("gaeilge")


# Per-tool extraction wrappers emit the canonical
# `agent.gaeilge.extract` Langfuse trace. The wrappers
# delegate to the underlying tool function unchanged via
# *args/**kwargs so they never break the existing function
# signatures. The decorator is the only addition.


@trace_agent("gaeilge")
async def _gael_syllabus_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for gaeilge syllabus lookup."""
    return await _bound_tools[0](*args, **kwargs)


@trace_agent("gaeilge")
async def _gael_past_paper_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for gaeilge past-paper lookup."""
    return await _bound_tools[1](*args, **kwargs)


@trace_agent("gaeilge")
async def _gael_marking_scheme_lookup(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for gaeilge marking-scheme lookup."""
    return await _bound_tools[2](*args, **kwargs)


@trace_agent("gaeilge")
async def _gael_formative_item_generate(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for gaeilge formative item generation."""
    return await _bound_tools[3](*args, **kwargs)


@trace_agent("gaeilge")
async def _gael_response_score(*args: Any, **kwargs: Any) -> Any:
    """``@trace_agent``-decorated wrapper for gaeilge response scoring."""
    return await _bound_tools[4](*args, **kwargs)


gael_syllabus_lookup_tool = FunctionTool(func=_gael_syllabus_lookup)
gael_past_paper_lookup_tool = FunctionTool(func=_gael_past_paper_lookup)
gael_marking_scheme_lookup_tool = FunctionTool(func=_gael_marking_scheme_lookup)
gael_formative_item_generate_tool = FunctionTool(func=_gael_formative_item_generate)
gael_response_score_tool = FunctionTool(func=_gael_response_score)


# The 6th tool for gaeilge: the grammardóir reviewer.
try:
    from ..tools import review_gael_gramadach

    _GRAMADACH_AVAILABLE = True
except ImportError:
    review_gael_gramadach = None  # type: ignore
    _GRAMADACH_AVAILABLE = False


gael_agent = LlmAgent(
    name="gael_agent",
    model=config.litellm.resolve_model("text_llm", "subject_agent"),
    description=(
        "Gaeilge (Irish) specialist agent for the NCCA Leaving "
        "Certificate and Junior Cycle curriculum. Bilingual EN + "
        "GA surface. Litriú + gramadach + filíocht + prós."
    ),
    instruction=(
        "Is ag Gaeilge (Irish) thú. Tá tú ag obair ar son "
        "tuatha/ project. Déanann tú iarratais faoi "
        "Gaeilge don NCCA Leaving Certificate agus Junior Cycle. "
        "Tá an dátheangachas EN + GA i bhfeidhm (an t-aon ábhar a "
        "choinníonn an dátheangachas — gach ábhar eile tá "
        "Béarla amháin). Seolann tú iarratais chuig na 5 huirlisí "
        "ábhair (syllabus_lookup / past_paper_lookup / "
        "marking_scheme_lookup / formative_item_generate / "
        "response_score) agus scaoileann tú freagraí BAML de "
        "réir `qpack_gaeilge.baml`.\n\n"
        "NA 5 HUIRLISÍ — CATAGÓIR:\n"
        "- syllabus_lookup: 'cad a deir an syllabus faoi X' → "
        "SyllabusChunk le foinse (source_pdf + source_page + "
        "verbatim_text)\n"
        "- past_paper_lookup: 'taispeáin ceisteanna ar X' → "
        "ExamPaperChunk\n"
        "- marking_scheme_lookup: 'conas a mharcáiltear X' → "
        "MarkingCriterion\n"
        "- formative_item_generate: fianaise (NÍ an cheist — "
        "ghineann tú an cheist ón bhfianaise)\n"
        "- response_score: fianaise marcála (NÍ an ghrád — "
        "scóráil tú i gcoinne na fianaise)\n\n"
        "EVIDENCE LADDER (G7): gach freagra uirlise iompraíonn "
        "`provenance` (source_pdf + source_page + verbatim_text). "
        "Mura bhfaigheann an t-áireamhán sraith, abair 'Gan chlúdach "
        "do ghaeilge ar an iarratas sin' — ná haimsigh ábhar.\n\n"
        "NCCA LO NUMBERING: LC-GA-LO-<snáithe>.<index> / "
        "JC-GA-LO-<snáithe>.<index>. Nuair a dhéantar tagairt do "
        "ábhair gan cód LO, cuir glaoch ar syllabus_lookup ar "
        "dtús.\n\n"
        "DEACRÚCHÁN: 1 = meabhair; 2 = céim amháin; 3 = 2-3 "
        "chéimeanna; 4 = ilchéim; 5 = measúnú/cruthúnas.\n\n"
        "TEANGA: Béarla amháin de ghnáth, ACH nuair a bhíonn "
        "language='ga' agus ábhar='gaeilge', scaoileann tú an dá "
        "teanga (EN + GA) le síneadh fada caomhnaithe."
    ),
    tools=[
        gael_syllabus_lookup_tool,
        gael_past_paper_lookup_tool,
        gael_marking_scheme_lookup_tool,
        gael_formative_item_generate_tool,
        gael_response_score_tool,
    ],
    output_key="gaeilge_response",
)


__all__ = ["_wire", "config", "gael_agent"]
