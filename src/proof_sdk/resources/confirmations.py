"""Confirmations resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import (
    Confirmation,
    ConfirmationListResponse,
)


class Confirmations:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        hitl_id: str,
        message: str,
        proof_expiry_days: int | None = None,
    ) -> Confirmation:
        """Create a new confirmation request."""
        body: dict[str, Any] = {"hitl_id": hitl_id, "message": message}
        if proof_expiry_days is not None:
            body["proof_expiry_days"] = proof_expiry_days
        return await self._http.post("/api/v1/confirmations", body)

    async def retrieve(self, id: str) -> Confirmation:
        """Get a confirmation by ID."""
        return await self._http.get(f"/api/v1/confirmations/{quote(id, safe='')}")

    async def list(
        self,
        *,
        status: str | None = None,
        hitl_id: str | None = None,
        search: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> ConfirmationListResponse:
        """List confirmations with optional filters."""
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if hitl_id is not None:
            params["hitl_id"] = hitl_id
        if search is not None:
            params["search"] = search
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page
        return await self._http.get("/api/v1/confirmations", params)
