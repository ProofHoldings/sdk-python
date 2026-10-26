"""Authorizations resource."""

from __future__ import annotations

import warnings
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
        hitl_id: str,
        recipient: str,
        phone: str,
        channel: str,
        scope: str | None = None,
        bsuid: str | None = None,
        business_profile_id: str | None = None,
        expires_in: int | None = None,
        business_name: str | None = None,
    ) -> CreateAuthorizationResponse:
        """Create a consent request for one recipient of an approval setup.

        The consent message names the approval setup's sub-account; ``business_name`` is
        deprecated and ignored by the server (it is still sent if given).
        """
        body: dict[str, Any] = {
            "hitl_id": hitl_id,
            "recipient": recipient,
            "phone": phone,
            "channel": channel,
        }
        if scope is not None:
            body["scope"] = scope
        if bsuid is not None:
            body["bsuid"] = bsuid
        if business_profile_id is not None:
            body["business_profile_id"] = business_profile_id
        if expires_in is not None:
            body["expires_in"] = expires_in
        if business_name is not None:
            warnings.warn(
                "business_name is ignored: the consent message names the approval setup's "
                "sub-account. Stop passing it.",
                DeprecationWarning,
                stacklevel=2,
            )
            body["business_name"] = business_name
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
