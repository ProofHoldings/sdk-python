"""Webhook deliveries resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import RetryDeliveryResponse, WebhookDelivery, WebhookDeliveryListResponse, WebhookDeliveryStats


class WebhookDeliveries:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def stats(self) -> WebhookDeliveryStats:
        """Get webhook delivery statistics (totals, rates, recent failures)."""
        return await self._http.get("/api/v1/webhook-deliveries/stats")

    async def list(
        self,
        *,
        status: str | None = None,
        event_type: str | None = None,
        verification_request_id: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> WebhookDeliveryListResponse:
        """List webhook deliveries with optional filters."""
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if event_type is not None:
            params["event_type"] = event_type
        if verification_request_id is not None:
            params["verification_request_id"] = verification_request_id
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page
        return await self._http.get("/api/v1/webhook-deliveries", params)

    async def retrieve(self, id: str) -> WebhookDelivery:
        """Get a webhook delivery by ID."""
        return await self._http.get(f"/api/v1/webhook-deliveries/{quote(id, safe="")}")

    async def retry(self, id: str) -> RetryDeliveryResponse:
        """Retry a failed webhook delivery."""
        return await self._http.post(f"/api/v1/webhook-deliveries/{quote(id, safe="")}/retry")
