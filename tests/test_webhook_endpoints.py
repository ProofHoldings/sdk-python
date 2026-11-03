"""Tests for the webhook_endpoints resource (verb, path and body per method)."""

from __future__ import annotations

from typing import Any

import pytest

from proof_sdk import Proof
from proof_sdk.resources.webhook_endpoints import WebhookEndpoints


def test_client_wires_webhook_endpoints() -> None:
    client = Proof("pk_test_123")
    assert isinstance(client.webhook_endpoints, WebhookEndpoints)


@pytest.mark.asyncio
class TestWebhookEndpoints:
    async def test_list_gets_collection_without_params(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"data": []}
        w = WebhookEndpoints(mock_http)

        result = await w.list()

        mock_http.get.assert_awaited_once_with("/api/v1/webhook-endpoints")
        assert result == {"data": []}

    async def test_create_posts_required_fields_only(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "we_1", "secret": "whsec_x"}
        w = WebhookEndpoints(mock_http)

        result = await w.create(url="https://example.com/hook", scope="all")

        mock_http.post.assert_awaited_once_with(
            "/api/v1/webhook-endpoints",
            {"url": "https://example.com/hook", "scope": "all"},
        )
        assert result["secret"] == "whsec_x"

    async def test_create_posts_every_given_field(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "we_1", "secret": "whsec_x"}
        w = WebhookEndpoints(mock_http)

        await w.create(
            url="https://example.com/hook",
            scope="selected",
            profile_ids=["pr_1"],
            events=["proof.revoked"],
            status="disabled",
            description="Billing",
        )

        mock_http.post.assert_awaited_once_with(
            "/api/v1/webhook-endpoints",
            {
                "url": "https://example.com/hook",
                "scope": "selected",
                "profile_ids": ["pr_1"],
                "events": ["proof.revoked"],
                "status": "disabled",
                "description": "Billing",
            },
        )

    async def test_retrieve_encodes_id(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"id": "we_1"}
        w = WebhookEndpoints(mock_http)

        await w.retrieve("we/1&x")

        mock_http.get.assert_awaited_once_with("/api/v1/webhook-endpoints/we%2F1%26x")

    async def test_update_patches_only_given_fields(self, mock_http: Any) -> None:
        mock_http.request.return_value = {"id": "we_1"}
        w = WebhookEndpoints(mock_http)

        await w.update("we_1", status="disabled", events=["proof.revoked"])

        mock_http.request.assert_awaited_once_with(
            "PATCH",
            "/api/v1/webhook-endpoints/we_1",
            json={"events": ["proof.revoked"], "status": "disabled"},
        )

    async def test_update_sends_null_description_to_clear_it(self, mock_http: Any) -> None:
        mock_http.request.return_value = {"id": "we_1", "description": None}
        w = WebhookEndpoints(mock_http)

        await w.update("we_1", description=None)

        mock_http.request.assert_awaited_once_with(
            "PATCH", "/api/v1/webhook-endpoints/we_1", json={"description": None}
        )

    async def test_update_with_no_fields_sends_empty_body(self, mock_http: Any) -> None:
        mock_http.request.return_value = {"id": "we_1"}
        w = WebhookEndpoints(mock_http)

        await w.update("we_1")

        mock_http.request.assert_awaited_once_with("PATCH", "/api/v1/webhook-endpoints/we_1", json={})

    async def test_update_sends_url_scope_and_profile_ids(self, mock_http: Any) -> None:
        mock_http.request.return_value = {"id": "we_1"}
        w = WebhookEndpoints(mock_http)

        await w.update("we_1", url="https://example.com/new", scope="selected", profile_ids=["pr_2"])

        mock_http.request.assert_awaited_once_with(
            "PATCH",
            "/api/v1/webhook-endpoints/we_1",
            json={"url": "https://example.com/new", "scope": "selected", "profile_ids": ["pr_2"]},
        )

    async def test_delete_deletes_and_returns_none(self, mock_http: Any) -> None:
        # The server answers 204 with no body; HttpClient turns that into {}.
        mock_http.delete.return_value = {}
        w = WebhookEndpoints(mock_http)

        result = await w.delete("we/1")

        mock_http.delete.assert_awaited_once_with("/api/v1/webhook-endpoints/we%2F1")
        assert result is None

    async def test_rotate_secret_posts_without_body(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"id": "we_1", "secret": "whsec_new"}
        w = WebhookEndpoints(mock_http)

        result = await w.rotate_secret("we_1")

        mock_http.post.assert_awaited_once_with("/api/v1/webhook-endpoints/we_1/rotate-secret")
        assert result["secret"] == "whsec_new"
