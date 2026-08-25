"""tuatha.asset_generation.image_gen.unsloth_client — the OpenAI-compatible Unsloth Studio client.

Per the centralized-model-registry contract: every image-gen + VLM
call routes through the canonical Unsloth Studio endpoint
(`unsloth.cianfhoghlaim.ie:8889`), which exposes:

- POST `/v1/images/generations` — for the image-gen family (Flux2,
  Z-Image-Turbo, Qwen-Image, SDXL, FIBO, DiffusionGemma 26B-A4B,
  Qwen-Image 2512). The model string resolves via
  `MODEL_REGISTRY.resolve("image_gen", role)`.

- POST `/v1/chat/completions` — for the ocr_vision family (Molmo2,
  Qwen3-VL, olmOCR-2, etc.). The model string resolves via
  `MODEL_REGISTRY.resolve("ocr_vision", role)`.

Auth: the `UNSLOTH_API_KEY` env var (Locket-injected via the
Infisical three-way contract).

Retry policy: max 3 retries with exponential backoff on HTTP 5xx
+ connection errors. 4xx responses bubble up immediately (no
retry — they're caller mistakes).
"""
from __future__ import annotations

import os
from typing import Any

# httpx is an optional import — the production UnslothClient path
# needs it, but the ABCs + stub backends should remain importable
# in unit-test sandboxes that haven't installed httpx yet. We
# probe at import time so the rest of the surface can degrade
# gracefully.
try:
    import httpx  # type: ignore[import-not-found]

    _HTTPX_AVAILABLE = True
except ImportError:
    httpx = None  # type: ignore[assignment, misc]
    _HTTPX_AVAILABLE = False

# The two canonical Unsloth endpoints. The hostname is
# `unsloth.cianfhoghlaim.ie` per the 2026-08-25 BonDI stack.
DEFAULT_BASE_URL = "http://unsloth.cianfhoghlaim.ie:8889"
IMAGES_ENDPOINT = "/v1/images/generations"
CHAT_ENDPOINT = "/v1/chat/completions"

# The canonical retry budget per the production-client pattern.
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 0.5
BACKOFF_MULTIPLIER = 2.0


class UnslothClientError(RuntimeError):
    """Raised when the Unsloth Studio endpoint returns a fatal error.

    Distinguished from a transient connection error so callers can
    decide whether to retry or surface to the user.
    """


