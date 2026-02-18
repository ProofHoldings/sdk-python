"""Tests for resource method routing (correct endpoints and params)."""

from __future__ import annotations

from typing import Any

import pytest

from proof_sdk.resources.verifications import Verifications
from proof_sdk.resources.sessions import Sessions
from proof_sdk.resources.verification_requests import VerificationRequests
from proof_sdk.resources.webhook_deliveries import WebhookDeliveries


@pytest.mark.asyncio
class TestVerifications:
    async def test_create_posts_to_endpoint(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "ver_123", "status": "pending"}
        v = Verifications(mock_http)

        await v.create(type="phone", channel="whatsapp", identifier="+1234567890")

        mock_http.post.assert_awaited_once_with("/api/v1/verifications", {
            "type": "phone",
            "channel": "whatsapp",
            "identifier": "+1234567890",
        })

    async def test_create_includes_optional_params(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "ver_123"}
        v = Verifications(mock_http)

        await v.create(type="phone", channel="sms", identifier="+1", external_user_id="u_1", callback_url="https://cb.io")

        body = mock_http.post.call_args[0][1]
        assert body["external_user_id"] == "u_1"
        assert body["callback_url"] == "https://cb.io"

    async def test_retrieve_gets_by_id(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "ver_123"}
        v = Verifications(mock_http)

        await v.retrieve("ver_123")

        mock_http.get.assert_awaited_once_with("/api/v1/verifications/ver_123")

    async def test_retrieve_encodes_special_chars(self, mock_http: Any) -> None:
        mock_http.get.return_value = {}
        v = Verifications(mock_http)

        await v.retrieve("ver/special&id")

        # quote(safe='') encodes all special chars including /
        mock_http.get.assert_awaited_once_with("/api/v1/verifications/ver%2Fspecial%26id")

    async def test_list_passes_filters(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"data": []}
        v = Verifications(mock_http)

        await v.list(status="verified", limit=10)

        mock_http.get.assert_awaited_once_with("/api/v1/verifications", {"status": "verified", "limit": 10})

    async def test_verify_posts_to_verify_endpoint(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"status": "verified"}
        v = Verifications(mock_http)

        await v.verify("ver_123")

        mock_http.post.assert_awaited_once_with("/api/v1/verifications/ver_123/verify")

    async def test_submit_posts_code(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"status": "verified"}
        v = Verifications(mock_http)

        await v.submit("ver_123", "ABC123")

        mock_http.post.assert_awaited_once_with("/api/v1/verifications/ver_123/submit", {"code": "ABC123"})


@pytest.mark.asyncio
class TestSessions:
    async def test_create_posts(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "ses_123"}
        s = Sessions(mock_http)

        await s.create(channel="telegram")

        mock_http.post.assert_awaited_once_with("/api/v1/sessions", {"channel": "telegram"})

    async def test_retrieve_gets(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "ses_123"}
        s = Sessions(mock_http)

        await s.retrieve("ses_123")

        mock_http.get.assert_awaited_once_with("/api/v1/sessions/ses_123")


@pytest.mark.asyncio
class TestVerificationRequests:
    async def test_create_posts_assets(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "vr_123"}
        vr = VerificationRequests(mock_http)

        await vr.create(assets=[{"type": "phone", "required": True}], reference_id="user_123")

        mock_http.post.assert_awaited_once_with("/api/v1/verification-requests", {
            "assets": [{"type": "phone", "required": True}],
            "reference_id": "user_123",
        })

    async def test_cancel_deletes(self, mock_http: Any) -> None:
        mock_http.delete.return_value = {"status": "cancelled"}
        vr = VerificationRequests(mock_http)

        await vr.cancel("vr_123")

        mock_http.delete.assert_awaited_once_with("/api/v1/verification-requests/vr_123")

    async def test_list_passes_filters(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"data": []}
        vr = VerificationRequests(mock_http)

        await vr.list(status="pending", limit=5)

        mock_http.get.assert_awaited_once_with("/api/v1/verification-requests", {"status": "pending", "limit": 5})


@pytest.mark.asyncio
class TestWebhookDeliveries:
    async def test_list_passes_filters(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"deliveries": []}
        wd = WebhookDeliveries(mock_http)

        await wd.list(status="failed")

        mock_http.get.assert_awaited_once_with("/api/v1/webhook-deliveries", {"status": "failed"})

    async def test_retrieve_gets_by_id(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "del_123"}
        wd = WebhookDeliveries(mock_http)

        await wd.retrieve("del_123")

        mock_http.get.assert_awaited_once_with("/api/v1/webhook-deliveries/del_123")

    async def test_retry_posts(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"success": True}
        wd = WebhookDeliveries(mock_http)

        await wd.retry("del_123")

        mock_http.post.assert_awaited_once_with("/api/v1/webhook-deliveries/del_123/retry")
