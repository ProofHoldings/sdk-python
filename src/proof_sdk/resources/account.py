"""Account resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import SuccessResponse


class Account:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def initiate_deletion(self) -> dict[str, Any]:
        """Initiate account deletion flow."""
        return await self._http.post("/api/v1/me/account/delete", {})

    async def deletion_status(self, session_id: str) -> dict[str, Any]:
        """Get account deletion session status."""
        sid = quote(session_id, safe="")
        return await self._http.get(f"/api/v1/me/account/delete/{sid}")

    async def verify_deletion(self, session_id: str, **kwargs: Any) -> dict[str, Any]:
        """Verify account deletion via email code."""
        sid = quote(session_id, safe="")
        return await self._http.post(f"/api/v1/me/account/delete/{sid}/verify", kwargs)

    async def verify_deletion_magic_link(self, token: str) -> SuccessResponse:
        """Verify account deletion via magic link."""
        return await self._http.post(f"/api/v1/me/account/delete/magic/{quote(token, safe='')}")

    async def delete(self, **kwargs: Any) -> SuccessResponse:
        """Finalize account deletion (requires confirmed session_id)."""
        return await self._http.request("DELETE", "/api/v1/me/account", json=kwargs)
