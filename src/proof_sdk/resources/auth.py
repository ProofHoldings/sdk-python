"""Auth resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import AuthUser, ListSessionsResponse, SuccessResponse


class Auth:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def get_me(self) -> AuthUser:
        """Get the current authenticated user."""
        return await self._http.get("/api/v1/auth/me")

    async def list_sessions(self) -> ListSessionsResponse:
        """List all active sessions for the current user."""
        return await self._http.get("/api/v1/auth/sessions")

    async def revoke_session(self, session_id: str) -> SuccessResponse:
        """Revoke a specific session."""
        sid = quote(session_id, safe="")
        return await self._http.delete(f"/api/v1/auth/sessions/{sid}")
