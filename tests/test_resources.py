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
from proof_sdk.resources.account import Account
from proof_sdk.resources.two_fa import TwoFA
from proof_sdk.resources.dns_credentials import DnsCredentials
from proof_sdk.resources.domains import Domains
from proof_sdk.resources.user_requests import UserRequests
from proof_sdk.resources.user_domain_verify import UserDomainVerify
from proof_sdk.resources.public_profiles import PublicProfiles
from proof_sdk.resources.authorizations import Authorizations
from proof_sdk.resources.confirmations import Confirmations as ConfirmationsResource
from proof_sdk.resources.hitl import HitlConfigs


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

    async def test_get_proofs_gets(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"proofs": [{"type": "phone", "identifier": "+37069199199", "proof_token": "jwt_proof"}]}
        vr = VerificationRequests(mock_http)

        result = await vr.get_proofs("vr_123")

        mock_http.get.assert_awaited_once_with("/api/v1/verification-requests/vr_123/proofs")
        assert len(result["proofs"]) == 1
        assert result["proofs"][0]["proof_token"] == "jwt_proof"


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


@pytest.mark.asyncio
class TestAccount:
    async def test_initiate_deletion_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"session_id": "sess_123"}
        a = Account(mock_http)

        await a.initiate_deletion()

        mock_http.post.assert_awaited_once_with("/api/v1/me/account/delete", {})

    async def test_deletion_status_gets_by_session(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"status": "pending"}
        a = Account(mock_http)

        await a.deletion_status("sess_123")

        mock_http.get.assert_awaited_once_with("/api/v1/me/account/delete/sess_123")

    async def test_deletion_status_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {}
        a = Account(mock_http)

        await a.deletion_status("sess/special&id")

        mock_http.get.assert_awaited_once_with("/api/v1/me/account/delete/sess%2Fspecial%26id")

    async def test_verify_deletion_posts_with_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        a = Account(mock_http)

        await a.verify_deletion("sess_123", code="123456")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/account/delete/sess_123/verify", {"code": "123456"}
        )

    async def test_verify_deletion_magic_link_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        a = Account(mock_http)

        await a.verify_deletion_magic_link("tok_abc")

        mock_http.post.assert_awaited_once_with("/api/v1/me/account/delete/magic/tok_abc")

    async def test_delete_sends_delete_with_body(self, mock_http: HttpClient) -> None:
        mock_http.request.return_value = {"success": True}
        a = Account(mock_http)

        await a.delete(session_id="sess_123")

        mock_http.request.assert_awaited_once_with(
            "DELETE", "/api/v1/me/account", json={"session_id": "sess_123"}
        )


@pytest.mark.asyncio
class TestTwoFA:
    async def test_start_posts_with_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"session_id": "sess_123"}
        t = TwoFA(mock_http)

        await t.start(action_type="api_key_view", channel="email")

        mock_http.post.assert_awaited_once_with("/api/v1/me/2fa/start", {"action_type": "api_key_view", "channel": "email"})

    async def test_get_status_gets_by_session(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"status": "pending"}
        t = TwoFA(mock_http)

        await t.get_status("sess_123")

        mock_http.get.assert_awaited_once_with("/api/v1/me/2fa/sess_123")

    async def test_get_status_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {}
        t = TwoFA(mock_http)

        await t.get_status("sess/special&id")

        mock_http.get.assert_awaited_once_with("/api/v1/me/2fa/sess%2Fspecial%26id")

    async def test_verify_posts_with_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        t = TwoFA(mock_http)

        await t.verify("sess_123", code="123456")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/2fa/sess_123/verify", {"code": "123456"}
        )

    async def test_verify_magic_link_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        t = TwoFA(mock_http)

        await t.verify_magic_link("tok_abc")

        mock_http.post.assert_awaited_once_with("/api/v1/me/2fa/magic/tok_abc")


