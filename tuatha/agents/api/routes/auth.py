"""Auth helpers for the Tuatha FastAPI surface.

Status: STUB. The real auth surface (Pocket ID OIDC + Pangolin session
binding + Infisical-issued service-account tokens) is deferred to a
follow-up change. This stub preserves the import contract so that
`routes/game_state.py` and `routes/mythology.py` can load.

When the real auth ships, replace `_STUB_USER` with a proper
`SessionContext` dataclass populated from the verified OIDC token.
"""

from fastapi import Header


_STUB_USER = "stub-user"


async def get_session_from_header(
    authorization: str | None = Header(default=None),
) -> str:
    """Return the session user identity.

    Real impl: verify `authorization: Bearer <oidc-jwt>` against the
    Pocket ID discovery endpoint, return the user's stable subject ID.
    Stub: return a constant.
    """
    if authorization is None:
        return _STUB_USER
    return authorization.split(" ", 1)[-1] or _STUB_USER
