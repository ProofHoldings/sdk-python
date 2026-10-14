"""Circle people-primitive resource (CRUD, members, member channels).

The Circle response DTOs are imported from the generated ``types.py`` (unified
2026-09; previously declared inline, duplicating the generated shapes field-for-
field). Member and channel responses expose reachability booleans (plus a
member's masked enrollment phone) only — an identifier is NEVER returned
(SEC-PM-006).
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import (
    Circle,
    CircleListResponse,
    CircleMember,
    CircleMemberChannel,
    CircleMemberChannelListResponse,
    CircleMemberDrillResponse,
    CircleMemberInviteResponse,
    CircleMemberListResponse,
)


class Circles:
    """Circle CRUD plus member and member-channel management."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        name: str,
        profile_id: str | None = None,
        proof_me_enabled: bool | None = None,
        members: list[dict[str, Any]] | None = None,
    ) -> Circle:
        """Create a Circle (optionally with initial members)."""
        body: dict[str, Any] = {"name": name}
        if profile_id is not None:
            body["profile_id"] = profile_id
        if proof_me_enabled is not None:
            body["proof_me_enabled"] = proof_me_enabled
        if members is not None:
            body["members"] = members
        return await self._http.post("/api/v1/circles", body)

    async def list(
        self,
        *,
        status: str | None = None,
        environment: str | None = None,
        profile_id: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> CircleListResponse:
        """List Circles (archived excluded by default)."""
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if environment is not None:
            params["environment"] = environment
        if profile_id is not None:
            params["profile_id"] = profile_id
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page
        return await self._http.get("/api/v1/circles", params)

    async def retrieve(self, id: str) -> Circle:
        """Get a Circle by ID."""
        return await self._http.get(f"/api/v1/circles/{quote(id, safe='')}")

    async def update(self, id: str, *, name: str | None = None) -> Circle:
        """Update a Circle's name (the profile binding is create-only)."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        return await self._http.request("PATCH", f"/api/v1/circles/{quote(id, safe='')}", json=body)

    async def archive(self, id: str) -> dict[str, Any]:
        """Archive a Circle (soft delete; returns an empty object)."""
        return await self._http.delete(f"/api/v1/circles/{quote(id, safe='')}")

    async def add_member(
        self,
        id: str,
        *,
        name: str,
        whatsapp_phone: str | None = None,
    ) -> CircleMember:
        """Add a pending member by name (+ an optional pre-declared WhatsApp phone)."""
        body: dict[str, Any] = {"name": name}
        if whatsapp_phone is not None:
            body["whatsapp_phone"] = whatsapp_phone
        return await self._http.post(f"/api/v1/circles/{quote(id, safe='')}/members", body)

    async def list_members(self, id: str) -> CircleMemberListResponse:
        """List a Circle's members (channel presence booleans and a masked enrollment phone only)."""
        return await self._http.get(f"/api/v1/circles/{quote(id, safe='')}/members")

    async def invite_member(self, id: str, member_id: str) -> CircleMemberInviteResponse:
        """Mint a single-use enrollment deep link (both channels + QR) for a member."""
        return await self._http.post(f"/api/v1/circles/{quote(id, safe='')}/members/invite", {"member_id": member_id})

    async def trigger_drill(self, id: str, member_id: str) -> CircleMemberDrillResponse:
        """Fire a cross-channel Proof-Me identity challenge against an enrolled member."""
        return await self._http.post(f"/api/v1/circles/{quote(id, safe='')}/members/{quote(member_id, safe='')}/drill")

    async def remove_member(self, id: str, member_id: str) -> dict[str, Any]:
        """Remove a member (deletes its channels and revokes its live authorizations)."""
        return await self._http.delete(f"/api/v1/circles/{quote(id, safe='')}/members/{quote(member_id, safe='')}")

    async def add_member_channel(
        self,
        id: str,
        member_id: str,
        *,
        channel: str,
        identifier: str,
    ) -> CircleMemberChannel:
        """Declare a channel for a member (409 if that channel type already exists)."""
        body: dict[str, Any] = {"channel": channel, "identifier": identifier}
        return await self._http.post(f"/api/v1/circles/{quote(id, safe='')}/members/{quote(member_id, safe='')}/channels", body)

    async def list_member_channels(self, id: str, member_id: str) -> CircleMemberChannelListResponse:
        """List a member's channels (metadata only, never an identifier)."""
        return await self._http.get(f"/api/v1/circles/{quote(id, safe='')}/members/{quote(member_id, safe='')}/channels")

    async def remove_member_channel(self, id: str, member_id: str, channel_id: str) -> dict[str, Any]:
        """Remove a member channel (removing the last channel is allowed)."""
        return await self._http.delete(f"/api/v1/circles/{quote(id, safe='')}/members/{quote(member_id, safe='')}/channels/{quote(channel_id, safe='')}")
