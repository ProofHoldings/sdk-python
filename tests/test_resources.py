"""Tests for resource method routing (correct endpoints and params)."""

from __future__ import annotations

import pytest

from proof_sdk.http import HttpClient

from proof_sdk.resources.verifications import Verifications
from proof_sdk.resources.sessions import Sessions
from proof_sdk.resources.verification_requests import VerificationRequests
from proof_sdk.resources.webhook_deliveries import WebhookDeliveries
from proof_sdk.resources.templates import Templates
from proof_sdk.resources.profiles import Profiles
from proof_sdk.resources.projects import Projects
from proof_sdk.resources.billing import Billing
from proof_sdk.resources.phones import Phones
from proof_sdk.resources.emails import Emails
from proof_sdk.resources.assets import Assets
from proof_sdk.resources.auth import Auth
from proof_sdk.resources.settings import Settings
from proof_sdk.resources.api_keys import ApiKeys


@pytest.mark.asyncio
class TestVerifications:
    async def test_create_posts_to_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "ver_123", "status": "pending"}
        v = Verifications(mock_http)

        await v.create(type="phone", channel="whatsapp", identifier="+1234567890")

        mock_http.post.assert_awaited_once_with("/api/v1/verifications", {
            "type": "phone",
            "channel": "whatsapp",
            "identifier": "+1234567890",
        })

    async def test_create_includes_optional_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "ver_123"}
        v = Verifications(mock_http)

        await v.create(type="phone", channel="sms", identifier="+1", external_user_id="u_1", callback_url="https://cb.io")

        body = mock_http.post.call_args[0][1]
        assert body["external_user_id"] == "u_1"
        assert body["callback_url"] == "https://cb.io"

    async def test_retrieve_gets_by_id(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "ver_123"}
        v = Verifications(mock_http)

        await v.retrieve("ver_123")

        mock_http.get.assert_awaited_once_with("/api/v1/verifications/ver_123")

    async def test_retrieve_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {}
        v = Verifications(mock_http)

        await v.retrieve("ver/special&id")

        # quote(safe='') encodes all special chars including /
        mock_http.get.assert_awaited_once_with("/api/v1/verifications/ver%2Fspecial%26id")

    async def test_list_passes_filters(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"data": []}
        v = Verifications(mock_http)

        await v.list(status="verified", limit=10)

        mock_http.get.assert_awaited_once_with("/api/v1/verifications", {"status": "verified", "limit": 10})

    async def test_verify_posts_to_verify_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"status": "verified"}
        v = Verifications(mock_http)

        await v.verify("ver_123")

        mock_http.post.assert_awaited_once_with("/api/v1/verifications/ver_123/verify")

    async def test_submit_posts_code(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"status": "verified"}
        v = Verifications(mock_http)

        await v.submit("ver_123", "ABC123")

        mock_http.post.assert_awaited_once_with("/api/v1/verifications/ver_123/submit", {"code": "ABC123"})


@pytest.mark.asyncio
class TestSessions:
    async def test_create_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "ses_123"}
        s = Sessions(mock_http)

        await s.create(channel="telegram")

        mock_http.post.assert_awaited_once_with("/api/v1/sessions", {"channel": "telegram"})

    async def test_retrieve_gets(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "ses_123"}
        s = Sessions(mock_http)

        await s.retrieve("ses_123")

        mock_http.get.assert_awaited_once_with("/api/v1/sessions/ses_123")


@pytest.mark.asyncio
class TestVerificationRequests:
    async def test_create_posts_assets(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "vr_123"}
        vr = VerificationRequests(mock_http)

        await vr.create(assets=[{"type": "phone", "required": True}], reference_id="user_123")

        mock_http.post.assert_awaited_once_with("/api/v1/verification-requests", {
            "assets": [{"type": "phone", "required": True}],
            "reference_id": "user_123",
        })

    async def test_cancel_deletes(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"status": "cancelled"}
        vr = VerificationRequests(mock_http)

        await vr.cancel("vr_123")

        mock_http.delete.assert_awaited_once_with("/api/v1/verification-requests/vr_123")

    async def test_list_passes_filters(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"data": []}
        vr = VerificationRequests(mock_http)

        await vr.list(status="pending", limit=5)

        mock_http.get.assert_awaited_once_with("/api/v1/verification-requests", {"status": "pending", "limit": 5})


