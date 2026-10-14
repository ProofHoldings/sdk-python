"""Authorizations resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import (
    Authorization,
    AuthorizationListResponse,
    CreateAuthorizationResponse,
)


class Authorizations:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        phone: str,
        channel: str,
        business_name: str,
        scope: str | None = None,
        business_profile_id: str | None = None,
        expires_in: int | None = None,
    ) -> CreateAuthorizationResponse:
        """Create a new authorization request."""
        body: dict[str, Any] = {
            "phone": phone,
            "channel": channel,
            "business_name": business_name,
        }
        if scope is not None:
            body["scope"] = scope
        if business_profile_id is not None:
            body["business_profile_id"] = business_profile_id
        if expires_in is not None:
            body["expires_in"] = expires_in
        return await self._http.post("/api/v1/authorizations", body)

    async def retrieve(self, id: str) -> Authorization:
        """Get an authorization by ID."""
        return await self._http.get(f"/api/v1/authorizations/{quote(id, safe='')}")

    async def list(
        self,
        *,
        status: str | None = None,
        phone: str | None = None,
        channel: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> AuthorizationListResponse:
        """List authorizations with optional filters."""
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if phone is not None:
            params["phone"] = phone
        if channel is not None:
            params["channel"] = channel
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page
        return await self._http.get("/api/v1/authorizations", params)

    async def revoke(
        self,
        id: str,
        *,
        reason: str | None = None,
    ) -> Authorization:
        """Revoke an authorization."""
        body = {"reason": reason} if reason is not None else None
        return await self._http.delete(f"/api/v1/authorizations/{quote(id, safe='')}", body)

    async def export(
        self,
        *,
        format: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """Export authorizations as CSV or JSON."""
        params: dict[str, Any] = {}
        if format is not None:
            params["format"] = format
        if from_ is not None:
            params["from"] = from_
        if to is not None:
            params["to"] = to
        if status is not None:
            params["status"] = status
        return await self._http.get("/api/v1/authorizations/export", params)
