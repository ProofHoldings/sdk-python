"""Verification requests resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..polling import poll_until_complete
from ..types import (
    CancelRequestResponse,
    VerificationRequest,
    VerificationRequestListResponse,
)

_TERMINAL_STATES = {"completed", "expired", "cancelled"}


class VerificationRequests:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        assets: list[dict[str, Any]],
        reference_id: str | None = None,
        action_type: str | None = None,
        action_context: dict[str, Any] | None = None,
        partial_ok: bool | None = None,
        validity_requirement: str | None = None,
        redirect_url: str | None = None,
        callback_url: str | None = None,
        expires_in: int | None = None,
        public_profile_id: str | None = None,
        proof_expiry_days: int | None = None,
    ) -> VerificationRequest:
        """Create a multi-asset verification request."""
        body: dict[str, Any] = {"assets": assets}
        if reference_id is not None:
            body["reference_id"] = reference_id
        if action_type is not None:
            body["action_type"] = action_type
        if action_context is not None:
            body["action_context"] = action_context
        if partial_ok is not None:
            body["partial_ok"] = partial_ok
        if validity_requirement is not None:
            body["validity_requirement"] = validity_requirement
        if redirect_url is not None:
            body["redirect_url"] = redirect_url
        if callback_url is not None:
            body["callback_url"] = callback_url
        if expires_in is not None:
            body["expires_in"] = expires_in
        if public_profile_id is not None:
            body["public_profile_id"] = public_profile_id
        if proof_expiry_days is not None:
            body["proof_expiry_days"] = proof_expiry_days
        return await self._http.post("/api/v1/verification-requests", body)

    async def retrieve(self, id: str) -> VerificationRequest:
        """Get a verification request by ID."""
        return await self._http.get(f"/api/v1/verification-requests/{quote(id, safe="")}")

    async def list(
        self,
        *,
        status: str | None = None,
        reference_id: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> VerificationRequestListResponse:
        """List verification requests with optional filters."""
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if reference_id is not None:
            params["reference_id"] = reference_id
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page
        return await self._http.get("/api/v1/verification-requests", params)

    async def get_by_reference(self, reference_id: str) -> VerificationRequest:
        """Get a verification request by its reference ID."""
        return await self._http.get(f"/api/v1/verification-requests/by-reference/{quote(reference_id, safe="")}")

    async def get_proofs(self, id: str) -> dict:
        """Get proof tokens for verified assets in a verification request."""
        return await self._http.get(f"/api/v1/verification-requests/{quote(id, safe='')}/proofs")

    async def cancel(self, id: str) -> CancelRequestResponse:
        """Cancel a pending verification request."""
        return await self._http.delete(f"/api/v1/verification-requests/{quote(id, safe="")}")

    async def wait_for_completion(
        self,
        id: str,
        *,
        interval: float = 3.0,
        timeout: float = 600.0,
    ) -> VerificationRequest:
        """Poll until request reaches a terminal state."""
        return await poll_until_complete(
            lambda: self.retrieve(id),
            _TERMINAL_STATES,
            f"Verification request {id}",
            interval=interval,
            timeout=timeout,
        )
