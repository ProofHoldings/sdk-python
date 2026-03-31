"""User verification requests resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import CancelRequestResponse, SuccessResponse, VerificationRequest, VerificationRequestListResponse


class UserRequests:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self) -> VerificationRequestListResponse:
        """List my verification requests."""
        return await self._http.get("/api/v1/me/verification-requests")

    async def list_incoming(self) -> VerificationRequestListResponse:
        """List incoming verification requests."""
        return await self._http.get("/api/v1/me/verification-requests/incoming")

    async def create(self, **kwargs: Any) -> VerificationRequest:
        """Create a verification request."""
        return await self._http.post("/api/v1/me/verification-requests", kwargs)

    async def claim(self, request_id: str) -> SuccessResponse:
        """Claim assets from a verification request."""
        rid = quote(request_id, safe='')
        return await self._http.post(f"/api/v1/me/verification-requests/{rid}/claim")

    async def cancel(self, request_id: str) -> CancelRequestResponse:
        """Cancel a verification request."""
        rid = quote(request_id, safe='')
        return await self._http.delete(f"/api/v1/me/verification-requests/{rid}")

    async def extend(self, request_id: str) -> VerificationRequest:
        """Extend a verification request."""
        rid = quote(request_id, safe='')
        return await self._http.post(f"/api/v1/me/verification-requests/{rid}/extend")

    async def share_email(self, request_id: str) -> SuccessResponse:
        """Share verification request via email."""
        rid = quote(request_id, safe='')
        return await self._http.post(f"/api/v1/me/verification-requests/{rid}/share-email")
