"""Verifications resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..polling import poll_until_complete

_TERMINAL_STATES = {"verified", "failed", "expired", "revoked"}


class Verifications:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        type: str,
        channel: str,
        identifier: str,
        external_user_id: str | None = None,
        callback_url: str | None = None,
        client_metadata: dict[str, Any] | None = None,
        dns_provider: dict[str, str] | None = None,
        email_prefix: str | None = None,
    ) -> dict[str, Any]:
        """Create a new verification."""
        body: dict[str, Any] = {"type": type, "channel": channel, "identifier": identifier}
        if external_user_id is not None:
            body["external_user_id"] = external_user_id
        if callback_url is not None:
            body["callback_url"] = callback_url
        if client_metadata is not None:
            body["client_metadata"] = client_metadata
        if dns_provider is not None:
            body["dns_provider"] = dns_provider
        if email_prefix is not None:
            body["email_prefix"] = email_prefix
        return await self._http.post("/api/v1/verifications", body)

    async def retrieve(self, id: str) -> dict[str, Any]:
        """Get a verification by ID."""
        return await self._http.get(f"/api/v1/verifications/{quote(id)}")

    async def list(
        self,
        *,
        status: str | None = None,
        type: str | None = None,
        channel: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """List verifications with optional filters."""
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if type is not None:
            params["type"] = type
        if channel is not None:
            params["channel"] = channel
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page
        return await self._http.get("/api/v1/verifications", params)

    async def verify(self, id: str) -> dict[str, Any]:
        """Trigger a DNS/HTTP verification check."""
        return await self._http.post(f"/api/v1/verifications/{quote(id)}/verify")

    async def submit(self, id: str, code: str) -> dict[str, Any]:
        """Submit an OTP/challenge code."""
        return await self._http.post(f"/api/v1/verifications/{quote(id)}/submit", {"code": code})

    async def wait_for_completion(
        self,
        id: str,
        *,
        interval: float = 3.0,
        timeout: float = 600.0,
    ) -> dict[str, Any]:
        """Poll until verification reaches a terminal state."""
        return await poll_until_complete(
            lambda: self.retrieve(id),
            _TERMINAL_STATES,
            f"Verification {id}",
            interval=interval,
            timeout=timeout,
        )