@pytest.mark.asyncio
class TestDnsCredentials:
    async def test_list_gets_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"data": []}
        d = DnsCredentials(mock_http)

        await d.list()

        mock_http.get.assert_awaited_once_with("/api/v1/me/dns-credentials")

    async def test_create_posts_with_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "cred_123"}
        d = DnsCredentials(mock_http)

        await d.create(provider="cloudflare", credentials={"api_token": "tok_123"})

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/dns-credentials", {"provider": "cloudflare", "credentials": {"api_token": "tok_123"}}
        )

    async def test_delete_deletes_by_id(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        d = DnsCredentials(mock_http)

        await d.delete("cred_123")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/dns-credentials/cred_123")

    async def test_delete_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        d = DnsCredentials(mock_http)

        await d.delete("cred/special&id")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/dns-credentials/cred%2Fspecial%26id")


@pytest.mark.asyncio
class TestDomains:
    async def test_list_gets_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"data": []}
        d = Domains(mock_http)

        await d.list()

        mock_http.get.assert_awaited_once_with("/api/v1/me/domains")

    async def test_add_posts_with_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "dom_123"}
        d = Domains(mock_http)

        await d.add(domain="example.com", verification_method="auto_dns")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/domains", {"domain": "example.com", "verification_method": "auto_dns"}
        )

    async def test_get_gets_by_id(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "dom_123"}
        d = Domains(mock_http)

        await d.get("dom_123")

        mock_http.get.assert_awaited_once_with("/api/v1/me/domains/dom_123")

    async def test_get_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "dom/special&id"}
        d = Domains(mock_http)

        await d.get("dom/special&id")

        mock_http.get.assert_awaited_once_with("/api/v1/me/domains/dom%2Fspecial%26id")

    async def test_delete_deletes_by_id(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        d = Domains(mock_http)

        await d.delete("dom_123")

        mock_http.delete.assert_awaited_once_with("/api/v1/me/domains/dom_123")

    async def test_oauth_url_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"oauth_url": "https://example.com", "state": "abc"}
        d = Domains(mock_http)

        await d.oauth_url("dom_123")

        mock_http.post.assert_awaited_once_with("/api/v1/me/domains/dom_123/oauth-url")

    async def test_verify_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = Domains(mock_http)

        await d.verify("dom_123")

        mock_http.post.assert_awaited_once_with("/api/v1/me/domains/dom_123/verify")

    async def test_connect_cloudflare_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = Domains(mock_http)

        await d.connect_cloudflare("dom_123", api_token="tok_cf")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/domains/dom_123/connect/cloudflare", {"api_token": "tok_cf"}
        )

    async def test_connect_godaddy_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = Domains(mock_http)

        await d.connect_godaddy("dom_123", api_key="key", api_secret="secret")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/domains/dom_123/connect/godaddy", {"api_key": "key", "api_secret": "secret"}
        )

    async def test_connect_provider_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = Domains(mock_http)

        await d.connect_provider("dom_123", "namecheap", credentials={"api_key": "k"})

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/domains/dom_123/connect/namecheap", {"credentials": {"api_key": "k"}}
        )

    async def test_connect_provider_encodes_both_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = Domains(mock_http)

        await d.connect_provider("dom/id", "pro/vider", credentials={"k": "v"})

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/domains/dom%2Fid/connect/pro%2Fvider", {"credentials": {"k": "v"}}
        )

    async def test_add_provider_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = Domains(mock_http)

        await d.add_provider("dom_123", "route53", credentials={"access_key": "ak"})

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/domains/dom_123/add-provider/route53", {"credentials": {"access_key": "ak"}}
        )

    async def test_add_provider_encodes_both_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = Domains(mock_http)

        await d.add_provider("dom/id", "pro/vider", credentials={"k": "v"})

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/domains/dom%2Fid/add-provider/pro%2Fvider", {"credentials": {"k": "v"}}
        )

    async def test_get_providers_gets(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"cloudflare": {}}
        d = Domains(mock_http)

        await d.get_providers()

        mock_http.get.assert_awaited_once_with("/api/v1/me/dns-providers")

    async def test_verify_with_credentials_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = Domains(mock_http)

        await d.verify_with_credentials("dom_123")

        mock_http.post.assert_awaited_once_with("/api/v1/me/domains/dom_123/verify-with-credentials")

    async def test_check_credentials_gets(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"has_access": True}
        d = Domains(mock_http)

        await d.check_credentials("dom_123")

        mock_http.get.assert_awaited_once_with("/api/v1/me/domains/dom_123/check-credentials")

    async def test_start_email_verification_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = Domains(mock_http)

        await d.start_email_verification("dom_123", email_prefix="admin")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/domains/dom_123/verify-email", {"email_prefix": "admin"}
        )

    async def test_start_email_verification_no_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = Domains(mock_http)

        await d.start_email_verification("dom_123")

        mock_http.post.assert_awaited_once_with("/api/v1/me/domains/dom_123/verify-email", {})

    async def test_confirm_email_code_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = Domains(mock_http)

        await d.confirm_email_code("dom_123", code="123456")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/domains/dom_123/verify-email/confirm", {"code": "123456"}
        )

    async def test_resend_email_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = Domains(mock_http)

        await d.resend_email("dom_123", email_prefix="webmaster")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/domains/dom_123/verify-email/resend", {"email_prefix": "webmaster"}
        )

    async def test_email_setup_posts(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = Domains(mock_http)

        await d.email_setup("dom_123", from_email="noreply@example.com")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/me/domains/dom_123/email-setup", {"from_email": "noreply@example.com"}
        )

    async def test_email_setup_no_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = Domains(mock_http)

        await d.email_setup("dom_123")

        mock_http.post.assert_awaited_once_with("/api/v1/me/domains/dom_123/email-setup", {})

    async def test_email_status_gets(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"status": "active"}
        d = Domains(mock_http)

        await d.email_status("dom_123")

        mock_http.get.assert_awaited_once_with("/api/v1/me/domains/dom_123/email-status")


