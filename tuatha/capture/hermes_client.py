"""tuatha.capture.hermes_client — Hermes Agent computer-use HTTP client stub.

Per the
`openspec/changes/2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1/`
T0.5: the Hermes Agent computer-use API is the new Phase-2
capture path for ANAM extraction (replacing the deprecated
Swift capture daemon in `tuatha/capture/macos/`).

The Hermes Agent endpoint is `https://unsloth.cianfhoghlaim.ie:8889/v1/`
(see the `2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1`
change for the Unsloth Studio wiring). The computer-use API
exposes 3 methods that match the Swift daemon's JSON-RPC
methods (start_run / stop_run / mark_event), but the
implementation is HTTP POST to the Hermes agent + JSON
response.

This is a Phase-2 stub — the implementation is `pass` bodies
for now. The full impl will land in a follow-up change once
the Hermes Agent endpoint is live + the authentication flow
is settled.

Per the centralized-secrets-management contract: `HERMES_API_KEY`
is the env var name (Locket-injected; do NOT hand-edit `.env`).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

HERMES_BASE_URL = "https://unsloth.cianfhoghlaim.ie:8889/v1"


@dataclass(frozen=True)
class HermesConfig:
    """The canonical Hermes Agent computer-use configuration."""

    base_url: str = field(
        default_factory=lambda: os.environ.get(
            "HERMES_BASE_URL", HERMES_BASE_URL
        )
    )
    api_key: str = field(
        default_factory=lambda: os.environ.get("HERMES_API_KEY", "")
    )
    timeout: int = 30  # seconds per request
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> HermesConfig:
        """Build the canonical config from environment variables."""
        return cls()


@dataclass
class HermesRunState:
    """The canonical run state for a Hermes capture session.

    Mirrors the Swift daemon's `RunState` (run_id, window_title,
    capture_dir, status) but adds the Hermes-specific fields
    (hermes_session_id, computer_use_actions).
    """

    run_id: str
    window_title: str = ""
    capture_dir: str = ""
    hermes_session_id: str = ""
    status: str = "idle"  # idle | running | stopped | error
    computer_use_actions: list[dict[str, Any]] = field(default_factory=list)


class HermesClient:
    """The Hermes Agent computer-use HTTP client.

    Phase-2 stub. Methods are no-ops that build the request +
    log it + return a placeholder response. Full impl lands in
    a follow-up change.
    """

    def __init__(self, config: HermesConfig | None = None) -> None:
        self.config = config or HermesConfig.from_env()
        self._state: HermesRunState | None = None

    def start_run(self, run_id: str, window_title: str) -> HermesRunState:
        """Start a capture run for the named window.

        Phase-2 stub: returns a HermesRunState with `status="running"`.
        The real impl will POST to `{base_url}/runs` with the
        `window_title` + `run_id` + return a `hermes_session_id`.
        """
        self._state = HermesRunState(
            run_id=run_id,
            window_title=window_title,
            capture_dir=f"/Users/cianmacandeisigh/.tuatha/captures/{run_id}/",
            status="running",
        )
        return self._state

    def stop_run(self) -> HermesRunState | None:
        """Stop the active capture run.

        Phase-2 stub: returns the current state with `status="stopped"`.
        The real impl will POST to `{base_url}/runs/{hermes_session_id}/stop`.
        """
        if self._state is None:
            return None
        self._state.status = "stopped"
        return self._state

    def mark_event(self, name: str) -> dict[str, Any]:
        """Write a sidecar event marker.

        Phase-2 stub: returns a placeholder ack. The real impl
        will POST to `{base_url}/runs/{hermes_session_id}/events`
        with the event `name` + timestamp.
        """
        return {
            "event": name,
            "at": "2026-08-27T00:00:00Z",
            "status": "acked",
            "stub": True,
        }

    def hermes_ping(self) -> dict[str, Any]:
        """Ping the Hermes agent endpoint.

        Phase-2 stub: returns a placeholder health check. The
        real impl will GET `{base_url}/health`.
        """
        return {
            "hermes_enabled": True,
            "phase": 2,
            "stub": True,
        }


__all__ = [
    "HERMES_BASE_URL",
    "HermesClient",
    "HermesConfig",
    "HermesRunState",
]
