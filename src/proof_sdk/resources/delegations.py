"""Delegations resource (Proof of Delegation).

A control-proven domain authorizes a typed url/purl artifact for a set of
capability scopes. The attestation is that the domain's controller authorized
the artifact — nothing more; it says nothing about the artifact or the
business behind it.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import (
    DelegateIdentifier,
    DelegationDetail,
    DelegationListItem,
    DelegationListResponse,
)


class Delegations:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        control_proof: str,
        delegate: DelegateIdentifier,
        scope: list[str],
        expires_in: int | None = None,
    ) -> DelegationDetail:
        """Create a delegation from your active domain control proof.

        Each mint is a billable proof. A requested lifetime longer than the
        control proof's remainder is rejected (400), never truncated. The result carries the
        publishable token AND the derived ``effective_status``/``is_valid`` the reads carry —
        the shape of a delegation does not depend on which verb produced it.
        """
        body: dict[str, Any] = {
            "control_proof": control_proof,
            "delegate": delegate,
            "scope": scope,
        }
        if expires_in is not None:
            body["expires_in"] = expires_in
        return await self._http.post("/api/v1/delegations", body)

    async def retrieve(self, id: str) -> DelegationDetail:
        """Get a delegation by Mongo id or ``ph_dlg_*`` handle.

        Returns the stored token plus the derived ``effective_status``/``is_valid``.
        """
        return await self._http.get(f"/api/v1/delegations/{quote(id, safe='')}")

    async def list(
        self,
        *,
        page: int | None = None,
        limit: int | None = None,
        status: str | None = None,
    ) -> DelegationListResponse:
        """List your own delegations (tokens are not included in the list).

        Each item carries the DERIVED ``effective_status``/``is_valid`` beside its stored
        ``status`` — render the derived one, since ``status`` records only whether you revoked
        the delegation yourself. ``status`` (the filter) matches the stored record only.
        """
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if status is not None:
            params["status"] = status
        return await self._http.get("/api/v1/delegations", params)

    async def revoke(self, id: str, *, reason: str | None = None) -> DelegationListItem:
        """Revoke one delegation — the domain proof and sibling delegations stay valid.

        Idempotent: a repeat revoke answers 200 with the same body, here and on
        ``POST /proofs/{handle}/revoke``. (A PROOF differs deliberately — that one answers
        ``400 already_revoked``.) The result carries the derived ``effective_status``/``is_valid``.
        """
        body: dict[str, Any] = {}
        if reason is not None:
            body["reason"] = reason
        return await self._http.post(f"/api/v1/delegations/{quote(id, safe='')}/revoke", body)
