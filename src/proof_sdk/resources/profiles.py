"""Profiles resource (multi-brand public profiles under /api/v1/me/profiles)."""

from __future__ import annotations

import warnings
from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import MessageType, TemplateChannel


def _warn_template_route_retired(replacement: str) -> None:
    warnings.warn(
        "The per-profile template routes (/api/v1/me/profiles/{id}/templates) are retired and answer "
        f"410 endpoint_retired. Use {replacement} instead.",
        DeprecationWarning,
        stacklevel=3,
    )


class Profiles:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self) -> dict[str, Any]:
        """List all profiles for the authenticated user."""
        return await self._http.get("/api/v1/me/profiles")

    async def create(self, **params: Any) -> dict[str, Any]:
        """Create a new profile.

        Accepts ``display_name``, ``bio``, ``avatar_url``, ``business_name``,
        ``is_business``, ``is_public``, ``is_primary``, ``theme``, ``email_theme``
        (``"dark"`` or ``"light"``), and ``support_email``.
        """
        return await self._http.post("/api/v1/me/profiles", params)

    async def retrieve(self, profile_id: str) -> dict[str, Any]:
        """Get a profile by ID."""
        return await self._http.get(f"/api/v1/me/profiles/{quote(profile_id, safe='')}")

    async def update(self, profile_id: str, **params: Any) -> dict[str, Any]:
        """Update a profile."""
        return await self._http.request("PATCH", f"/api/v1/me/profiles/{quote(profile_id, safe='')}", json=params)

    async def delete(self, profile_id: str) -> dict[str, Any]:
        """Delete a profile."""
        return await self._http.delete(f"/api/v1/me/profiles/{quote(profile_id, safe='')}")

    async def set_primary(self, profile_id: str) -> dict[str, Any]:
        """Set a profile as the primary profile."""
        return await self._http.post(f"/api/v1/me/profiles/{quote(profile_id, safe='')}/primary")

    async def list_templates(self, profile_id: str) -> dict[str, Any]:
        """List a profile's message templates (custom and default).

        Deprecated: the server retired this route (410 ``endpoint_retired``).
        Use ``templates.list(profile_id=...)``.
        """
        _warn_template_route_retired("templates.list(profile_id=...)")
        return await self._http.get(f"/api/v1/me/profiles/{quote(profile_id, safe='')}/templates")

    async def update_template(
        self,
        profile_id: str,
        channel: TemplateChannel,
        type: MessageType,
        content: dict[str, Any],
    ) -> dict[str, Any]:
        """Create or update a profile template for a channel/message type.

        Deprecated: the server retired this route (410 ``endpoint_retired``).
        Use ``templates.upsert(channel, message_type, content, profile_id=...)``.
        """
        _warn_template_route_retired("templates.upsert(channel, message_type, content, profile_id=...)")
        # NOTE: the path f-string must stay on ONE line — parsePySdkMethods
        # does not join adjacent string literals across lines.
        return await self._http.put(
            f"/api/v1/me/profiles/{quote(profile_id, safe='')}/templates/{quote(channel, safe='')}/{quote(type, safe='')}",
            content,
        )

    async def delete_template(
        self,
        profile_id: str,
        channel: TemplateChannel,
        type: MessageType,
    ) -> dict[str, Any]:
        """Delete a profile template (resets to default).

        Deprecated: the server retired this route (410 ``endpoint_retired``).
        Use ``templates.delete(channel, message_type, profile_id=...)``.
        """
        _warn_template_route_retired("templates.delete(channel, message_type, profile_id=...)")
        # NOTE: single-line path f-string — see update_template.
        return await self._http.delete(
            f"/api/v1/me/profiles/{quote(profile_id, safe='')}/templates/{quote(channel, safe='')}/{quote(type, safe='')}"
        )

    async def preview_template(
        self,
        profile_id: str,
        *,
        channel: TemplateChannel,
        message_type: MessageType,
        body: str,
        subject: str | None = None,
        button_text: str | None = None,
        button_url_template: str | None = None,
    ) -> dict[str, Any]:
        """Preview a profile template with the profile's branding.

        Deprecated: the server retired this route (410 ``endpoint_retired``).
        Use ``templates.preview(..., profile_id=...)``.
        """
        _warn_template_route_retired("templates.preview(..., profile_id=...)")
        payload: dict[str, Any] = {
            "channel": channel,
            "message_type": message_type,
            "body": body,
        }
        if subject is not None:
            payload["subject"] = subject
        if button_text is not None:
            payload["button_text"] = button_text
        if button_url_template is not None:
            payload["button_url_template"] = button_url_template
        return await self._http.post(
            f"/api/v1/me/profiles/{quote(profile_id, safe='')}/templates/preview",
            payload,
        )
