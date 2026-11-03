"""Billing resource: the subscription, Stripe checkout and portal links, and the prepaid balance.

Checkout, portal and top-up raise ``BillingUnavailableError`` (``503 billing_unavailable``) while
billing is not live; the reads keep answering. Their redirect URLs must be on ``proof.holdings`` (or
``localhost``): the API refuses any other host, so a flow that sends the payer back to your own site
cannot use them yet. The four writes are account-level, so a key bound to one sub-account is
refused ``403 account_key_required``.
"""

from __future__ import annotations

from typing import Any

from ..http import HttpClient
from ..types import (
    BalanceResponse,
    BillingPlan,
    CheckoutResponse,
    LedgerListResponse,
    PortalResponse,
    SubscriptionResponse,
    TopUpResponse,
)


class Billing:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def subscription(self) -> SubscriptionResponse:
        """The account's subscription, whatever its status; with none, the account's plan and ``status: None``."""
        return await self._http.get("/api/v1/billing/subscription")

    async def checkout(self, *, plan: BillingPlan, success_url: str, cancel_url: str) -> CheckoutResponse:
        """Open a Stripe Checkout session for a plan and return its ``checkout_url``.

        Refused ``409 subscription_exists`` while the account has a live subscription (change the
        plan in the portal instead), and ``409 company_details_required`` until the account's company
        profile is complete.

        Its redirect URLs must be on ``proof.holdings`` (or ``localhost``): the API refuses any other
        host. A key bound to one sub-account is refused ``403 account_key_required``.
        """
        return await self._http.post(
            "/api/v1/billing/checkout",
            {"plan": plan, "success_url": success_url, "cancel_url": cancel_url},
        )

    async def portal(self, *, return_url: str) -> PortalResponse:
        """Open a Stripe billing portal session and return its ``portal_url`` (``404 no_subscription`` without one).

        Its redirect URLs must be on ``proof.holdings`` (or ``localhost``): the API refuses any other
        host. A key bound to one sub-account is refused ``403 account_key_required``.
        """
        return await self._http.post("/api/v1/billing/portal", {"return_url": return_url})

    async def top_up(
        self,
        *,
        amount: int,
        success_url: str,
        cancel_url: str,
        auto_top_up: bool | None = None,
    ) -> TopUpResponse:
        """Open a Stripe Checkout session for a prepaid balance top-up and return its ``checkout_url``.

        ``amount`` is in euros: 10, 50 or 200. Nothing is credited here — the balance grows once
        Stripe reports the payment. ``auto_top_up=True`` is refused to an API key
        (``403 owner_session_required``): saving the card for automatic top-ups is the account owner's
        act on the dashboard.

        Its redirect URLs must be on ``proof.holdings`` (or ``localhost``): the API refuses any other
        host. A key bound to one sub-account is refused ``403 account_key_required``.
        """
        body: dict[str, Any] = {"amount": amount, "success_url": success_url, "cancel_url": cancel_url}
        if auto_top_up is not None:
            body["auto_top_up"] = auto_top_up
        return await self._http.post("/api/v1/billing/top-up", body)

    async def balance(self) -> BalanceResponse:
        """The prepaid balance, the low-balance threshold, the top-up amounts and the auto top-up setting."""
        return await self._http.get("/api/v1/billing/balance")

    async def balance_ledger(self, *, page: int | None = None, limit: int | None = None) -> LedgerListResponse:
        """The balance history, newest first: every top-up, refund and adjustment, and one usage row per month."""
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        return await self._http.get("/api/v1/billing/balance/ledger", params)

    async def auto_top_up(self, *, enabled: bool, amount: int | None = None) -> BalanceResponse:
        """Switch auto top-up off (``enabled=False``).

        An API key may not switch it on or change its amount (``403 owner_session_required``):
        automatic top-ups charge the saved card with no one present, so the account owner switches
        them on from the dashboard. A key bound to one sub-account is refused
        ``403 account_key_required``.
        """
        body: dict[str, Any] = {"enabled": enabled}
        if amount is not None:
            body["amount"] = amount
        return await self._http.request("PATCH", "/api/v1/billing/auto-top-up", json=body)
