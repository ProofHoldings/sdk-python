"""Tests for resource method routing (correct endpoints and params)."""

from __future__ import annotations

from typing import Any

import pytest

from proof_sdk.resources.verifications import Verifications
from proof_sdk.resources.sessions import Sessions
from proof_sdk.resources.verification_requests import VerificationRequests
from proof_sdk.resources.webhook_deliveries import WebhookDeliveries
from proof_sdk.resources.confirmations import Confirmations
from proof_sdk.resources.authorizations import Authorizations
from proof_sdk.resources.hitl import Hitl
from proof_sdk.resources.hitl_keys import HitlKeys
from proof_sdk.resources.templates import Templates
from proof_sdk.resources.profiles import Profiles
from proof_sdk.resources.public_profiles import PublicProfiles
from proof_sdk.resources.me import Me


@pytest.mark.asyncio
class TestMe:
    async def test_summary_gets_with_environment(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"as_of": "2026-06-22", "active_api_keys": 1}
        m = Me(mock_http)

        await m.summary(environment="test")

        mock_http.get.assert_awaited_once_with("/api/v1/me/summary", {"environment": "test"})

    async def test_summary_gets_without_params(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"as_of": "2026-06-22"}
        m = Me(mock_http)

        await m.summary()

        mock_http.get.assert_awaited_once_with("/api/v1/me/summary", {})

    async def test_search_passes_query_params(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"data": {}, "total": 0}
        m = Me(mock_http)

        await m.search(q="acme", type="verifications", limit=5)

        mock_http.get.assert_awaited_once_with(
            "/api/v1/me/search", {"q": "acme", "type": "verifications", "limit": 5}
        )

    async def test_api_key_self_gets_singular_endpoint(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "key_1", "key_prefix": "pk_live_"}
        m = Me(mock_http)

        await m.api_key_self()

        mock_http.get.assert_awaited_once_with("/api/v1/me/api-key")

    async def test_api_key_usage_gets_with_encoded_id(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"api_key": {}, "verifications": {}}
        m = Me(mock_http)

        await m.api_key_usage("key/special&id", environment="production")

        mock_http.get.assert_awaited_once_with(
            "/api/v1/me/api-keys/key%2Fspecial%26id/usage", {"environment": "production"}
        )


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

    async def test_create_multi_channel_posts_to_endpoint(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"group_id": "vg_abc", "status": "pending"}
        v = Verifications(mock_http)

        await v.create_multi_channel(type="phone", identifier="+1234567890", channels=["whatsapp", "sms"])

        mock_http.post.assert_awaited_once_with("/api/v1/verifications/multi-channel", {
            "type": "phone",
            "identifier": "+1234567890",
            "channels": ["whatsapp", "sms"],
        })

    async def test_create_multi_channel_passes_optional_fields(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"group_id": "vg_abc"}
        v = Verifications(mock_http)

        await v.create_multi_channel(
            type="phone",
            identifier="+1234567890",
            channels=["telegram"],
            external_user_id="user-1",
            client_metadata={"k": "v"},
            proof_expiry_days=30,
        )

        body = mock_http.post.call_args[0][1]
        assert body["external_user_id"] == "user-1"
        assert body["client_metadata"] == {"k": "v"}
        assert body["proof_expiry_days"] == 30

    async def test_get_multi_channel_status_gets_endpoint(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"group_id": "vg_abc", "status": "pending", "winning_channel": None, "channels": []}
        v = Verifications(mock_http)

        await v.get_multi_channel_status("vg_abc123")

        mock_http.get.assert_awaited_once_with("/api/v1/verifications/multi-channel/vg_abc123/status")

    async def test_get_multi_channel_status_encodes_group_id(self, mock_http: Any) -> None:
        mock_http.get.return_value = {}
        v = Verifications(mock_http)

        await v.get_multi_channel_status("vg/special&id")

        mock_http.get.assert_awaited_once_with("/api/v1/verifications/multi-channel/vg%2Fspecial%26id/status")

    async def test_delete_domain_verification_deletes_encoded_id(self, mock_http: Any) -> None:
        mock_http.delete.return_value = {}
        v = Verifications(mock_http)

        await v.delete_domain_verification("dom/1&x")

        mock_http.delete.assert_awaited_once_with("/api/v1/verifications/domain/dom%2F1%26x")


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


