"""API Keys resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import APIKeyResponse, SuccessResponse


class ApiKeys:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self) -> list[APIKeyResponse]:
        """List all API keys."""
        return await self._http.get("/api/v1/me/api-keys")

    async def create(self, **kwargs: Any) -> APIKeyResponse:
        """Create a new API key.

        Args:
            name: Optional key name.
            environment: 'production' or 'test'.
            scopes: List of permission scopes.
        """
        return await self._http.post("/api/v1/me/api-keys", kwargs)

    async def revoke(self, key_id: str) -> SuccessResponse:
        """Revoke an API key."""
        kid = quote(key_id, safe="")
        return await self._http.delete(f"/api/v1/me/api-keys/{kid}")

    async def regenerate(self, key_id: str) -> APIKeyResponse:
        """Regenerate an API key."""
        kid = quote(key_id, safe="")
        return await self._http.post(f"/api/v1/me/api-keys/{kid}/regenerate")