@pytest.mark.asyncio
class TestWebhookDeliveries:
    async def test_list_passes_filters(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"deliveries": []}
        wd = WebhookDeliveries(mock_http)

        await wd.list(status="failed")

        mock_http.get.assert_awaited_once_with("/api/v1/webhook-deliveries", {"status": "failed"})

    async def test_retrieve_gets_by_id(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "del_123"}
        wd = WebhookDeliveries(mock_http)

        await wd.retrieve("del_123")

        mock_http.get.assert_awaited_once_with("/api/v1/webhook-deliveries/del_123")

    async def test_retry_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        wd = WebhookDeliveries(mock_http)

        await wd.retry("del_123")

        mock_http.post.assert_awaited_once_with("/api/v1/webhook-deliveries/del_123/retry")


@pytest.mark.asyncio
class TestTemplates:
    async def test_list_gets_templates(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"custom_templates": []}
        t = Templates(mock_http)

        await t.list()

        mock_http.get.assert_awaited_once_with("/api/v1/templates")

    async def test_get_defaults(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"defaults": {}}
        t = Templates(mock_http)

        await t.get_defaults()

        mock_http.get.assert_awaited_once_with("/api/v1/templates/defaults")

    async def test_retrieve_by_channel_and_type(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"is_custom": False, "template": {}}
        t = Templates(mock_http)

        await t.retrieve("email", "verification_request")

        mock_http.get.assert_awaited_once_with("/api/v1/templates/email/verification_request")

    async def test_retrieve_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {}
        t = Templates(mock_http)

        await t.retrieve("sms/special", "2fa&request")

        mock_http.get.assert_awaited_once_with("/api/v1/templates/sms%2Fspecial/2fa%26request")

    async def test_upsert_puts_template(self, mock_http: HttpClient) -> None:
        mock_http.put.return_value = {"success": True, "template": {}}
        t = Templates(mock_http)

        await t.upsert("telegram", "login_request", body="Hello {{code}}")

        mock_http.put.assert_awaited_once_with(
            "/api/v1/templates/telegram/login_request",
            {"body": "Hello {{code}}"},
        )

    async def test_upsert_includes_optional_params(self, mock_http: HttpClient) -> None:
        mock_http.put.return_value = {"success": True}
        t = Templates(mock_http)

        await t.upsert("email", "verification_request", body="Test", subject="Verify", button_text="Click")

        body = mock_http.put.call_args[0][1]
        assert body["subject"] == "Verify"
        assert body["button_text"] == "Click"

    async def test_delete_template(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        t = Templates(mock_http)

        await t.delete("whatsapp", "verification_success")

        mock_http.delete.assert_awaited_once_with("/api/v1/templates/whatsapp/verification_success")

    async def test_preview_posts_content(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"preview": {}, "is_valid": True}
        t = Templates(mock_http)

        await t.preview(channel="email", message_type="verification_request", body="Test {{code}}")

        mock_http.post.assert_awaited_once_with("/api/v1/templates/preview", {
            "channel": "email",
            "message_type": "verification_request",
            "body": "Test {{code}}",
        })

    async def test_render_posts_variables(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"rendered": {}}
        t = Templates(mock_http)

        await t.render(channel="sms", message_type="2fa_request", variables={"code": "123456"})

        mock_http.post.assert_awaited_once_with("/api/v1/templates/render", {
            "channel": "sms",
            "message_type": "2fa_request",
            "variables": {"code": "123456"},
        })


@pytest.mark.asyncio
class TestProfiles:
    async def test_list_gets_profiles(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"profiles": []}
        p = Profiles(mock_http)

        await p.list()

        mock_http.get.assert_awaited_once_with("/api/v1/me/profiles")

    async def test_create_posts_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "prof_123"}
        p = Profiles(mock_http)

        await p.create(display_name="Test", is_public=True)

        mock_http.post.assert_awaited_once_with("/api/v1/me/profiles", {
            "display_name": "Test",
            "is_public": True,
        })

    async def test_create_omits_none_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "prof_123"}
        p = Profiles(mock_http)

        await p.create(display_name="Test")

        body = mock_http.post.call_args[0][1]
        assert "is_public" not in body
        assert "bio" not in body

    async def test_retrieve_gets_by_id(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "prof_123"}
        p = Profiles(mock_http)

        await p.retrieve("prof_123")

        mock_http.get.assert_awaited_once_with("/api/v1/me/profiles/prof_123")

    async def test_retrieve_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {}
        p = Profiles(mock_http)

        await p.retrieve("prof/special&id")

        mock_http.get.assert_awaited_once_with("/api/v1/me/profiles/prof%2Fspecial%26id")

    async def test_update_patches_params(self, mock_http: HttpClient) -> None:
        mock_http.patch.return_value = {"id": "prof_123"}
        p = Profiles(mock_http)

        await p.update("prof_123", display_name="Updated")

        mock_http.patch.assert_awaited_once_with("/api/v1/me/profiles/prof_123", {
            "display_name": "Updated",
        })

    async def test_update_omits_none_params(self, mock_http: HttpClient) -> None:
        mock_http.patch.return_value = {"id": "prof_123"}
        p = Profiles(mock_http)

        await p.update("prof_123", bio="Hello")

        body = mock_http.patch.call_args[0][1]
        assert "display_name" not in body
        assert body["bio"] == "Hello"

    async def test_update_avatar_url_none_clears(self, mock_http: HttpClient) -> None:
        mock_http.patch.return_value = {"id": "prof_123"}
        p = Profiles(mock_http)

        await p.update("prof_123", avatar_url=None)

        body = mock_http.patch.call_args[0][1]
        assert "avatar_url" in body
        assert body["avatar_url"] is None

    async def test_update_avatar_url_omitted_not_sent(self, mock_http: HttpClient) -> None:
        mock_http.patch.return_value = {"id": "prof_123"}
        p = Profiles(mock_http)

        await p.update("prof_123", bio="Hello")

        body = mock_http.patch.call_args[0][1]
        assert "avatar_url" not in body

    async def test_delete_deletes_by_id(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        p = Profiles(mock_http)

        await p.delete("prof_123")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/profiles/prof_123")

    async def test_set_primary_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        p = Profiles(mock_http)

        await p.set_primary("prof_123")

        mock_http.post.assert_awaited_once_with("/api/v1/me/profiles/prof_123/primary")


@pytest.mark.asyncio
class TestProjects:
    async def test_list_gets_projects(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"data": []}
        p = Projects(mock_http)

        await p.list()

        mock_http.get.assert_awaited_once_with("/api/v1/me/projects")

    async def test_create_posts_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "proj_123"}
        p = Projects(mock_http)

        await p.create(name="My Project")

        mock_http.post.assert_awaited_once_with("/api/v1/me/projects", {
            "name": "My Project",
        })

    async def test_create_includes_optional_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "proj_123"}
        p = Projects(mock_http)

        await p.create(name="Test", description="A test project", branding={"business_name": "Acme"})

        body = mock_http.post.call_args[0][1]
        assert body["description"] == "A test project"
        assert body["branding"] == {"business_name": "Acme"}

    async def test_create_omits_none_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "proj_123"}
        p = Projects(mock_http)

        await p.create(name="Test")

        body = mock_http.post.call_args[0][1]
        assert "description" not in body
        assert "branding" not in body

    async def test_retrieve_gets_by_id(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "proj_123"}
        p = Projects(mock_http)

        await p.retrieve("proj_123")

        mock_http.get.assert_awaited_once_with("/api/v1/me/projects/proj_123")

    async def test_retrieve_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {}
        p = Projects(mock_http)

        await p.retrieve("proj/special&id")

        mock_http.get.assert_awaited_once_with("/api/v1/me/projects/proj%2Fspecial%26id")

    async def test_update_puts_params(self, mock_http: HttpClient) -> None:
        mock_http.put.return_value = {"id": "proj_123"}
        p = Projects(mock_http)

        await p.update("proj_123", name="Updated")

        mock_http.put.assert_awaited_once_with("/api/v1/me/projects/proj_123", {
            "name": "Updated",
        })

    async def test_update_omits_none_params(self, mock_http: HttpClient) -> None:
        mock_http.put.return_value = {"id": "proj_123"}
        p = Projects(mock_http)

        await p.update("proj_123", description="New desc")

        body = mock_http.put.call_args[0][1]
        assert "name" not in body
        assert body["description"] == "New desc"

    async def test_delete_deletes_by_id(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        p = Projects(mock_http)

        await p.delete("proj_123")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/projects/proj_123")

    async def test_list_templates_gets(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"templates": []}
        p = Projects(mock_http)

        await p.list_templates("proj_123")

        mock_http.get.assert_awaited_once_with("/api/v1/me/projects/proj_123/templates")

    async def test_update_template_puts_compound_url(self, mock_http: HttpClient) -> None:
        mock_http.put.return_value = {"is_custom": True}
        p = Projects(mock_http)

        await p.update_template("proj_123", "email", "verification_request", body="Hello {{code}}")

        mock_http.put.assert_awaited_once_with(
            "/api/v1/me/projects/proj_123/templates/email/verification_request",
            {"body": "Hello {{code}}"},
        )

    async def test_delete_template_deletes_compound_url(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"is_custom": False}
        p = Projects(mock_http)

        await p.delete_template("proj_123", "sms", "2fa_request")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/projects/proj_123/templates/sms/2fa_request")

    async def test_preview_template_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"preview": {}}
        p = Projects(mock_http)

        await p.preview_template("proj_123", channel="email", message_type="verification_request", body="Test {{code}}")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/projects/proj_123/templates/preview",
            {"channel": "email", "message_type": "verification_request", "body": "Test {{code}}"},
        )

    async def test_update_template_encodes_all_segments(self, mock_http: HttpClient) -> None:
        mock_http.put.return_value = {}
        p = Projects(mock_http)

        await p.update_template("proj/id", "ch/an", "ty/pe", body="test")

        mock_http.put.assert_awaited_once_with(
            "/api/v1/me/projects/proj%2Fid/templates/ch%2Fan/ty%2Fpe",
            {"body": "test"},
        )