class UnslothClient:
    """The OpenAI-compatible Unsloth Studio HTTP client.

    Used by both the image-gen router (`/v1/images/generations`)
    and the VLM router (`/v1/chat/completions`). The same client
    handles both endpoints because they share the base URL +
    auth + retry policy.

    Per the dignified-python production-client pattern: no
    module-level mutable state, no hidden connections. Each
    call site constructs / receives its own client (typically
    via `httpx.Client` injected at app start-up).
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str | None = None,
        timeout: float = 60.0,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        # LBYL: prefer the explicit constructor arg, then the env
        # var, then fail loudly with a clear message.
        if api_key is None:
            api_key = os.environ.get("UNSLOTH_API_KEY")
        if not api_key:
            raise UnslothClientError(
                "UNSLOTH_API_KEY is required for the Unsloth Studio "
                "client. Add it to the .infisical.env template and "
                "re-run `bun run secrets:init`."
            )

        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._max_retries = max_retries

        # Reuse one httpx.Client across requests for connection
        # pooling. The client is closed when the user explicitly
        # calls close() or the object is GC'd.
        self._http = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=self._timeout,
        )

    @property
    def base_url(self) -> str:
        """Return the canonical Unsloth Studio base URL."""
        return self._base_url

    def close(self) -> None:
        """Close the underlying HTTP client (idempotent)."""
        self._http.close()

    def __enter__(self) -> UnslothClient:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def generate_image(
        self,
        model: str,
        prompt: str,
        *,
        size: str = "1024x1024",
        n: int = 1,
        extra_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call POST `/v1/images/generations` on the Unsloth Studio.

        Args:
            model: The canonical model key (e.g.,
                `"local/image/qwen-image-2512"`). Resolved via
                `MODEL_REGISTRY.resolve("image_gen", role)` by the
                caller before being passed in.
            prompt: The image-gen prompt (FIBO template, BAML
                output, etc.).
            size: The OpenAI-style `"<W>x<H>"` size string.
            n: The number of images to generate.
            extra_body: Extra fields merged into the JSON body
                (Unsloth-specific extensions).

        Returns:
            The parsed JSON response dict (OpenAI Images API
            shape: `{"created": int, "data": [{"url"|"b64_json"}]}`).

        Raises:
            UnslothClientError: on 4xx (caller mistake) or after
                all retries exhausted on 5xx / connection errors.
        """
        body: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "n": n,
        }
        if extra_body:
            body.update(extra_body)

        response = self._request_with_retry("POST", IMAGES_ENDPOINT, json_body=body)
        return self._parse_json(response)

    def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        extra_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call POST `/v1/chat/completions` on the Unsloth Studio.

        Args:
            model: The canonical model key (e.g.,
                `"molmo2-8b"`). Resolved via
                `MODEL_REGISTRY.resolve("ocr_vision", role)` by the
                caller before being passed in.
            messages: The OpenAI-style messages list
                (`[{"role": "user", "content": "..."}]`).
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Max output tokens.
            extra_body: Extra fields merged into the JSON body
                (Unsloth-specific extensions).

        Returns:
            The parsed JSON response dict (OpenAI Chat Completions
            API shape: `{"choices": [{"message": {"content": "..."}}]}`).

        Raises:
            UnslothClientError: on 4xx (caller mistake) or after
                all retries exhausted on 5xx / connection errors.
        """
        body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if extra_body:
            body.update(extra_body)

        response = self._request_with_retry("POST", CHAT_ENDPOINT, json_body=body)
        return self._parse_json(response)

    # ── Internal helpers ──────────────────────────────────────

    def _request_with_retry(
        self,
        method: str,
        path: str,
        json_body: dict[str, Any],
    ) -> httpx.Response:
        """POST `json_body` to `path` with the canonical retry policy.

        - 5xx + connection errors: retry up to `max_retries` with
          exponential backoff (`initial * multiplier ** attempt`).
        - 4xx: bubble up immediately (no retry — caller mistake).
        - 2xx: return the response.
        """
        last_error: Exception | None = None
        backoff = INITIAL_BACKOFF_SECONDS

        # attempt 0..max_retries inclusive (so max_retries=3 → 4 tries)
        for attempt in range(self._max_retries + 1):
            try:
                response = self._http.request(method, path, json=json_body)
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt >= self._max_retries:
                    raise UnslothClientError(
                        f"Unsloth Studio unreachable after "
                        f"{self._max_retries + 1} attempts: {exc}"
                    ) from exc
                self._sleep(backoff)
                backoff *= BACKOFF_MULTIPLIER
                continue

            # 5xx → retry
            if 500 <= response.status_code < 600:
                last_error = UnslothClientError(
                    f"Unsloth Studio {response.status_code}: "
                    f"{response.text[:200]}"
                )
                if attempt >= self._max_retries:
                    raise last_error
                self._sleep(backoff)
                backoff *= BACKOFF_MULTIPLIER
                continue

            # 4xx → bubble up immediately (no retry)
            if 400 <= response.status_code < 500:
                raise UnslothClientError(
                    f"Unsloth Studio client error {response.status_code}: "
                    f"{response.text[:200]}"
                )

            # 2xx → return
            if 200 <= response.status_code < 300:
                return response

            # Anything else: treat as fatal
            raise UnslothClientError(
                f"Unsloth Studio unexpected status "
                f"{response.status_code}: {response.text[:200]}"
            )

        # Defensive: should be unreachable.
        raise UnslothClientError(
            f"Unsloth Studio exhausted retries: {last_error}"
        )

    @staticmethod
    def _parse_json(response: httpx.Response) -> dict[str, Any]:
        """Parse a 2xx response as JSON.

        Raises UnslothClientError if the body is not valid JSON.
        """
        try:
            data = response.json()
        except ValueError as exc:
            raise UnslothClientError(
                f"Unsloth Studio returned non-JSON body: "
                f"{response.text[:200]}"
            ) from exc

        # LBYL: ensure the parsed payload is a dict.
        if not isinstance(data, dict):
            raise UnslothClientError(
                f"Unsloth Studio returned non-dict JSON: {type(data).__name__}"
            )
        return data

    @staticmethod
    def _sleep(seconds: float) -> None:
        """Sleep helper (isolated for test monkey-patching)."""
        import time

        time.sleep(seconds)


__all__ = [
    "CHAT_ENDPOINT",
    "DEFAULT_BASE_URL",
    "IMAGES_ENDPOINT",
    "MAX_RETRIES",
    "UnslothClient",
    "UnslothClientError",
    "_HTTPX_AVAILABLE",
]
