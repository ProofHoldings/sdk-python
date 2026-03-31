"""Billing resource."""

from __future__ import annotations

from typing import Any

from ..http import HttpClient
from ..types import CheckoutResponse, PortalResponse


class Billing:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def subscription(self) -> dict[str, Any]:
        """Get current subscription details."""
        return await self._http.get("/api/v1/billing/subscription")

    async def checkout(
        self,
        *,
        plan: str,
        success_url: str,
        cancel_url: str,
    ) -> CheckoutResponse:
        """Create a Stripe checkout session for plan upgrade."""
        return await self._http.post("/api/v1/billing/checkout", {
            "plan": plan,
            "success_url": success_url,
            "cancel_url": cancel_url,
        })

    async def portal(self, *, return_url: str) -> PortalResponse:
        """Create a Stripe customer portal session."""
        return await self._http.post("/api/v1/billing/portal", {
            "return_url": return_url,
        })