@pytest.mark.asyncio
class TestBilling:
    async def test_subscription_gets_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"plan": "free", "status": None}
        b = Billing(mock_http)

        await b.subscription()

        mock_http.get.assert_awaited_once_with("/api/v1/billing/subscription")

    async def test_checkout_posts_with_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"checkout_url": "https://checkout.stripe.com/..."}
        b = Billing(mock_http)

        await b.checkout(plan="pro", success_url="https://proof.holdings/success", cancel_url="https://proof.holdings/cancel")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/billing/checkout",
            {"plan": "pro", "success_url": "https://proof.holdings/success", "cancel_url": "https://proof.holdings/cancel"},
        )

    async def test_portal_posts_with_return_url(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"portal_url": "https://billing.stripe.com/..."}
        b = Billing(mock_http)

        await b.portal(return_url="https://proof.holdings/billing")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/billing/portal",
            {"return_url": "https://proof.holdings/billing"},
        )


@pytest.mark.asyncio
class TestPhones:
    async def test_list_gets_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"phones": []}
        p = Phones(mock_http)

        await p.list()

        mock_http.get.assert_awaited_once_with("/api/v1/me/phones")

    async def test_remove_deletes_by_id(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        p = Phones(mock_http)

        await p.remove("ph_123")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/phones/ph_123")

    async def test_remove_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        p = Phones(mock_http)

        await p.remove("ph/special&id")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/phones/ph%2Fspecial%26id")

    async def test_set_primary_puts(self, mock_http: HttpClient) -> None:
        mock_http.put.return_value = {"success": True}
        p = Phones(mock_http)

        await p.set_primary("ph_123")

        mock_http.put.assert_awaited_once_with("/api/v1/me/phones/ph_123/primary")

    async def test_start_add_posts_with_channel(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"session_id": "ses_123"}
        p = Phones(mock_http)

        await p.start_add(channel="telegram")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/phones/add", {"channel": "telegram"}
        )

    async def test_get_add_status_gets_by_session(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"status": "pending"}
        p = Phones(mock_http)

        await p.get_add_status("ses_123")

        mock_http.get.assert_awaited_once_with("/api/v1/me/phones/add/ses_123")


