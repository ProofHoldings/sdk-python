"""Streams resource — collects ``stream()`` methods for every SSE endpoint.

The 8 SSE endpoints span several backend resources, some of which do not
yet have full Python SDK resource classes. To keep the public surface
area narrow and discoverable we expose all stream methods here. Each
method returns an async generator that yields ``{"event", "id", "data"}``
events and falls back to contract-compliant polling when SSE is unavailable.
"""

from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator
from urllib.parse import quote

from ..http import HttpClient
from ..streaming import stream_endpoint

_VERIFICATION_TERMINAL = {"verified", "failed", "expired", "revoked"}
_CONFIRMATION_TERMINAL = {"approved", "denied", "expired", "cancelled"}
_AUTH_SESSION_TERMINAL = {"authenticated", "failed", "expired", "cancelled"}
_TWOFA_TERMINAL = {"verified", "failed", "expired", "cancelled"}
_PHONE_ADD_TERMINAL = {"verified", "failed", "expired", "cancelled"}
_EMAIL_ADD_TERMINAL = {"verified", "failed", "expired", "cancelled"}
_HITL_CHAT_TERMINAL = {"completed", "expired", "cancelled"}
_ASSET_TERMINAL = {"verified", "failed", "expired", "revoked"}
_ASSET_REQUEST_TERMINAL = {"cancelled", "expired"}


class Streams:
    """Convenience resource exposing every SSE stream on the API."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    # 1. /api/v1/verifications/:id/events
    def verification_events(
        self,
        id: str,
        *,
        cancel_event: asyncio.Event | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream events for a single verification."""
        encoded = quote(id, safe="")
        return stream_endpoint(
            self._http,
            f"/api/v1/verifications/{encoded}/events",
            cancel_event=cancel_event,
            poll_retrieve=lambda: self._http.get(f"/api/v1/verifications/{encoded}"),
            terminal_states=_VERIFICATION_TERMINAL,
        )

    # 2. /api/v1/confirmations/:id/events
    def confirmation_events(
        self,
        id: str,
        *,
        cancel_event: asyncio.Event | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream events for a single HITL confirmation."""
        encoded = quote(id, safe="")
        return stream_endpoint(
            self._http,
            f"/api/v1/confirmations/{encoded}/events",
            cancel_event=cancel_event,
            poll_retrieve=lambda: self._http.get(f"/api/v1/confirmations/{encoded}"),
            terminal_states=_CONFIRMATION_TERMINAL,
        )

    # 3. /api/v1/auth/sessions/:id/events
    def auth_session_events(
        self,
        id: str,
        *,
        cancel_event: asyncio.Event | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream events for an OAuth/magic-link auth session."""
        encoded = quote(id, safe="")
        return stream_endpoint(
            self._http,
            f"/api/v1/auth/sessions/{encoded}/events",
            cancel_event=cancel_event,
            poll_retrieve=lambda: self._http.get(f"/api/v1/auth/sessions/{encoded}"),
            terminal_states=_AUTH_SESSION_TERMINAL,
        )

    # 4. /api/v1/me/2fa/:sessionId/events
    def twofa_events(
        self,
        session_id: str,
        *,
        cancel_event: asyncio.Event | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream events for a 2FA verification session."""
        encoded = quote(session_id, safe="")
        return stream_endpoint(
            self._http,
            f"/api/v1/me/2fa/{encoded}/events",
            cancel_event=cancel_event,
            poll_retrieve=lambda: self._http.get(f"/api/v1/me/2fa/{encoded}"),
            terminal_states=_TWOFA_TERMINAL,
        )

    # 5. /api/v1/me/phones/add/:sessionId/events
    def phone_add_events(
        self,
        session_id: str,
        *,
        cancel_event: asyncio.Event | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream events for an add-phone verification session."""
        encoded = quote(session_id, safe="")
        return stream_endpoint(
            self._http,
            f"/api/v1/me/phones/add/{encoded}/events",
            cancel_event=cancel_event,
            poll_retrieve=lambda: self._http.get(f"/api/v1/me/phones/add/{encoded}"),
            terminal_states=_PHONE_ADD_TERMINAL,
        )

    # 6. /api/v1/me/emails/add/:sessionId/events
    def email_add_events(
        self,
        session_id: str,
        *,
        cancel_event: asyncio.Event | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream events for an add-email verification session."""
        encoded = quote(session_id, safe="")
        return stream_endpoint(
            self._http,
            f"/api/v1/me/emails/add/{encoded}/events",
            cancel_event=cancel_event,
            poll_retrieve=lambda: self._http.get(f"/api/v1/me/emails/add/{encoded}"),
            terminal_states=_EMAIL_ADD_TERMINAL,
        )

    # 7. /api/v1/hitl/chat-id-discovery/:token/events
    def hitl_chat_id_discovery_events(
        self,
        token: str,
        *,
        cancel_event: asyncio.Event | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream events for a Telegram chat-ID discovery flow."""
        encoded = quote(token, safe="")
        return stream_endpoint(
            self._http,
            f"/api/v1/hitl/chat-id-discovery/{encoded}/events",
            cancel_event=cancel_event,
            poll_retrieve=lambda: self._http.get(
                f"/api/v1/hitl/chat-id-discovery/{encoded}"
            ),
            terminal_states=_HITL_CHAT_TERMINAL,
        )

    # 8. /api/v1/verify/request/:id/assets/:assetIndex/events
    def verification_request_asset_events(
        self,
        id: str,
        asset_index: int,
        *,
        cancel_event: asyncio.Event | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream events for a specific asset within a verification request.

        Ends on the asset's outcome (``verified``, ``failed``, ``expired``,
        ``revoked``) or when its request is cancelled or expires. ``failed``
        ends this generator although the server keeps the stream open after
        it — a failed asset can be started again; open a new stream to follow
        the retry.
        """
        encoded_id = quote(id, safe="")
        idx = int(asset_index)
        return stream_endpoint(
            self._http,
            f"/api/v1/verify/request/{encoded_id}/assets/{idx}/events",
            cancel_event=cancel_event,
            poll_retrieve=lambda: self._http.get(
                f"/api/v1/verify/request/{encoded_id}/assets/{idx}/status"
            ),
            terminal_states=_ASSET_TERMINAL,
            request_terminal_states=_ASSET_REQUEST_TERMINAL,
        )
