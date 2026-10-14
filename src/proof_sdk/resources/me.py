"""Account / Me resource: the authenticated account's dashboard/agent data surface."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient


class Me:
    """Authenticated-account data surface (dual-auth: JWT or API key)."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def summary(self, environment: str | None = None) -> dict[str, Any]:
        """One-call account snapshot: quota + end-of-month projection, request
        health, per-channel completion rates, HITL counts, active API keys.

        ``GET /api/v1/me/summary``
        """
        params: dict[str, Any] = {}
        if environment is not None:
            params["environment"] = environment
        return await self._http.get("/api/v1/me/summary", params)

    async def search(
        self,
        q: str,
        type: str | None = None,
        environment: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Prefix-anchored global account search across six resource buckets.

        ``GET /api/v1/me/search``
        """
        params: dict[str, Any] = {"q": q}
        if type is not None:
            params["type"] = type
        if environment is not None:
            params["environment"] = environment
        if limit is not None:
            params["limit"] = limit
        return await self._http.get("/api/v1/me/search", params)

    async def api_key_self(self) -> dict[str, Any]:
        """Retrieve the calling API key's own redacted metadata (agent
        self-inspection). The backend returns 400 api_key_required for a JWT
        caller, but SDK callers always authenticate with an API key.

        ``GET /api/v1/me/api-key``
        """
        return await self._http.get("/api/v1/me/api-key")

    async def api_key_usage(self, id: str, environment: str | None = None) -> dict[str, Any]:
        """Per-API-key usage counts (verifications, requests, confirmations,
        authorizations) plus attribution context for key ``id`` and every key it
        replaced (``api_key.replaced_key_ids``).

        ``GET /api/v1/me/api-keys/:id/usage``
        """
        params: dict[str, Any] = {}
        if environment is not None:
            params["environment"] = environment
        return await self._http.get(f"/api/v1/me/api-keys/{quote(id, safe='')}/usage", params)
