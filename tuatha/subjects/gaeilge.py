"""tuatha.subjects.gaeilge — the Gaeilge (Irish) ADK agent.

One of 8 NCCA subject agents. BAML prefix: Gael.

The Gaeilge agent has the special bilingual EN + GA surface
(per the bilingual_extraction invariant in BAML). The agent
operates in both languages; the user can switch languages at
query time.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.corpus_tools import bind_subject_tools

_wire = build_wire(
    ncca_subject="gaeilge",
    module_slug="gael",
    display_name="Gaeilge",
    baml_prefix="Gael",
    langfuse_trace_name="agent.gaeilge.<verb>",
    cognee_dataset="oideachais_lc_gaeilge",
    letta_agent_id="kcg-gaeilge-agent",
)

config = TuathaConfig.from_env()

# The five corpus tools, bound to this subject so the model
# cannot query another subject's corpus.
_tools = [FunctionTool(func=f) for f in bind_subject_tools("gaeilge")]


gael_agent = LlmAgent(
    name="gael_agent",
    model=config.litellm.resolve_model("subject_agent"),
    description=(
        "Gaeilge (Irish) specialist agent for the NCCA Leaving "
        "Certificate and Junior Cycle curriculum. Bilingual EN + "
        "GA surface. Litriú + gramadach + filíocht + prós."
    ),
    instruction=(
        "Is ag Gaeilge (Irish) thú. Tá tú ag obair ar son "
        "tuatha/ project. Déanann tú iarratais faoi "
        "Gaeilge don NCCA Leaving Certificate agus Junior Cycle. "
        "Tá an dátheangachas EN + GA i bhfeidhm. Seolann tú "
        "iarratais chuig na 5 huirlisí ábhair (syllabus_lookup / "
        "past_paper_lookup / marking_scheme_lookup / "
        "formative_item_generate / response_score) agus "
        "scaoileann tú freagraí BAML de réir "
        "`qpack_gaeilge.baml`."
    ),
    tools=_tools,
    output_key="gaeilge_response",
)


__all__ = ["_wire", "config", "gael_agent"]
