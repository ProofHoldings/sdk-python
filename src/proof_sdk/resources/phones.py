"""Phones resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import SuccessResponse, UserPhone


class Phones:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self) -> list[UserPhone]:
        """List all phones for the authenticated user."""
        return await self._http.get("/api/v1/me/phones")

    async def remove(self, phone_id: str) -> SuccessResponse:
        """Remove a phone by ID."""
        pid = quote(phone_id, safe="")
        return await self._http.delete(f"/api/v1/me/phones/{pid}")

    async def set_primary(self, phone_id: str) -> UserPhone:
        """Set a phone as the primary phone."""
        pid = quote(phone_id, safe="")
        return await self._http.put(f"/api/v1/me/phones/{pid}/primary")

    async def start_add(self, *, channel: str) -> dict[str, Any]:
        """Start adding a new phone.

        Args:
            channel: Verification channel ('telegram', 'whatsapp', or 'sms').
        """
        return await self._http.post("/api/v1/me/phones/add", {"channel": channel})

    async def get_add_status(self, session_id: str) -> dict[str, Any]:
        """Get the status of a phone add session."""
        sid = quote(session_id, safe="")
        return await self._http.get(f"/api/v1/me/phones/add/{sid}")
