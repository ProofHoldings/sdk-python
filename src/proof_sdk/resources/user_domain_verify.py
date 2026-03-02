"""User domain verification resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import DomainCheckResponse, DomainVerificationResponse


class UserDomainVerify:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def start(self, **kwargs: Any) -> DomainVerificationResponse:
        """Start domain verification (self-service)."""
        return await self._http.post("/api/v1/me/verify/domain", kwargs)

    async def status(self, session_id: str) -> dict[str, Any]:
        """Poll domain verification status."""
        sid = quote(session_id, safe='')
        return await self._http.get(f"/api/v1/me/verify/domain/{sid}")

    async def check(self, session_id: str) -> DomainCheckResponse:
        """Check domain verification."""
        sid = quote(session_id, safe='')
        return await self._http.post(f"/api/v1/me/verify/domain/{sid}/check")
