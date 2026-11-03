"""Webhook endpoints resource (``/api/v1/webhook-endpoints``).

An account can register several webhook endpoints, each scoped to every sub-account (``all``) or
to a chosen set (``selected`` + ``profile_ids``). Each endpoint signs its deliveries with its own
secret. The secret is returned ONCE — in the response to ``create`` and to ``rotate_secret`` —
and never by ``list``, ``retrieve`` or ``update`` (those carry ``secret_set`` only), so store it
when you receive it.
"""

from __future__ import annotations

from typing import Any, Literal
from urllib.parse import quote

from ..http import HttpClient
from ..types import WebhookEndpoint, WebhookEndpointList, WebhookEndpointWithSecret

# Distinguishes "not passed" from an explicit ``description=None`` (which clears it).
_UNSET: Any = object()


class WebhookEndpoints:
    """Webhook endpoint CRUD plus signing-secret rotation."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self) -> WebhookEndpointList:
        """List the webhook endpoints the caller may see.

        A sub-account key sees only the endpoints scoped to exactly its own sub-account.
        Secrets are never included.
        """
        return await self._http.get("/api/v1/webhook-endpoints")

    async def create(
        self,
        *,
        url: str,
        scope: Literal["all", "selected"],
        profile_ids: list[str] | None = None,
        events: list[str] | None = None,
        status: Literal["active", "disabled"] | None = None,
        description: str | None = None,
    ) -> WebhookEndpointWithSecret:
        """Create a webhook endpoint.

        The response carries the endpoint's signing ``secret`` — returned only here and by
        ``rotate_secret``, so store it now. A sub-account key may create only an endpoint
        scoped ``selected`` to exactly its own sub-account.
        """
        body: dict[str, Any] = {"url": url, "scope": scope}
        if profile_ids is not None:
            body["profile_ids"] = profile_ids
        if events is not None:
            body["events"] = events
        if status is not None:
            body["status"] = status
        if description is not None:
            body["description"] = description
        return await self._http.post("/api/v1/webhook-endpoints", body)

    async def retrieve(self, id: str) -> WebhookEndpoint:
        """Get a webhook endpoint by ID (without its secret)."""
        return await self._http.get(f"/api/v1/webhook-endpoints/{quote(id, safe='')}")

    async def update(
        self,
        id: str,
        *,
        url: str | None = None,
        scope: Literal["all", "selected"] | None = None,
        profile_ids: list[str] | None = None,
        events: list[str] | None = None,
        status: Literal["active", "disabled"] | None = None,
        description: str | None = _UNSET,
    ) -> WebhookEndpoint:
        """Update a webhook endpoint; only the fields passed are sent.

        Moving to ``scope="all"`` drops ``profile_ids``; ``profile_ids`` sent alone keeps a
        ``selected`` endpoint selected. ``description=None`` clears the description. A
        sub-account key can never widen an endpoint. The secret is not returned.
        """
        body: dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if scope is not None:
            body["scope"] = scope
        if profile_ids is not None:
            body["profile_ids"] = profile_ids
        if events is not None:
            body["events"] = events
        if status is not None:
            body["status"] = status
        if description is not _UNSET:
            body["description"] = description
        return await self._http.request("PATCH", f"/api/v1/webhook-endpoints/{quote(id, safe='')}", json=body)

    async def delete(self, id: str) -> None:
        """Delete a webhook endpoint (the server answers 204 with no body)."""
        await self._http.delete(f"/api/v1/webhook-endpoints/{quote(id, safe='')}")

    async def rotate_secret(self, id: str) -> WebhookEndpointWithSecret:
        """Replace an endpoint's signing secret.

        The response carries the new ``secret`` — returned only here and by ``create``. Deliveries
        already queued keep the secret they were signed with.
        """
        return await self._http.post(f"/api/v1/webhook-endpoints/{quote(id, safe='')}/rotate-secret")
