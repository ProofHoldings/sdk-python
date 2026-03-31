"""Templates resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import SuccessResponse, Template


class Templates:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self) -> list[Template]:
        """List all custom templates for the authenticated tenant."""
        return await self._http.get("/api/v1/templates")

    async def get_defaults(self) -> list[Template]:
        """Get all default templates."""
        return await self._http.get("/api/v1/templates/defaults")

    async def retrieve(self, channel: str, message_type: str) -> Template:
        """Get a specific template (custom or default) by channel and message type."""
        ch = quote(channel, safe="")
        mt = quote(message_type, safe="")
        return await self._http.get(f"/api/v1/templates/{ch}/{mt}")

    async def upsert(
        self,
        channel: str,
        message_type: str,
        *,
        body: str,
        subject: str | None = None,
        button_text: str | None = None,
        button_url_template: str | None = None,
    ) -> Template:
        """Create or update a custom template."""
        payload: dict[str, Any] = {"body": body}
        if subject is not None:
            payload["subject"] = subject
        if button_text is not None:
            payload["button_text"] = button_text
        if button_url_template is not None:
            payload["button_url_template"] = button_url_template
        ch = quote(channel, safe="")
        mt = quote(message_type, safe="")
        return await self._http.put(f"/api/v1/templates/{ch}/{mt}", payload)

    async def delete(self, channel: str, message_type: str) -> SuccessResponse:
        """Delete a custom template (resets to default)."""
        ch = quote(channel, safe="")
        mt = quote(message_type, safe="")
        return await self._http.delete(f"/api/v1/templates/{ch}/{mt}")

    async def preview(
        self,
        *,
        channel: str,
        message_type: str,
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
        channel: str,
        message_type: str,
        variables: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Render a template with provided variables."""
        payload: dict[str, Any] = {
            "channel": channel,
            "message_type": message_type,
        }
        if variables is not None:
            payload["variables"] = variables
        return await self._http.post("/api/v1/templates/render", payload)