@pytest.mark.asyncio
class TestEmails:
    async def test_list_gets_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"emails": []}
        e = Emails(mock_http)

        await e.list()

        mock_http.get.assert_awaited_once_with("/api/v1/me/emails")

    async def test_remove_deletes_by_id(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        e = Emails(mock_http)

        await e.remove("em_123")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/emails/em_123")

    async def test_remove_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        e = Emails(mock_http)

        await e.remove("em/special&id")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/emails/em%2Fspecial%26id")

    async def test_set_primary_puts(self, mock_http: HttpClient) -> None:
        mock_http.put.return_value = {"success": True}
        e = Emails(mock_http)

        await e.set_primary("em_123")

        mock_http.put.assert_awaited_once_with("/api/v1/me/emails/em_123/primary")

    async def test_start_add_posts_with_email(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"session_id": "ses_456"}
        e = Emails(mock_http)

        await e.start_add(email="user@example.com")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/emails/add", {"email": "user@example.com"}
        )

    async def test_get_add_status_gets_by_session(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"status": "pending"}
        e = Emails(mock_http)

        await e.get_add_status("ses_456")

        mock_http.get.assert_awaited_once_with("/api/v1/me/emails/add/ses_456")

    async def test_verify_otp_posts_code(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"verified": True}
        e = Emails(mock_http)

        await e.verify_otp("ses_456", code="123456")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/emails/add/ses_456/verify", {"code": "123456"}
        )

    async def test_resend_otp_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        e = Emails(mock_http)

        await e.resend_otp("ses_456")

        mock_http.post.assert_awaited_once_with("/api/v1/me/emails/add/ses_456/resend")


