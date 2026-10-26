"""Message templates resource (custom notification templates).

Templates exist per project (sub-account) only. Every method but ``get_defaults`` takes an
optional keyword ``profile_id`` naming the project, sent as the ``profile_id`` query parameter.
Omitted, a project-bound API key uses its own project and any other caller the primary project;
a project-bound key naming a different project is refused (403 ``profile_mismatch``).
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import MessageType, TemplateChannel, TemplateContent


def _project_params(profile_id: str | None) -> dict[str, str] | None:
    """The ``profile_id`` query naming the project, or None when the caller named none."""
    return None if profile_id is None else {"profile_id": profile_id}


class Templates:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self, *, profile_id: str | None = None) -> dict[str, Any]:
        """List the project's custom templates plus available channels, message types, and variables."""
        return await self._http.get("/api/v1/templates", params=_project_params(profile_id))

    async def get_defaults(self) -> dict[str, Any]:
        """Get all default templates (for reference)."""
        return await self._http.get("/api/v1/templates/defaults")

    async def retrieve(
        self,
        channel: TemplateChannel,
        message_type: MessageType,
        *,
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        """Get a specific template (the project's own if set, default otherwise)."""
        return await self._http.get(
            f"/api/v1/templates/{quote(channel, safe='')}/{quote(message_type, safe='')}",
            params=_project_params(profile_id),
        )

    async def upsert(
        self,
        channel: TemplateChannel,
        message_type: MessageType,
        content: TemplateContent,
        *,
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        """Create or update the project's custom template."""
        return await self._http.put(
            f"/api/v1/templates/{quote(channel, safe='')}/{quote(message_type, safe='')}",
            dict(content),
            params=_project_params(profile_id),
        )

    async def delete(
        self,
        channel: TemplateChannel,
        message_type: MessageType,
        *,
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        """Delete the project's custom template (resets to default; 404 if no custom template exists)."""
        return await self._http.delete(
            f"/api/v1/templates/{quote(channel, safe='')}/{quote(message_type, safe='')}",
            params=_project_params(profile_id),
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
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        """Preview a template with sample data and the project's branding."""
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
        return await self._http.post("/api/v1/templates/preview", payload, params=_project_params(profile_id))

    async def render(
        self,
        *,
        channel: TemplateChannel,
        message_type: MessageType,
        variables: dict[str, str] | None = None,
        profile_id: str | None = None,
    ) -> dict[str, Any]:
        """Render the project's template with provided variables (for testing)."""
        payload: dict[str, Any] = {"channel": channel, "message_type": message_type}
        if variables is not None:
            payload["variables"] = variables
        return await self._http.post("/api/v1/templates/render", payload, params=_project_params(profile_id))
