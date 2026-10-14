"""Public profiles resource (unauthenticated reads under /api/v1/profiles)."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient


class PublicProfiles:
    """Public profile reads — unauthenticated endpoints; the client's
    Authorization header is sent but ignored by the server."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def get_by_id(self, profile_id: str) -> dict[str, Any]:
        """Get a public profile by its PUBLIC ``profile_id``.

        ``profile_id`` is the ``profile_id`` field on ``/me/profiles``
        responses — the internal ``id`` is NOT accepted here and will 404.
        """
        return await self._http.get(f"/api/v1/profiles/p/{quote(profile_id, safe='')}")

    async def get_avatar(self, profile_id: str) -> dict[str, Any]:
        """Get a profile's avatar image.

        Accepts either the public ``profile_id`` or the internal ``id``.
        Returns ``{"data": bytes, "content_type": str}``; https-hosted
        avatars are followed through the server's 301 redirect.
        """
        return await self._http.get(f"/api/v1/profiles/p/{quote(profile_id, safe='')}/avatar")

    async def get_by_username(self, username: str) -> dict[str, Any]:
        """Get a public profile by username."""
        return await self._http.get(f"/api/v1/profiles/u/{quote(username, safe='')}")

    async def get_badge(self, username: str) -> dict[str, Any]:
        """Get the embeddable badge descriptor for a username.

        Everything needed to embed the verification badge in one call: the
        subject it asserts, the live verified count, the badge image URL for
        each style, and ready-to-paste snippets. A username with no public
        record answers 200 with ``state: "no_public_record"`` rather than a
        404, so a caller never has to treat "nothing to show" as an error.
        """
        return await self._http.get(f"/api/v1/profiles/badge/{quote(username, safe='')}")

    async def check_username(self, username: str) -> dict[str, Any]:
        """Check username availability."""
        return await self._http.get(f"/api/v1/profiles/check-username/{quote(username, safe='')}")
