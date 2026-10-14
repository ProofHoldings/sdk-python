"""HITL config resource (CRUD, finalize/authorize, chat ID discovery)."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import (
    ChatIdDiscoveryResponse,
    Hitl as HitlConfig,
    HitlAuthorizationResponse,
    HitlFinalizeResponse,
    HitlListResponse,
)


class Hitl:
    """HITL config CRUD. Configs are created in ``pending`` status; upload an
    encryption keypair (see :class:`HitlKeys`) and call :meth:`finalize` to
    activate.
    """

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        name: str,
        channels: list[dict[str, Any]],
        timeout_seconds: int | None = None,
        profile_id: str | None = None,
    ) -> HitlConfig:
        """Create a HITL configuration (starts in ``pending`` status)."""
        body: dict[str, Any] = {"name": name, "channels": channels}
        if timeout_seconds is not None:
            body["timeout_seconds"] = timeout_seconds
        if profile_id is not None:
            body["profile_id"] = profile_id
        return await self._http.post("/api/v1/hitl", body)

    async def list(
        self,
        *,
        status: str | None = None,
        environment: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> HitlListResponse:
        """List HITL configurations with optional filters."""
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if environment is not None:
            params["environment"] = environment
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page
        return await self._http.get("/api/v1/hitl", params)

    async def retrieve(self, id: str) -> HitlConfig:
        """Get a HITL configuration by ID."""
        return await self._http.get(f"/api/v1/hitl/{quote(id, safe='')}")

    async def update(
        self,
        id: str,
        *,
        name: str | None = None,
        channels: list[dict[str, Any]] | None = None,
        timeout_seconds: int | None = None,
    ) -> HitlConfig:
        """Update a HITL configuration's name, channels, or timeout."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if channels is not None:
            body["channels"] = channels
        if timeout_seconds is not None:
            body["timeout_seconds"] = timeout_seconds
        return await self._http.request("PATCH", f"/api/v1/hitl/{quote(id, safe='')}", json=body)

    async def archive(self, id: str) -> HitlConfig:
        """Archive a HITL configuration (soft delete; returns the archived config)."""
        return await self._http.delete(f"/api/v1/hitl/{quote(id, safe='')}")

    async def finalize(self, id: str) -> HitlFinalizeResponse:
        """Finalize a pending HITL configuration (``pending`` → ``active``).

        Requires an uploaded encryption keypair; dispatches authorization
        consent messages to configured channels.
        """
        return await self._http.post(f"/api/v1/hitl/{quote(id, safe='')}/finalize")

    async def request_authorization(self, id: str) -> HitlAuthorizationResponse:
        """Request authorization consent for channels in an active HITL config
        that don't have one yet.
        """
        return await self._http.post(f"/api/v1/hitl/{quote(id, safe='')}/authorize")

    async def get_approver_keys(self, id: str) -> dict[str, Any]:
        """List enrolled approver public keys for a config.

        Feed these into :func:`proof_sdk.crypto.encrypt_message_v2` to wrap a
        confirmation message for every enrolled approver.
        """
        return await self._http.get(f"/api/v1/hitl/{quote(id, safe='')}/approver-keys")

    async def create_chat_id_discovery(self) -> ChatIdDiscoveryResponse:
        """Create a chat-ID discovery token (Telegram deeplink + QR code)."""
        return await self._http.post("/api/v1/hitl/chat-id-discovery")
