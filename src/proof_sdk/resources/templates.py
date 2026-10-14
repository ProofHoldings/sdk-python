"""Message templates resource (custom notification templates)."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import MessageType, TemplateChannel, TemplateContent


class Templates:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self) -> dict[str, Any]:
        """List custom templates plus available channels, message types, and variables."""
        return await self._http.get("/api/v1/templates")

    async def get_defaults(self) -> dict[str, Any]:
        """Get all default templates (for reference)."""
        return await self._http.get("/api/v1/templates/defaults")

    async def retrieve(self, channel: TemplateChannel, message_type: MessageType) -> dict[str, Any]:
        """Get a specific template (custom if set, default otherwise)."""
        return await self._http.get(
            f"/api/v1/templates/{quote(channel, safe='')}/{quote(message_type, safe='')}"
        )

    async def upsert(
        self,
        channel: TemplateChannel,
        message_type: MessageType,
        content: TemplateContent,
    ) -> dict[str, Any]:
        """Create or update a custom template."""
        return await self._http.put(
            f"/api/v1/templates/{quote(channel, safe='')}/{quote(message_type, safe='')}",
            dict(content),
        )

    async def delete(self, channel: TemplateChannel, message_type: MessageType) -> dict[str, Any]:
        """Delete a custom template (resets to default; 404 if no custom template exists)."""
        return await self._http.delete(
            f"/api/v1/templates/{quote(channel, safe='')}/{quote(message_type, safe='')}"
        )

    async def preview(
        self,
        *,
        channel: TemplateChannel,
        message_type: MessageType,
        body: str,
        subject: str | None = None,
        button_text: str | None = None,
        button_url_template: str | None = None,
    ) -> dict[str, Any]:
        """Preview a template with sample data."""
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
        return await self._http.post("/api/v1/templates/preview", payload)

    async def render(
        self,
        *,
        channel: TemplateChannel,
        message_type: MessageType,
        variables: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Render a template with provided variables (for testing)."""
        payload: dict[str, Any] = {"channel": channel, "message_type": message_type}
        if variables is not None:
            payload["variables"] = variables
        return await self._http.post("/api/v1/templates/render", payload)