@pytest.mark.asyncio
class TestConfirmations:
    async def test_create_posts_to_endpoint(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "conf_123", "status": "pending"}
        c = Confirmations(mock_http)

        await c.create(hitl_id="hitl_123", message="ciphertext-envelope")

        mock_http.post.assert_awaited_once_with("/api/v1/confirmations", {
            "hitl_id": "hitl_123",
            "message": "ciphertext-envelope",
        })

    async def test_create_includes_proof_expiry_days(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "conf_123"}
        c = Confirmations(mock_http)

        await c.create(hitl_id="hitl_123", message="ct", proof_expiry_days=30)

        body = mock_http.post.call_args[0][1]
        assert body["proof_expiry_days"] == 30

    async def test_retrieve_gets_by_id(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "conf_123"}
        c = Confirmations(mock_http)

        await c.retrieve("conf_123")

        mock_http.get.assert_awaited_once_with("/api/v1/confirmations/conf_123")

    async def test_retrieve_encodes_special_chars(self, mock_http: Any) -> None:
        mock_http.get.return_value = {}
        c = Confirmations(mock_http)

        await c.retrieve("conf/special&id")

        mock_http.get.assert_awaited_once_with("/api/v1/confirmations/conf%2Fspecial%26id")

    async def test_list_passes_filters(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"data": []}
        c = Confirmations(mock_http)

        await c.list(status="pending", hitl_id="hitl_123", start_date="2026-01-01", end_date="2026-02-01", limit=10, page=2)

        mock_http.get.assert_awaited_once_with("/api/v1/confirmations", {
            "status": "pending",
            "hitl_id": "hitl_123",
            "start_date": "2026-01-01",
            "end_date": "2026-02-01",
            "limit": 10,
            "page": 2,
        })

    async def test_list_omits_unset_filters(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"data": []}
        c = Confirmations(mock_http)

        await c.list()

        mock_http.get.assert_awaited_once_with("/api/v1/confirmations", {})


@pytest.mark.asyncio
class TestAuthorizations:
    async def test_create_posts_to_endpoint(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "auth_123", "status": "pending"}
        a = Authorizations(mock_http)

        await a.create(phone="+1234567890", channel="telegram", business_name="Acme")

        mock_http.post.assert_awaited_once_with("/api/v1/authorizations", {
            "phone": "+1234567890",
            "channel": "telegram",
            "business_name": "Acme",
        })

    async def test_retrieve_gets_by_id(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "auth_123"}
        a = Authorizations(mock_http)

        await a.retrieve("auth_123")

        mock_http.get.assert_awaited_once_with("/api/v1/authorizations/auth_123")

    async def test_revoke_sends_reason_body(self, mock_http: Any) -> None:
        mock_http.delete.return_value = {"id": "auth_123", "status": "revoked"}
        a = Authorizations(mock_http)

        await a.revoke("auth_123", reason="no longer needed")

        mock_http.delete.assert_awaited_once_with(
            "/api/v1/authorizations/auth_123", {"reason": "no longer needed"}
        )

    async def test_revoke_without_reason_sends_no_body(self, mock_http: Any) -> None:
        mock_http.delete.return_value = {"id": "auth_123", "status": "revoked"}
        a = Authorizations(mock_http)

        await a.revoke("auth_123")

        mock_http.delete.assert_awaited_once_with("/api/v1/authorizations/auth_123", None)

    async def test_export_passes_filters(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"data": []}
        a = Authorizations(mock_http)

        await a.export(format="csv", status="revoked")

        mock_http.get.assert_awaited_once_with(
            "/api/v1/authorizations/export", {"format": "csv", "status": "revoked"}
        )


@pytest.mark.asyncio
class TestHitlKeys:
    async def test_get_keys(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"kid": "abc"}
        hk = HitlKeys(mock_http)

        await hk.get("hitl_123")

        mock_http.get.assert_awaited_once_with("/api/v1/hitl/hitl_123/keys")

    async def test_upload_puts_key_material(self, mock_http: Any) -> None:
        mock_http.put.return_value = {"kid": "abc"}
        hk = HitlKeys(mock_http)

        await hk.upload(
            "hitl_123",
            public_key="pem",
            encrypted_private_key="enc",
            kdf_salt="salt",
        )

        mock_http.put.assert_awaited_once_with(
            "/api/v1/hitl/hitl_123/keys",
            {"public_key": "pem", "encrypted_private_key": "enc", "kdf_salt": "salt"},
        )

    async def test_delete_keys(self, mock_http: Any) -> None:
        mock_http.delete.return_value = {"success": True}
        hk = HitlKeys(mock_http)

        await hk.delete("hitl_123")

        mock_http.delete.assert_awaited_once_with("/api/v1/hitl/hitl_123/keys")


