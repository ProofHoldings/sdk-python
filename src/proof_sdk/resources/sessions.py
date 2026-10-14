"""Sessions resource."""

from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..polling import poll_until_complete

_TERMINAL_STATES = {"verified", "failed", "expired"}


class Sessions:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        channel: str,
        client_metadata: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new phone verification session."""
        body: dict[str, Any] = {"channel": channel}
        if client_metadata is not None:
            body["client_metadata"] = client_metadata
        if context is not None:
            body["context"] = context
        return await self._http.post("/api/v1/sessions", body)

    async def retrieve(self, id: str) -> dict[str, Any]:
        """Get session status by ID."""
        return await self._http.get(f"/api/v1/sessions/{quote(id)}")

    async def wait_for_completion(
        self,
        id: str,
        *,
        interval: float = 2.0,
        timeout: float = 600.0,
        backoff: float = 1.5,
        max_interval: float = 30.0,
        jitter: float = 0.5,
        cancel_event: asyncio.Event | None = None,
    ) -> dict[str, Any]:
        """Poll until session reaches a terminal state.

        Uses exponential backoff with jitter per the standard polling contract.
        Pass ``cancel_event`` (an :class:`asyncio.Event`) to abort polling early.
        """
        return await poll_until_complete(
            lambda: self.retrieve(id),
            _TERMINAL_STATES,
            f"Session {id}",
            interval=interval,
            timeout=timeout,
            backoff=backoff,
            max_interval=max_interval,
            jitter=jitter,
            cancel_event=cancel_event,
        )
