"""Profiles resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import PublicProfile, SuccessResponse

_UNSET: Any = object()  # sentinel distinguishing "not provided" from None


class Profiles:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self) -> list[PublicProfile]:
        """List all profiles for the authenticated user."""
        return await self._http.get("/api/v1/me/profiles")

    async def create(
        self,
        *,
        display_name: str | None = None,
        bio: str | None = None,
        avatar_url: str | None = None,
        business_name: str | None = None,
        is_business: bool | None = None,
        is_public: bool | None = None,
        is_primary: bool | None = None,
        theme: dict[str, Any] | None = None,
    ) -> PublicProfile:
        """Create a new profile."""
        payload: dict[str, Any] = {}
        if display_name is not None:
            payload["display_name"] = display_name
        if bio is not None:
            payload["bio"] = bio
        if avatar_url is not None:
            payload["avatar_url"] = avatar_url
        if business_name is not None:
            payload["business_name"] = business_name
        if is_business is not None:
            payload["is_business"] = is_business
        if is_public is not None:
            payload["is_public"] = is_public
        if is_primary is not None:
            payload["is_primary"] = is_primary
        if theme is not None:
            payload["theme"] = theme
        return await self._http.post("/api/v1/me/profiles", payload)

    async def retrieve(self, profile_id: str) -> PublicProfile:
        """Get a specific profile by ID."""
        pid = quote(profile_id, safe="")
        return await self._http.get(f"/api/v1/me/profiles/{pid}")

    async def update(
        self,
        profile_id: str,
        *,
        display_name: str | None = None,
        bio: str | None = None,
        avatar_url: str | None = _UNSET,
        business_name: str | None = None,
        is_business: bool | None = None,
        is_public: bool | None = None,
        is_primary: bool | None = None,
        show_verification_dates: bool | None = None,
        show_proof_channels: bool | None = None,
        theme: dict[str, Any] | None = None,
        custom_links: list[dict[str, Any]] | None = None,
    ) -> PublicProfile:
        """Update a specific profile.

        Pass ``avatar_url=None`` to clear the avatar.  Omit the argument
        entirely to leave it unchanged.
        """
        payload: dict[str, Any] = {}
        if display_name is not None:
            payload["display_name"] = display_name
        if bio is not None:
            payload["bio"] = bio
        if avatar_url is not _UNSET:
            payload["avatar_url"] = avatar_url  # None clears the avatar
        if business_name is not None:
            payload["business_name"] = business_name
        if is_business is not None:
            payload["is_business"] = is_business
        if is_public is not None:
            payload["is_public"] = is_public
        if is_primary is not None:
            payload["is_primary"] = is_primary
        if show_verification_dates is not None:
            payload["show_verification_dates"] = show_verification_dates
        if show_proof_channels is not None:
            payload["show_proof_channels"] = show_proof_channels
        if theme is not None:
            payload["theme"] = theme
        if custom_links is not None:
            payload["custom_links"] = custom_links
        pid = quote(profile_id, safe="")
        return await self._http.patch(f"/api/v1/me/profiles/{pid}", payload)

    async def delete(self, profile_id: str) -> SuccessResponse:
        """Delete a profile."""
        pid = quote(profile_id, safe="")
        return await self._http.delete(f"/api/v1/me/profiles/{pid}")

    async def set_primary(self, profile_id: str) -> PublicProfile:
        """Set a profile as the primary profile."""
        pid = quote(profile_id, safe="")
        return await self._http.post(f"/api/v1/me/profiles/{pid}/primary")