@pytest.mark.asyncio
class TestHitl:
    async def test_create_posts_to_endpoint(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "hitl_123", "status": "pending"}
        h = Hitl(mock_http)

        await h.create(
            name="Production Approvals",
            channels=[{"type": "telegram", "config": {"chat_id": "12345"}}],
            timeout_seconds=3600,
        )

        mock_http.post.assert_awaited_once_with("/api/v1/hitl", {
            "name": "Production Approvals",
            "channels": [{"type": "telegram", "config": {"chat_id": "12345"}}],
            "timeout_seconds": 3600,
        })

    async def test_create_omits_unset_optional_params(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "hitl_123"}
        h = Hitl(mock_http)

        await h.create(
            name="Minimal",
            channels=[{"type": "whatsapp", "config": {"phone_number": "+12345678901"}}],
        )

        body = mock_http.post.call_args[0][1]
        assert "timeout_seconds" not in body
        assert "profile_id" not in body

    async def test_list_passes_filters(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"data": []}
        h = Hitl(mock_http)

        await h.list(status="active", limit=10)

        mock_http.get.assert_awaited_once_with("/api/v1/hitl", {"status": "active", "limit": 10})

    async def test_list_omits_unset_filters(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"data": []}
        h = Hitl(mock_http)

        await h.list()

        mock_http.get.assert_awaited_once_with("/api/v1/hitl", {})

    async def test_retrieve_gets_by_id(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "hitl_123"}
        h = Hitl(mock_http)

        await h.retrieve("hitl_123")

        mock_http.get.assert_awaited_once_with("/api/v1/hitl/hitl_123")

    async def test_retrieve_encodes_special_chars(self, mock_http: Any) -> None:
        mock_http.get.return_value = {}
        h = Hitl(mock_http)

        await h.retrieve("hitl/special&id")

        mock_http.get.assert_awaited_once_with("/api/v1/hitl/hitl%2Fspecial%26id")

    async def test_update_patches_body(self, mock_http: Any) -> None:
        mock_http.request.return_value = {"id": "hitl_123"}
        h = Hitl(mock_http)

        await h.update("hitl_123", name="Renamed", timeout_seconds=7200)

        mock_http.request.assert_awaited_once_with(
            "PATCH",
            "/api/v1/hitl/hitl_123",
            json={"name": "Renamed", "timeout_seconds": 7200},
        )

    async def test_archive_deletes(self, mock_http: Any) -> None:
        mock_http.delete.return_value = {"id": "hitl_123", "status": "archived"}
        h = Hitl(mock_http)

        await h.archive("hitl_123")

        mock_http.delete.assert_awaited_once_with("/api/v1/hitl/hitl_123")

    async def test_finalize_posts_without_body(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "hitl_123", "status": "active"}
        h = Hitl(mock_http)

        await h.finalize("hitl_123")

        mock_http.post.assert_awaited_once_with("/api/v1/hitl/hitl_123/finalize")

    async def test_request_authorization_posts_to_authorize(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"hitl_id": "hitl_123", "authorizations": []}
        h = Hitl(mock_http)

        await h.request_authorization("hitl_123")

        mock_http.post.assert_awaited_once_with("/api/v1/hitl/hitl_123/authorize")

    async def test_request_authorization_encodes_special_chars(self, mock_http: Any) -> None:
        mock_http.post.return_value = {}
        h = Hitl(mock_http)

        await h.request_authorization("hitl/special&id")

        mock_http.post.assert_awaited_once_with("/api/v1/hitl/hitl%2Fspecial%26id/authorize")

    async def test_create_chat_id_discovery_posts(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"token": "tok", "deep_link": "https://t.me/x"}
        h = Hitl(mock_http)

        await h.create_chat_id_discovery()

        mock_http.post.assert_awaited_once_with("/api/v1/hitl/chat-id-discovery")


@pytest.mark.asyncio
class TestConfirmationsApprovalLink:
    async def test_approval_link_posts_by_id(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"approval_url": "https://api.example.com/resolve?t=x"}
        c = Confirmations(mock_http)

        await c.approval_link("conf_123")

        mock_http.post.assert_awaited_once_with("/api/v1/confirmations/conf_123/approval-link")

    async def test_approval_link_encodes_special_chars(self, mock_http: Any) -> None:
        mock_http.post.return_value = {}
        c = Confirmations(mock_http)

        await c.approval_link("conf/special&id")

        mock_http.post.assert_awaited_once_with("/api/v1/confirmations/conf%2Fspecial%26id/approval-link")


