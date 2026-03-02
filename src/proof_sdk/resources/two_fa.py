"""TwoFA resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import SuccessResponse


class TwoFA:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def start(self, **kwargs: Any) -> dict[str, Any]:
        """Start a 2FA session. Requires action_type and channel."""
        return await self._http.post("/api/v1/me/2fa/start", kwargs)

    async def get_status(self, session_id: str) -> dict[str, Any]:
        """Poll 2FA session status."""
        sid = quote(session_id, safe="")
        return await self._http.get(f"/api/v1/me/2fa/{sid}")

    async def verify(self, session_id: str, **kwargs: Any) -> dict[str, Any]:
        """Verify 2FA code."""
        sid = quote(session_id, safe="")
        return await self._http.post(f"/api/v1/me/2fa/{sid}/verify", kwargs)

    async def verify_magic_link(self, token: str) -> SuccessResponse:
        """Verify 2FA via magic link."""
        return await self._http.post(f"/api/v1/me/2fa/magic/{quote(token, safe='')}")