@pytest.mark.asyncio
class TestUserRequests:
    async def test_list(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"requests": []}
        r = UserRequests(mock_http)
        await r.list()
        mock_http.get.assert_awaited_once_with("/api/v1/me/verification-requests")

    async def test_list_incoming(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"requests": []}
        r = UserRequests(mock_http)
        await r.list_incoming()
        mock_http.get.assert_awaited_once_with("/api/v1/me/verification-requests/incoming")

    async def test_create(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "req_1"}
        r = UserRequests(mock_http)
        await r.create(type="phone")
        mock_http.post.assert_awaited_once_with("/api/v1/me/verification-requests", {"type": "phone"})

    async def test_claim(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        r = UserRequests(mock_http)
        await r.claim("req_1")
        mock_http.post.assert_awaited_once_with("/api/v1/me/verification-requests/req_1/claim")

    async def test_cancel(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        r = UserRequests(mock_http)
        await r.cancel("req_1")
        mock_http.delete.assert_awaited_once_with("/api/v1/me/verification-requests/req_1")

    async def test_extend(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        r = UserRequests(mock_http)
        await r.extend("req_1")
        mock_http.post.assert_awaited_once_with("/api/v1/me/verification-requests/req_1/extend")

    async def test_share_email(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        r = UserRequests(mock_http)
        await r.share_email("req_1")
        mock_http.post.assert_awaited_once_with("/api/v1/me/verification-requests/req_1/share-email")

    async def test_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        r = UserRequests(mock_http)
        await r.claim("req/special")
        mock_http.post.assert_awaited_once_with("/api/v1/me/verification-requests/req%2Fspecial/claim")


@pytest.mark.asyncio
class TestUserDomainVerify:
    async def test_start(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"sessionId": "sess_1"}
        d = UserDomainVerify(mock_http)
        await d.start(domain="example.com")
        mock_http.post.assert_awaited_once_with("/api/v1/me/verify/domain", {"domain": "example.com"})

    async def test_status(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"status": "pending"}
        d = UserDomainVerify(mock_http)
        await d.status("sess_1")
        mock_http.get.assert_awaited_once_with("/api/v1/me/verify/domain/sess_1")

    async def test_check(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        d = UserDomainVerify(mock_http)
        await d.check("sess_1")
        mock_http.post.assert_awaited_once_with("/api/v1/me/verify/domain/sess_1/check")

    async def test_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"status": "pending"}
        d = UserDomainVerify(mock_http)
        await d.status("sess/special")
        mock_http.get.assert_awaited_once_with("/api/v1/me/verify/domain/sess%2Fspecial")


@pytest.mark.asyncio
class TestPublicProfiles:
    async def test_get_by_id(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "prof_1"}
        p = PublicProfiles(mock_http)
        await p.get_by_id("prof_1")
        mock_http.get.assert_awaited_once_with("/api/v1/profiles/p/prof_1")

    async def test_get_avatar(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"url": "https://..."}
        p = PublicProfiles(mock_http)
        await p.get_avatar("prof_1")
        mock_http.get.assert_awaited_once_with("/api/v1/profiles/p/prof_1/avatar")

    async def test_get_by_username(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"username": "alice"}
        p = PublicProfiles(mock_http)
        await p.get_by_username("alice")
        mock_http.get.assert_awaited_once_with("/api/v1/profiles/u/alice")

    async def test_check_username(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"available": True}
        p = PublicProfiles(mock_http)
        await p.check_username("alice")
        mock_http.get.assert_awaited_once_with("/api/v1/profiles/check-username/alice")

    async def test_list_profiles(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"profiles": []}
        p = PublicProfiles(mock_http)
        await p.list_profiles()
        mock_http.get.assert_awaited_once_with("/api/v1/profiles/profiles")

    async def test_create_profile(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "prof_2"}
        p = PublicProfiles(mock_http)
        await p.create_profile(name="Test")
        mock_http.post.assert_awaited_once_with("/api/v1/profiles/profiles", {"name": "Test"})

    async def test_get_profile(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "prof_1"}
        p = PublicProfiles(mock_http)
        await p.get_profile("prof_1")
        mock_http.get.assert_awaited_once_with("/api/v1/profiles/profiles/prof_1")

    async def test_update_profile(self, mock_http: HttpClient) -> None:
        mock_http.patch.return_value = {"id": "prof_1"}
        p = PublicProfiles(mock_http)
        await p.update_profile("prof_1", name="Updated")
        mock_http.patch.assert_awaited_once_with("/api/v1/profiles/profiles/prof_1", {"name": "Updated"})

    async def test_delete_profile(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"success": True}
        p = PublicProfiles(mock_http)
        await p.delete_profile("prof_1")
        mock_http.delete.assert_awaited_once_with("/api/v1/profiles/profiles/prof_1")

    async def test_set_primary(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        p = PublicProfiles(mock_http)
        await p.set_primary("prof_1")
        mock_http.post.assert_awaited_once_with("/api/v1/profiles/profiles/prof_1/primary")

    async def test_update_profile_proofs(self, mock_http: HttpClient) -> None:
        mock_http.put.return_value = {"id": "prof_1"}
        p = PublicProfiles(mock_http)
        await p.update_profile_proofs("prof_1", proofs=["p_1"])
        mock_http.put.assert_awaited_once_with("/api/v1/profiles/profiles/prof_1/proofs", {"proofs": ["p_1"]})

    async def test_get_my_profile(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "prof_1"}
        p = PublicProfiles(mock_http)
        await p.get_my_profile()
        mock_http.get.assert_awaited_once_with("/api/v1/profiles/me")

    async def test_update_my_profile(self, mock_http: HttpClient) -> None:
        mock_http.put.return_value = {"id": "prof_1"}
        p = PublicProfiles(mock_http)
        await p.update_my_profile(bio="Hello")
        mock_http.put.assert_awaited_once_with("/api/v1/profiles/me", {"bio": "Hello"})

    async def test_claim_username(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"success": True}
        p = PublicProfiles(mock_http)
        await p.claim_username(username="alice")
        mock_http.post.assert_awaited_once_with("/api/v1/profiles/me/username", {"username": "alice"})

    async def test_get_available_assets(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"assets": []}
        p = PublicProfiles(mock_http)
        await p.get_available_assets()
        mock_http.get.assert_awaited_once_with("/api/v1/profiles/me/assets")

    async def test_update_public_proofs(self, mock_http: HttpClient) -> None:
        mock_http.put.return_value = {"success": True}
        p = PublicProfiles(mock_http)
        await p.update_public_proofs(proofs=["p_1"])
        mock_http.put.assert_awaited_once_with("/api/v1/profiles/me/proofs", {"proofs": ["p_1"]})

    async def test_encodes_profile_id(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "prof/special"}
        p = PublicProfiles(mock_http)
        await p.get_by_id("prof/special")
        mock_http.get.assert_awaited_once_with("/api/v1/profiles/p/prof%2Fspecial")

    async def test_encodes_username(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"available": True}
        p = PublicProfiles(mock_http)
        await p.check_username("user/special")
        mock_http.get.assert_awaited_once_with("/api/v1/profiles/check-username/user%2Fspecial")


@pytest.mark.asyncio
class TestAuthorizations:
    async def test_create_posts_to_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "auth_123", "status": "pending"}
        a = Authorizations(mock_http)
        await a.create(phone="+15551234567", channel="whatsapp", business_name="Acme Corp")
        mock_http.post.assert_awaited_once_with("/api/v1/authorizations", {
            "phone": "+15551234567",
            "channel": "whatsapp",
            "business_name": "Acme Corp",
        })

    async def test_create_includes_optional_params(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "auth_123"}
        a = Authorizations(mock_http)
        await a.create(
            phone="+15551234567",
            channel="sms",
            business_name="Acme",
            scope="confirmations",
            business_profile_id="507f1f77bcf86cd799439011",
            expires_in=86400,
        )
        body = mock_http.post.call_args[0][1]
        assert body["scope"] == "confirmations"
        assert body["business_profile_id"] == "507f1f77bcf86cd799439011"
        assert body["expires_in"] == 86400

    async def test_retrieve_gets_by_id(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "auth_123"}
        a = Authorizations(mock_http)
        await a.retrieve("auth_123")
        mock_http.get.assert_awaited_once_with("/api/v1/authorizations/auth_123")

    async def test_retrieve_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {}
        a = Authorizations(mock_http)
        await a.retrieve("auth/special&id")
        mock_http.get.assert_awaited_once_with("/api/v1/authorizations/auth%2Fspecial%26id")

    async def test_list_passes_filters(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"data": [], "pagination": {}}
        a = Authorizations(mock_http)
        await a.list(status="active", channel="whatsapp", limit=10)
        mock_http.get.assert_awaited_once_with("/api/v1/authorizations", {
            "status": "active",
            "channel": "whatsapp",
            "limit": 10,
        })

    async def test_list_without_filters(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"data": [], "pagination": {}}
        a = Authorizations(mock_http)
        await a.list()
        mock_http.get.assert_awaited_once_with("/api/v1/authorizations", {})

    async def test_revoke_sends_delete_with_reason(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"id": "auth_123", "status": "revoked"}
        a = Authorizations(mock_http)
        await a.revoke("auth_123", reason="No longer needed")
        mock_http.delete.assert_awaited_once_with(
            "/api/v1/authorizations/auth_123",
            {"reason": "No longer needed"},
        )

    async def test_revoke_sends_delete_without_reason(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = {"id": "auth_123", "status": "revoked"}
        a = Authorizations(mock_http)
        await a.revoke("auth_123")
        mock_http.delete.assert_awaited_once_with("/api/v1/authorizations/auth_123", None)

    async def test_export_passes_params(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"data": [], "total": 0}
        a = Authorizations(mock_http)
        await a.export(format="json", status="active")
        mock_http.get.assert_awaited_once_with("/api/v1/authorizations/export", {
            "format": "json",
            "status": "active",
        })

    async def test_export_without_params(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"data": [], "total": 0}
        a = Authorizations(mock_http)
        await a.export()
        mock_http.get.assert_awaited_once_with("/api/v1/authorizations/export", {})


# =============================================================================
# Confirmations
# =============================================================================

@pytest.mark.asyncio
class TestConfirmations:
    async def test_create_posts_to_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "conf_123", "status": "pending"}
        c = ConfirmationsResource(mock_http)
        await c.create(hitl_id="hitl_123", message="Deploy v2.3?")
        mock_http.post.assert_awaited_once_with("/api/v1/confirmations", {
            "hitl_id": "hitl_123",
            "message": "Deploy v2.3?",
        })

    async def test_retrieve_gets_by_id(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "conf_123", "status": "pending"}
        c = ConfirmationsResource(mock_http)
        await c.retrieve("conf_123")
        mock_http.get.assert_awaited_once_with("/api/v1/confirmations/conf_123")

    async def test_retrieve_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "conf/special&id"}
        c = ConfirmationsResource(mock_http)
        await c.retrieve("conf/special&id")
        mock_http.get.assert_awaited_once_with("/api/v1/confirmations/conf%2Fspecial%26id")

    async def test_list_passes_filters(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"data": [], "pagination": {}}
        c = ConfirmationsResource(mock_http)
        await c.list(status="pending", hitl_id="hitl_1", limit=10)
        mock_http.get.assert_awaited_once_with("/api/v1/confirmations", {
            "status": "pending",
            "hitl_id": "hitl_1",
            "limit": 10,
        })

    async def test_list_without_filters(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"data": [], "pagination": {}}
        c = ConfirmationsResource(mock_http)
        await c.list()
        mock_http.get.assert_awaited_once_with("/api/v1/confirmations", {})


# =============================================================================
# HitlConfigs
# =============================================================================

@pytest.mark.asyncio
class TestHitlConfigs:
    async def test_create_posts_to_endpoint(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "hitl_123", "name": "Ops HITL", "status": "active"}
        h = HitlConfigs(mock_http)
        await h.create(channels=[{"type": "telegram", "chat_id": "123456"}], name="Ops HITL")
        mock_http.post.assert_awaited_once_with("/api/v1/hitl", {
            "channels": [{"type": "telegram", "chat_id": "123456"}],
            "name": "Ops HITL",
        })

    async def test_create_includes_optional_timeout(self, mock_http: HttpClient) -> None:
        mock_http.post.return_value = {"id": "hitl_123"}
        h = HitlConfigs(mock_http)
        await h.create(
            channels=[{"type": "telegram", "chat_id": "123456"}],
            name="Ops HITL",
            timeout_seconds=3600,
        )
        body = mock_http.post.call_args[0][1]
        assert body["timeout_seconds"] == 3600

    async def test_retrieve_gets_by_id(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"id": "hitl_123", "name": "Ops HITL"}
        h = HitlConfigs(mock_http)
        await h.retrieve("hitl_123")
        mock_http.get.assert_awaited_once_with("/api/v1/hitl/hitl_123")

    async def test_retrieve_encodes_special_chars(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {}
        h = HitlConfigs(mock_http)
        await h.retrieve("hitl/special&id")
        mock_http.get.assert_awaited_once_with("/api/v1/hitl/hitl%2Fspecial%26id")

    async def test_list_passes_filters(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"data": [], "pagination": {}}
        h = HitlConfigs(mock_http)
        await h.list(status="active", limit=10, page=2)
        mock_http.get.assert_awaited_once_with("/api/v1/hitl", {
            "status": "active",
            "limit": 10,
            "page": 2,
        })

    async def test_list_without_filters(self, mock_http: HttpClient) -> None:
        mock_http.get.return_value = {"data": [], "pagination": {}}
        h = HitlConfigs(mock_http)
        await h.list()
        mock_http.get.assert_awaited_once_with("/api/v1/hitl", {})

    async def test_update_sends_patch(self, mock_http: HttpClient) -> None:
        mock_http.patch.return_value = {"id": "hitl_123", "name": "Updated HITL"}
        h = HitlConfigs(mock_http)
        await h.update("hitl_123", name="Updated HITL", timeout_seconds=7200)
        mock_http.patch.assert_awaited_once_with("/api/v1/hitl/hitl_123", {
            "name": "Updated HITL",
            "timeout_seconds": 7200,
        })

    async def test_update_sends_channels(self, mock_http: HttpClient) -> None:
        mock_http.patch.return_value = {"id": "hitl_123"}
        h = HitlConfigs(mock_http)
        await h.update("hitl_123", channels=[{"type": "telegram", "chat_id": "999"}])
        body = mock_http.patch.call_args[0][1]
        assert body["channels"] == [{"type": "telegram", "chat_id": "999"}]

    async def test_delete_sends_delete(self, mock_http: HttpClient) -> None:
        mock_http.delete.return_value = None
        h = HitlConfigs(mock_http)
        await h.delete("hitl_123")
        mock_http.delete.assert_awaited_once_with("/api/v1/hitl/hitl_123")