@pytest.mark.asyncio
class TestVerificationRequestProofs:
    async def test_get_proofs_gets_by_id(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"proofs": []}
        vr = VerificationRequests(mock_http)

        await vr.get_proofs("vr_123")

        mock_http.get.assert_awaited_once_with("/api/v1/verification-requests/vr_123/proofs")

    async def test_get_proofs_encodes_special_chars(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"proofs": []}
        vr = VerificationRequests(mock_http)

        await vr.get_proofs("vr/special&id")

        mock_http.get.assert_awaited_once_with("/api/v1/verification-requests/vr%2Fspecial%26id/proofs")


@pytest.mark.asyncio
class TestTemplates:
    async def test_list_gets_templates(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"custom_templates": [], "available_channels": []}
        t = Templates(mock_http)

        await t.list()

        mock_http.get.assert_awaited_once_with("/api/v1/templates")

    async def test_get_defaults(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"defaults": {}}
        t = Templates(mock_http)

        await t.get_defaults()

        mock_http.get.assert_awaited_once_with("/api/v1/templates/defaults")

    async def test_retrieve_gets_channel_and_type(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"is_custom": False, "template": {}}
        t = Templates(mock_http)

        await t.retrieve("telegram", "confirmation_request")

        mock_http.get.assert_awaited_once_with("/api/v1/templates/telegram/confirmation_request")

    async def test_upsert_puts_content(self, mock_http: Any) -> None:
        mock_http.put.return_value = {"success": True, "template": {}}
        t = Templates(mock_http)

        await t.upsert("whatsapp", "verification_request", {"body": "Your code is {{code}}", "button_text": "Verify"})

        mock_http.put.assert_awaited_once_with(
            "/api/v1/templates/whatsapp/verification_request",
            {"body": "Your code is {{code}}", "button_text": "Verify"},
        )

    async def test_delete_deletes_template(self, mock_http: Any) -> None:
        mock_http.delete.return_value = {"success": True, "message": "Template reset to default"}
        t = Templates(mock_http)

        await t.delete("email", "login_request")

        mock_http.delete.assert_awaited_once_with("/api/v1/templates/email/login_request")

    async def test_preview_posts_content(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"preview": {"body": "x"}, "validation_errors": [], "is_valid": True}
        t = Templates(mock_http)

        await t.preview(channel="telegram", message_type="confirmation_request", body="Hi {{business_name}}")

        mock_http.post.assert_awaited_once_with("/api/v1/templates/preview", {
            "channel": "telegram",
            "message_type": "confirmation_request",
            "body": "Hi {{business_name}}",
        })

    async def test_preview_includes_optional_fields(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"preview": {}, "validation_errors": [], "is_valid": True}
        t = Templates(mock_http)

        await t.preview(
            channel="email",
            message_type="2fa_request",
            body="Code: {{code}}",
            subject="Your code",
            button_text="Open",
            button_url_template="https://x.io/{{code}}",
        )

        body = mock_http.post.call_args[0][1]
        assert body["subject"] == "Your code"
        assert body["button_text"] == "Open"
        assert body["button_url_template"] == "https://x.io/{{code}}"

    async def test_render_posts_variables(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"rendered": {"body": "Code: 123456"}}
        t = Templates(mock_http)

        await t.render(channel="sms", message_type="verification_request", variables={"code": "123456"})

        mock_http.post.assert_awaited_once_with("/api/v1/templates/render", {
            "channel": "sms",
            "message_type": "verification_request",
            "variables": {"code": "123456"},
        })

    async def test_render_omits_absent_variables(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"rendered": {}}
        t = Templates(mock_http)

        await t.render(channel="sms", message_type="login_request")

        mock_http.post.assert_awaited_once_with("/api/v1/templates/render", {
            "channel": "sms",
            "message_type": "login_request",
        })


