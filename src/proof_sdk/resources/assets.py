"""Assets resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import SuccessResponse, UserAsset


class Assets:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(
        self,
        *,
        asset_type: str | None = None,
        status: str | None = None,
    ) -> list[UserAsset]:
        """List all verified assets for the authenticated user.

        Args:
            asset_type: Filter by asset type ('phone', 'email', 'domain', 'social', 'wallet').
            status: Filter by status ('active', 'expired', 'revoked').
        """
        params: dict[str, str] = {}
        if asset_type is not None:
            params["type"] = asset_type
        if status is not None:
            params["status"] = status
        return await self._http.get("/api/v1/me/assets", params=params)

    async def get(self, asset_id: str) -> UserAsset:
        """Get a specific asset by ID."""
        aid = quote(asset_id, safe="")
        return await self._http.get(f"/api/v1/me/assets/{aid}")

    async def revoke(self, asset_id: str) -> SuccessResponse:
        """Revoke an asset by ID."""
        aid = quote(asset_id, safe="")
        return await self._http.delete(f"/api/v1/me/assets/{aid}")
