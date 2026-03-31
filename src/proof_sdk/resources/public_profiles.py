"""Public profiles resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import PublicProfile, SuccessResponse


class PublicProfiles:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    # --- Public endpoints ---

    async def get_by_id(self, profile_id: str) -> PublicProfile:
        """Get public profile by profile ID."""
        pid = quote(profile_id, safe='')
        return await self._http.get(f"/api/v1/profiles/p/{pid}")

    async def get_avatar(self, profile_id: str) -> dict[str, Any]:
        """Get profile avatar image."""
        pid = quote(profile_id, safe='')
        return await self._http.get(f"/api/v1/profiles/p/{pid}/avatar")

    async def get_by_username(self, username: str) -> PublicProfile:
        """Get public profile by username."""
        uname = quote(username, safe='')
        return await self._http.get(f"/api/v1/profiles/u/{uname}")

    async def check_username(self, username: str) -> dict[str, Any]:
        """Check username availability."""
        uname = quote(username, safe='')
        return await self._http.get(f"/api/v1/profiles/check-username/{uname}")

    # --- Multi-profile endpoints ---

    async def list_profiles(self) -> list[PublicProfile]:
        """List all profiles."""
        return await self._http.get("/api/v1/profiles/profiles")

    async def create_profile(self, **kwargs: Any) -> PublicProfile:
        """Create a new profile."""
        return await self._http.post("/api/v1/profiles/profiles", kwargs)

    async def get_profile(self, profile_id: str) -> PublicProfile:
        """Get a specific profile by ID."""
        pid = quote(profile_id, safe='')
        return await self._http.get(f"/api/v1/profiles/profiles/{pid}")

    async def update_profile(self, profile_id: str, **kwargs: Any) -> PublicProfile:
        """Update a specific profile."""
        pid = quote(profile_id, safe='')
        return await self._http.patch(f"/api/v1/profiles/profiles/{pid}", kwargs)

    async def delete_profile(self, profile_id: str) -> SuccessResponse:
        """Delete a profile."""
        pid = quote(profile_id, safe='')
        return await self._http.delete(f"/api/v1/profiles/profiles/{pid}")

    async def set_primary(self, profile_id: str) -> PublicProfile:
        """Set a profile as primary."""
        pid = quote(profile_id, safe='')
        return await self._http.post(f"/api/v1/profiles/profiles/{pid}/primary")

    async def update_profile_proofs(self, profile_id: str, **kwargs: Any) -> PublicProfile:
        """Update proofs for a specific profile."""
        pid = quote(profile_id, safe='')
        return await self._http.put(f"/api/v1/profiles/profiles/{pid}/proofs", kwargs)

    # --- Legacy /me endpoints ---

    async def get_my_profile(self) -> PublicProfile:
        """Get current user's primary profile."""
        return await self._http.get("/api/v1/profiles/me")

    async def update_my_profile(self, **kwargs: Any) -> PublicProfile:
        """Update current user's profile."""
        return await self._http.put("/api/v1/profiles/me", kwargs)

    async def claim_username(self, **kwargs: Any) -> PublicProfile:
        """Claim a username."""
        return await self._http.post("/api/v1/profiles/me/username", kwargs)

    async def get_available_assets(self) -> dict[str, Any]:
        """Get available assets for public profile."""
        return await self._http.get("/api/v1/profiles/me/assets")

    async def update_public_proofs(self, **kwargs: Any) -> PublicProfile:
        """Update public proofs."""
        return await self._http.put("/api/v1/profiles/me/proofs", kwargs)
