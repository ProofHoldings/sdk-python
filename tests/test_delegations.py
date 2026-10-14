"""Unit tests for the Delegations resource."""

from __future__ import annotations

from typing import Any

import pytest

from proof_sdk.resources import Delegations

PH_DLG = "ph_dlg_" + "a" * 32
PH_CTL = "ph_ctl_" + "b" * 32


@pytest.mark.asyncio
class TestDelegations:
    async def test_create_posts_typed_delegate_body(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "507f1f77bcf86cd799439011", "token": "eyJ.token.sig"}
        d = Delegations(mock_http)

        result = await d.create(
            control_proof=PH_CTL,
            delegate={"type": "purl", "value": "pkg:npm/@postmark/mcp"},
            scope=["email:send"],
            expires_in=3600,
        )

        mock_http.post.assert_awaited_once_with(
            "/api/v1/delegations",
            {
                "control_proof": PH_CTL,
                "delegate": {"type": "purl", "value": "pkg:npm/@postmark/mcp"},
                "scope": ["email:send"],
                "expires_in": 3600,
            },
        )
        assert result["token"] == "eyJ.token.sig"

    async def test_create_omits_optional_expires_in(self, mock_http: Any) -> None:
        mock_http.post.return_value = {}
        d = Delegations(mock_http)

        await d.create(
            control_proof=PH_CTL,
            delegate={"type": "url", "value": "https://mcp.example.com/server"},
            scope=["email:send"],
        )

        body = mock_http.post.await_args.args[1]
        assert "expires_in" not in body

    async def test_retrieve_escapes_id(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "x", "is_valid": True}
        d = Delegations(mock_http)

        await d.retrieve("dlg/special&id")

        mock_http.get.assert_awaited_once_with("/api/v1/delegations/dlg%2Fspecial%26id")

    async def test_retrieve_accepts_handle(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"token": "eyJ.token.sig", "effective_status": "active"}
        d = Delegations(mock_http)

        result = await d.retrieve(PH_DLG)

        mock_http.get.assert_awaited_once_with(f"/api/v1/delegations/{PH_DLG}")
        assert result["effective_status"] == "active"

    async def test_list_builds_query(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"data": [], "pagination": {"page": 1, "limit": 20, "total": 0}}
        d = Delegations(mock_http)

        await d.list(page=2, limit=10, status="revoked")

        mock_http.get.assert_awaited_once_with(
            "/api/v1/delegations", {"page": 2, "limit": 10, "status": "revoked"}
        )

    async def test_list_defaults_to_empty_params(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"data": [], "pagination": {}}
        d = Delegations(mock_http)

        await d.list()

        mock_http.get.assert_awaited_once_with("/api/v1/delegations", {})

    async def test_revoke_posts_reason(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"status": "revoked"}
        d = Delegations(mock_http)

        await d.revoke("507f1f77bcf86cd799439011", reason="key_compromise")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/delegations/507f1f77bcf86cd799439011/revoke",
            {"reason": "key_compromise"},
        )

    async def test_revoke_without_reason_posts_empty_body(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"status": "revoked"}
        d = Delegations(mock_http)

        await d.revoke(PH_DLG)

        mock_http.post.assert_awaited_once_with(f"/api/v1/delegations/{PH_DLG}/revoke", {})
