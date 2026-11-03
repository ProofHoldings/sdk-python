"""Unit tests for the Billing resource and the two billing refusals as typed errors."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from proof_sdk import Proof
from proof_sdk.errors import BalanceEmptyError, BillingUnavailableError, ProofError, ServerError
from proof_sdk.http import HttpClient
from proof_sdk.resources import Billing

FIXTURES = Path(__file__).resolve().parents[2] / "shared" / "fixtures"


def fixture(name: str) -> dict[str, Any]:
    """A shared fixture with its ``_``-prefixed metadata keys dropped."""
    raw = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return {key: value for key, value in raw.items() if not key.startswith("_")}


BALANCE = fixture("balance.json")
BALANCE_EMPTY = fixture("error_balance_empty.json")


def response(status_code: int, body: dict[str, Any]) -> httpx.Response:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = body
    resp.headers = {"content-type": "application/json"}
    return resp


async def send(responses: list[httpx.Response], max_retries: int = 2) -> tuple[Exception, int]:
    """Send one POST through a real HttpClient answering ``responses`` in turn; the raised error and the call count."""
    client = HttpClient(api_key="pk_test_123", base_url="https://api.example.com", timeout=5.0, max_retries=max_retries)
    with patch.object(client, "_get_client") as get_client:
        transport = AsyncMock()
        transport.request.side_effect = responses
        get_client.return_value = transport
        with patch("proof_sdk.http.asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(ProofError) as raised:
                await client.post("/api/v1/verifications", {})
    return raised.value, transport.request.await_count


def test_billing_is_wired_into_the_client() -> None:
    assert isinstance(Proof("pk_test_123").billing, Billing)


@pytest.mark.asyncio
class TestBilling:
    async def test_subscription(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"plan": "free", "status": None, "current_period_start": None, "current_period_end": None, "cancel_at_period_end": False}
        result = await Billing(mock_http).subscription()
        mock_http.get.assert_awaited_once_with("/api/v1/billing/subscription")
        assert result["status"] is None

    async def test_checkout(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"checkout_url": "https://checkout.stripe.com/c/pay/cs_test"}
        result = await Billing(mock_http).checkout(plan="pro", success_url="https://proof.holdings/billing?ok=1", cancel_url="https://proof.holdings/billing")
        mock_http.post.assert_awaited_once_with(
            "/api/v1/billing/checkout",
            {"plan": "pro", "success_url": "https://proof.holdings/billing?ok=1", "cancel_url": "https://proof.holdings/billing"},
        )
        assert result["checkout_url"] == "https://checkout.stripe.com/c/pay/cs_test"

    async def test_portal(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"portal_url": "https://billing.stripe.com/p/session/test"}
        result = await Billing(mock_http).portal(return_url="https://proof.holdings/billing")
        mock_http.post.assert_awaited_once_with("/api/v1/billing/portal", {"return_url": "https://proof.holdings/billing"})
        assert result["portal_url"] == "https://billing.stripe.com/p/session/test"

    async def test_top_up_sends_a_numeric_amount(self, mock_http: Any) -> None:
        mock_http.post.return_value = {"checkout_url": "https://checkout.stripe.com/c/pay/cs_top_up"}
        await Billing(mock_http).top_up(amount=50, success_url="https://proof.holdings/usage?top_up=success", cancel_url="https://proof.holdings/usage", auto_top_up=True)
        mock_http.post.assert_awaited_once_with(
            "/api/v1/billing/top-up",
            {"amount": 50, "success_url": "https://proof.holdings/usage?top_up=success", "cancel_url": "https://proof.holdings/usage", "auto_top_up": True},
        )

    async def test_top_up_omits_auto_top_up_when_not_given(self, mock_http: Any) -> None:
        mock_http.post.return_value = {}
        await Billing(mock_http).top_up(amount=10, success_url="https://proof.holdings/usage", cancel_url="https://proof.holdings/usage")
        assert "auto_top_up" not in mock_http.post.await_args.args[1]

    async def test_balance_reads_the_shared_fixture_shape(self, mock_http: Any) -> None:
        mock_http.get.return_value = BALANCE
        result = await Billing(mock_http).balance()
        mock_http.get.assert_awaited_once_with("/api/v1/billing/balance")
        assert result["balance"]["currency"] == "eur"
        assert result["auto_top_up"]["has_payment_method"] is True

    async def test_balance_ledger_sends_page_and_limit(self, mock_http: Any) -> None:
        mock_http.get.return_value = {"data": [], "pagination": {"page": 2, "limit": 10, "total": 0, "total_pages": 1}}
        billing = Billing(mock_http)
        await billing.balance_ledger(page=2, limit=10)
        mock_http.get.assert_awaited_with("/api/v1/billing/balance/ledger", {"page": 2, "limit": 10})
        await billing.balance_ledger()
        mock_http.get.assert_awaited_with("/api/v1/billing/balance/ledger", {})

    async def test_auto_top_up_patches(self, mock_http: Any) -> None:
        mock_http.request.return_value = BALANCE
        result = await Billing(mock_http).auto_top_up(enabled=True, amount=50)
        mock_http.request.assert_awaited_once_with("PATCH", "/api/v1/billing/auto-top-up", json={"enabled": True, "amount": 50})
        assert result["auto_top_up"]["amount"] == 50

    async def test_auto_top_up_off_sends_no_amount(self, mock_http: Any) -> None:
        mock_http.request.return_value = BALANCE
        await Billing(mock_http).auto_top_up(enabled=False)
        mock_http.request.assert_awaited_once_with("PATCH", "/api/v1/billing/auto-top-up", json={"enabled": False})


@pytest.mark.asyncio
class TestBillingRefusals:
    async def test_402_raises_balance_empty_error_with_the_four_fields(self) -> None:
        error, calls = await send([response(402, BALANCE_EMPTY)])
        sent = BALANCE_EMPTY["error"]
        assert isinstance(error, BalanceEmptyError)
        assert error.status_code == 402
        assert error.code == "balance_empty"
        assert error.top_up_url == sent["top_up_url"]
        assert error.used == sent["used"]
        assert error.included == sent["included"]
        assert error.balance == sent["balance"]
        assert error.request_id == sent["request_id"]
        assert calls == 1

    async def test_billing_unavailable_is_a_server_error_sent_once(self) -> None:
        error, calls = await send([response(503, {"error": {"code": "billing_unavailable", "message": "Billing is not configured"}})])
        assert isinstance(error, BillingUnavailableError)
        assert isinstance(error, ServerError)
        assert error.status_code == 503
        assert calls == 1

    async def test_any_other_503_keeps_the_retries(self) -> None:
        down = response(503, {"error": {"code": "service_unavailable", "message": "down"}})
        error, calls = await send([down, down, down])
        assert isinstance(error, ServerError)
        assert not isinstance(error, BillingUnavailableError)
        assert calls == 3
