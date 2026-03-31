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

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self._timeout,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": f"proof-sdk-python/{VERSION}",
                },
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

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

    async def post(self, path: str, json: Any = None) -> dict[str, Any]:
        return await self.request("POST", path, json=json)

    async def put(self, path: str, json: Any = None) -> dict[str, Any]:
        return await self.request("PUT", path, json=json)

    async def patch(self, path: str, json: Any = None) -> dict[str, Any]:
        return await self.request("PATCH", path, json=json)

    async def delete(self, path: str, json: Any = None) -> dict[str, Any]:
        return await self.request("DELETE", path, json=json)

    @staticmethod
    def _backoff(attempt: int) -> float:
        return min(1.0 * math.pow(2, attempt), 10.0)
