"""HTTP client for the proof.holdings API."""

from __future__ import annotations

import asyncio
import math
from typing import Any

import httpx

from .errors import ProofError, NetworkError, RequestTimeoutError
from .version import VERSION


class HttpClient:
    """Low-level HTTP client with retry, backoff, and rate limit handling."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: float,
        max_retries: int,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._max_retries = max_retries
        self._client: httpx.AsyncClient | None = None
        # A second, credential-free client for public artifacts — see `fetch_public`.
        self._public_client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self._timeout,
                # Follow redirects like the JS (fetch), Go (http.Client), and
                # PHP (Guzzle) SDKs do by default — the avatar endpoint
                # 301-redirects for https-hosted avatars.
                follow_redirects=True,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": f"proof-sdk-python/{VERSION}",
                },
            )
        return self._client

    async def fetch_public(
        self,
        url: str,
        *,
        timeout: float,
        headers: dict[str, str] | None = None,
        max_bytes: int = 512 * 1024,
    ) -> tuple[int, httpx.Headers, bytes]:
        """Fetch a PUBLIC artifact by absolute url — no API key, no retries, no redirects.

        The key is left off deliberately rather than forgotten: the issuer's status list is a
        shared document whose whole point is that reading it says nothing about WHICH proof is
        being checked. Sending a credential with it would hand the issuer the one fact the design
        withholds. Redirects are refused because the caller has already decided the url's origin
        is trusted, and a redirect would move it.

        The body is STREAMED and abandoned one byte past ``max_bytes``: reading it whole and
        measuring afterwards would make the ceiling a check on a document already in memory,
        which is no ceiling at all for a response that declares no length.
        """
        if self._public_client is None or self._public_client.is_closed:
            self._public_client = httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=False,
                headers={"User-Agent": f"proof-sdk-python/{VERSION}"},
            )

        client = self._public_client

        async def transfer() -> tuple[int, httpx.Headers, bytes]:
            body = bytearray()
            async with client.stream("GET", url, headers=headers or {}, timeout=timeout) as response:
                async for chunk in response.aiter_bytes():
                    body.extend(chunk)
                    if len(body) > max_bytes:
                        break
                return response.status_code, response.headers, bytes(body[: max_bytes + 1])

        # ONE deadline over the whole transfer. httpx's `timeout` bounds each socket operation,
        # and the loop above restarts it on every chunk, so a server trickling bytes could hold
        # this call far past its own timeout — measured at 8s under a 2s timeout before this.
        # `wait_for` rather than `asyncio.timeout`, which only exists from Python 3.11.
        return await asyncio.wait_for(transfer(), timeout)

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
        if self._public_client and not self._public_client.is_closed:
            await self._public_client.aclose()
            self._public_client = None

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        # Filter None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        last_error: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                client = self._get_client()
                response = await client.request(method, path, json=json, params=params)

                # Rate limiting - retry with backoff
                if response.status_code == 429 and attempt < self._max_retries:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else self._backoff(attempt)
                    await asyncio.sleep(delay)
                    continue

                # Server errors - retry with backoff
                if response.status_code >= 500 and attempt < self._max_retries:
                    await asyncio.sleep(self._backoff(attempt))
                    continue

                # Non-JSON success (e.g. avatar images): return a
                # {data, content_type} envelope instead of attempting a JSON
                # parse. Only when the server EXPLICITLY declares a non-JSON
                # content type — responses without a Content-Type header keep
                # the legacy JSON-parse path.
                content_type = response.headers.get("content-type", "")
                if (
                    response.status_code < 400
                    and content_type
                    and "application/json" not in content_type
                ):
                    if response.content:
                        return {"data": response.content, "content_type": content_type}
                    return {}

                # Parse response
                try:
                    body = response.json()
                except Exception:
                    body = {}

                # Error responses
                if response.status_code >= 400:
                    api_error = body.get("error") if isinstance(body, dict) else None
                    raise ProofError.from_response(response.status_code, api_error)

                return body

            except ProofError:
                raise
            except httpx.TimeoutException as e:
                last_error = e
                if attempt < self._max_retries:
                    await asyncio.sleep(self._backoff(attempt))
                    continue
                raise RequestTimeoutError(f"Request to {method} {path} timed out after {self._timeout}s")
            except httpx.HTTPError as e:
                last_error = e
                if attempt < self._max_retries:
                    await asyncio.sleep(self._backoff(attempt))
                    continue

        raise NetworkError(str(last_error) if last_error else "Network request failed")

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self.request("GET", path, params=params)

    async def post(self, path: str, json: Any = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self.request("POST", path, json=json, params=params)

    async def put(self, path: str, json: Any = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self.request("PUT", path, json=json, params=params)

    async def delete(self, path: str, json: Any = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self.request("DELETE", path, json=json, params=params)

    @staticmethod
    def _backoff(attempt: int) -> float:
        return min(1.0 * math.pow(2, attempt), 10.0)
