"""Settings resource."""

from __future__ import annotations

from typing import Any

from ..http import HttpClient


class Settings:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def get(self) -> dict[str, Any]:
        """Get user settings."""
        return await self._http.get("/api/v1/me/settings")

    async def update(self, **kwargs: Any) -> dict[str, Any]:
        """Update user settings.

        Args:
            branding: Branding settings object with business_name, logo_url,
                      primary_color, support_email, email_theme.
        """
        return await self._http.patch("/api/v1/me/settings", kwargs)

    async def get_usage(
        self,
        *,
        period: str | None = None,
        months: int | None = None,
    ) -> dict[str, Any]:
        """Get usage metrics.

        Args:
            period: Period in YYYY-MM format.
            months: Number of months (1-12).
        """
        params: dict[str, str] = {}
        if period is not None:
            params["period"] = period
        if months is not None:
            params["months"] = str(months)
        return await self._http.get("/api/v1/me/usage", params=params)

    async def export(self) -> dict[str, Any]:
        """Export user data (GDPR)."""
        return await self._http.get("/api/v1/me/export")
