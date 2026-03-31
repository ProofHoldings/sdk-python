"""Projects resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import Project, SuccessResponse, Template


class Projects:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self) -> list[Project]:
        """List all projects for the authenticated user."""
        return await self._http.get("/api/v1/me/projects")

    async def create(
        self,
        *,
        name: str,
        description: str | None = None,
        branding: dict[str, Any] | None = None,
    ) -> Project:
        """Create a new project."""
        payload: dict[str, Any] = {"name": name}
        if description is not None:
            payload["description"] = description
        if branding is not None:
            payload["branding"] = branding
        return await self._http.post("/api/v1/me/projects", payload)

    async def retrieve(self, project_id: str) -> dict[str, Any]:
        """Get a specific project by ID."""
        pid = quote(project_id, safe="")
        return await self._http.get(f"/api/v1/me/projects/{pid}")

    async def update(
        self,
        project_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        branding: dict[str, Any] | None = None,
        callbacks: dict[str, Any] | None = None,
    ) -> Project:
        """Update a specific project."""
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if branding is not None:
            payload["branding"] = branding
        if callbacks is not None:
            payload["callbacks"] = callbacks
        pid = quote(project_id, safe="")
        return await self._http.put(f"/api/v1/me/projects/{pid}", payload)

    async def delete(self, project_id: str) -> SuccessResponse:
        """Delete a project (soft delete)."""
        pid = quote(project_id, safe="")
        return await self._http.delete(f"/api/v1/me/projects/{pid}")

    async def list_templates(self, project_id: str) -> list[Template]:
        """List all templates for a project."""
        pid = quote(project_id, safe="")
        return await self._http.get(f"/api/v1/me/projects/{pid}/templates")

    async def update_template(
        self,
        project_id: str,
        channel: str,
        message_type: str,
        *,
        body: str,
        subject: str | None = None,
        button_text: str | None = None,
        button_url_template: str | None = None,
        is_active: bool | None = None,
    ) -> Template:
        """Update (upsert) a project template by channel and message type."""
        payload: dict[str, Any] = {"body": body}
        if subject is not None:
            payload["subject"] = subject
        if button_text is not None:
            payload["button_text"] = button_text
        if button_url_template is not None:
            payload["button_url_template"] = button_url_template
        if is_active is not None:
            payload["is_active"] = is_active
        pid = quote(project_id, safe="")
        ch = quote(channel, safe="")
        mt = quote(message_type, safe="")
        return await self._http.put(f"/api/v1/me/projects/{pid}/templates/{ch}/{mt}", payload)

    async def delete_template(
        self,
        project_id: str,
        channel: str,
        message_type: str,
    ) -> SuccessResponse:
        """Delete a custom project template, reverting to the default."""
        pid = quote(project_id, safe="")
        ch = quote(channel, safe="")
        mt = quote(message_type, safe="")
        return await self._http.delete(f"/api/v1/me/projects/{pid}/templates/{ch}/{mt}")

    async def preview_template(
        self,
        project_id: str,
        *,
        channel: str,
        message_type: str,
        body: str,
        subject: str | None = None,
        button_text: str | None = None,
        button_url_template: str | None = None,
    ) -> dict[str, Any]:
        """Preview a project template with sample variables."""
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
        pid = quote(project_id, safe="")
        return await self._http.post(f"/api/v1/me/projects/{pid}/templates/preview", payload)
