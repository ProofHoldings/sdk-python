"""HITL configs resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import (
    Hitl,
    HitlListResponse,
)


class HitlConfigs:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        channels: list[dict[str, Any]],
        name: str | None = None,
        timeout_seconds: int | None = None,
    ) -> Hitl:
        """Create a new HITL config."""
        body: dict[str, Any] = {"channels": channels}
        if name is not None:
            body["name"] = name
        if timeout_seconds is not None:
            body["timeout_seconds"] = timeout_seconds
        return await self._http.post("/api/v1/hitl", body)

    async def retrieve(self, id: str) -> Hitl:
        """Get a HITL config by ID."""
        return await self._http.get(f"/api/v1/hitl/{quote(id, safe='')}")

    async def list(
        self,
        *,
        status: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> HitlListResponse:
        """List HITL configs with optional filters."""
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page
        return await self._http.get("/api/v1/hitl", params)

    async def update(
        self,
        id: str,
        *,
        name: str | None = None,
        channels: list[dict[str, Any]] | None = None,
        timeout_seconds: int | None = None,
    ) -> Hitl:
        """Update a HITL config."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if channels is not None:
            body["channels"] = channels
        if timeout_seconds is not None:
            body["timeout_seconds"] = timeout_seconds
        return await self._http.patch(f"/api/v1/hitl/{quote(id, safe='')}", body)

    async def delete(self, id: str) -> Hitl:
        """Delete (archive) a HITL config."""
        return await self._http.delete(f"/api/v1/hitl/{quote(id, safe='')}")

    async def request_authorization(self, id: str) -> dict[str, Any]:
        """Request authorization for a HITL config — sends consent to all configured channels."""
        return await self._http.post(f"/api/v1/hitl/{quote(id, safe='')}/authorize", {})

    async def create_chat_id_discovery(self) -> dict[str, Any]:
        """Create a Telegram chat ID discovery token — returns deep link and QR code."""
        return await self._http.post("/api/v1/hitl/chat-id-discovery", {})

    async def poll_chat_id_discovery(self, token: str) -> dict[str, Any]:
        """Poll a chat ID discovery token — returns discovered chat ID when user interacts with bot."""
        return await self._http.get(f"/api/v1/hitl/chat-id-discovery/{quote(token, safe='')}")