@pytest.mark.asyncio
class TestAssets:
    async def test_list_gets_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"assets": []}
        a = Assets(mock_http)

        await a.list()

        mock_http.get.assert_awaited_once_with("/api/v1/me/assets", params={})

    async def test_list_passes_filters(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"assets": []}
        a = Assets(mock_http)

        await a.list(asset_type="phone", status="active")

        mock_http.get.assert_awaited_once_with(
            "/api/v1/me/assets", params={"type": "phone", "status": "active"}
        )

    async def test_get_gets_by_id(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "asset_123"}
        a = Assets(mock_http)

        await a.get("asset_123")

        mock_http.get.assert_awaited_once_with("/api/v1/me/assets/asset_123")

    async def test_revoke_deletes_by_id(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        a = Assets(mock_http)

        await a.revoke("asset_123")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/assets/asset_123")


@pytest.mark.asyncio
class TestAuth:
    async def test_get_me_gets_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "user_123", "email": "test@example.com"}
        a = Auth(mock_http)

        await a.get_me()

        mock_http.get.assert_awaited_once_with("/api/v1/auth/me")

    async def test_list_sessions_gets_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"sessions": []}
        a = Auth(mock_http)

        await a.list_sessions()

        mock_http.get.assert_awaited_once_with("/api/v1/auth/sessions")

    async def test_revoke_session_deletes_by_id(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        a = Auth(mock_http)

        await a.revoke_session("sess_123")

        mock_http.delete.assert_awaited_once_with("/api/v1/auth/sessions/sess_123")

    async def test_revoke_session_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        a = Auth(mock_http)

        await a.revoke_session("sess/special&id")

        mock_http.delete.assert_awaited_once_with("/api/v1/auth/sessions/sess%2Fspecial%26id")


@pytest.mark.asyncio
class TestSettings:
    async def test_get_gets_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"branding": {}}
        s = Settings(mock_http)

        await s.get()

        mock_http.get.assert_awaited_once_with("/api/v1/me/settings")

    async def test_update_patches_with_params(self, mock_http: HttpClient) -> None:
        mock_http.patch.return_value = {"branding": {"business_name": "Acme"}}
        s = Settings(mock_http)

        await s.update(branding={"business_name": "Acme"})

        mock_http.patch.assert_awaited_once_with("/api/v1/me/settings", {"branding": {"business_name": "Acme"}})

    async def test_get_usage_gets_without_params(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"usage": []}
        s = Settings(mock_http)

        await s.get_usage()

        mock_http.get.assert_awaited_once_with("/api/v1/me/usage", params={})

    async def test_get_usage_gets_with_params(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"usage": []}
        s = Settings(mock_http)

        await s.get_usage(period="2026-02", months=3)

        mock_http.get.assert_awaited_once_with("/api/v1/me/usage", params={"period": "2026-02", "months": "3"})

    async def test_export_gets_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"data": {}}
        s = Settings(mock_http)

        await s.export()

        mock_http.get.assert_awaited_once_with("/api/v1/me/export")


@pytest.mark.asyncio
class TestApiKeys:
    async def test_list_gets_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"api_keys": []}
        ak = ApiKeys(mock_http)

        await ak.list()

        mock_http.get.assert_awaited_once_with("/api/v1/me/api-keys")

    async def test_create_posts_with_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "key_123", "secret": "pk_test_..."}
        ak = ApiKeys(mock_http)

        await ak.create(name="My Key", environment="test")

        mock_http.post.assert_awaited_once_with("/api/v1/me/api-keys", {"name": "My Key", "environment": "test"})

    async def test_create_posts_empty_body_when_no_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "key_123"}
        ak = ApiKeys(mock_http)

        await ak.create()

        mock_http.post.assert_awaited_once_with("/api/v1/me/api-keys", {})

    async def test_revoke_deletes_by_id(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        ak = ApiKeys(mock_http)

        await ak.revoke("key_123")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/api-keys/key_123")

    async def test_revoke_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        ak = ApiKeys(mock_http)

        await ak.revoke("key/special&id")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/api-keys/key%2Fspecial%26id")

    async def test_regenerate_posts_to_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "key_123", "secret": "pk_test_new..."}
        ak = ApiKeys(mock_http)

        await ak.regenerate("key_123")

        mock_http.post.assert_awaited_once_with("/api/v1/me/api-keys/key_123/regenerate")
