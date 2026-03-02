"""DNS Credentials resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import SuccessResponse


class DnsCredentials:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self) -> dict[str, Any]:
        """List all DNS credentials."""
        return await self._http.get("/api/v1/me/dns-credentials")

    async def create(self, **kwargs: Any) -> dict[str, Any]:
        """Create a DNS credential."""
        return await self._http.post("/api/v1/me/dns-credentials", kwargs)

    async def delete(self, credential_id: str) -> SuccessResponse:
        """Delete a DNS credential."""
        cid = quote(credential_id, safe="")
        return await self._http.delete(f"/api/v1/me/dns-credentials/{cid}")