@pytest.mark.asyncio
class TestProfiles:
    async def test_list_gets_profiles(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"profiles": [], "count": 0, "max_profiles": 1}
        p = Profiles(mock_http)

        await p.list()

        mock_http.get.assert_awaited_once_with("/api/v1/me/profiles")

    async def test_create_posts_params(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "pr_1"}
        p = Profiles(mock_http)

        await p.create(display_name="Acme", is_business=True)

        mock_http.post.assert_awaited_once_with("/api/v1/me/profiles", {
            "display_name": "Acme",
            "is_business": True,
        })

    async def test_retrieve_encodes_profile_id(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "pr_1"}
        p = Profiles(mock_http)

        await p.retrieve("pr/special&id")

        mock_http.get.assert_awaited_once_with("/api/v1/me/profiles/pr%2Fspecial%26id")

    async def test_update_patches_profile(self, mock_http: Any) -> None:
        mock_http.request.return_value = {"id": "pr_1"}
        p = Profiles(mock_http)

        await p.update("pr_1", bio="New bio")

        mock_http.request.assert_awaited_once_with("PATCH", "/api/v1/me/profiles/pr_1", json={"bio": "New bio"})

    async def test_delete_deletes_profile(self, mock_http: Any) -> None:
        mock_http.delete.return_value = {"success": True, "message": "Profile deleted"}
        p = Profiles(mock_http)

        await p.delete("pr_1")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/profiles/pr_1")

    async def test_set_primary_posts(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "pr_1", "is_primary": True}
        p = Profiles(mock_http)

        await p.set_primary("pr_1")

        mock_http.post.assert_awaited_once_with("/api/v1/me/profiles/pr_1/primary")

    async def test_list_templates(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"profile_id": "pr_1", "templates": []}
        p = Profiles(mock_http)

        await p.list_templates("pr_1")

        mock_http.get.assert_awaited_once_with("/api/v1/me/profiles/pr_1/templates")

    async def test_update_template_puts_content(self, mock_http: Any) -> None:
        mock_http.put.return_value = {"channel": "telegram", "message_type": "confirmation_request", "is_custom": True}
        p = Profiles(mock_http)

        await p.update_template("pr_1", "telegram", "confirmation_request", {"body": "Approve {{business_name}}?"})

        mock_http.put.assert_awaited_once_with(
            "/api/v1/me/profiles/pr_1/templates/telegram/confirmation_request",
            {"body": "Approve {{business_name}}?"},
        )

    async def test_delete_template(self, mock_http: Any) -> None:
        mock_http.delete.return_value = {"channel": "email", "message_type": "login_request", "is_custom": False}
        p = Profiles(mock_http)

        await p.delete_template("pr_1", "email", "login_request")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/profiles/pr_1/templates/email/login_request")

    async def test_preview_template_posts_content(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"preview": {"body": "x"}, "variables_used": []}
        p = Profiles(mock_http)

        await p.preview_template("pr_1", channel="sms", message_type="2fa_request", body="Code: {{code}}")

        mock_http.post.assert_awaited_once_with("/api/v1/me/profiles/pr_1/templates/preview", {
            "channel": "sms",
            "message_type": "2fa_request",
            "body": "Code: {{code}}",
        })


@pytest.mark.asyncio
class TestPublicProfiles:
    async def test_get_by_id(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"profile_id": "pr_1", "proofs": [], "links": []}
        p = PublicProfiles(mock_http)

        await p.get_by_id("pr_1")

        mock_http.get.assert_awaited_once_with("/api/v1/profiles/p/pr_1")

    async def test_get_by_id_encodes_special_chars(self, mock_http: Any) -> None:
        mock_http.get.return_value = {}
        p = PublicProfiles(mock_http)

        await p.get_by_id("pr/special&id")

        mock_http.get.assert_awaited_once_with("/api/v1/profiles/p/pr%2Fspecial%26id")

    async def test_get_avatar(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"data": b"\x89PNG", "content_type": "image/png"}
        p = PublicProfiles(mock_http)

        result = await p.get_avatar("pr_1")

        mock_http.get.assert_awaited_once_with("/api/v1/profiles/p/pr_1/avatar")
        assert result["content_type"] == "image/png"
        assert isinstance(result["data"], bytes)

    async def test_get_by_username(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"profile_id": "pr_1", "username": "acme"}
        p = PublicProfiles(mock_http)

        await p.get_by_username("acme")

        mock_http.get.assert_awaited_once_with("/api/v1/profiles/u/acme")

    async def test_get_badge(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"username": "team_mgmt", "state": "no_public_record"}
        p = PublicProfiles(mock_http)

        result = await p.get_badge("team_mgmt")

        mock_http.get.assert_awaited_once_with("/api/v1/profiles/badge/team_mgmt")
        # `state` is the field a caller branches on: a username with no public record answers
        # 200, never a 404, so treating a missing badge as an error would be wrong.
        assert result["state"] == "no_public_record"

    async def test_check_username(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"available": True}
        p = PublicProfiles(mock_http)

        result = await p.check_username("acme")

        mock_http.get.assert_awaited_once_with("/api/v1/profiles/check-username/acme")
        assert result["available"] is True
