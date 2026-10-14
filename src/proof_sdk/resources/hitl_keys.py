"""HITL encryption key management resource."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient


class HitlKeys:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def get(self, hitl_id: str) -> dict[str, Any]:
        """Get encryption keypair for a HITL config."""
        return await self._http.get(f"/api/v1/hitl/{quote(hitl_id, safe='')}/keys")

    async def upload(self, hitl_id: str, *, public_key: str, encrypted_private_key: str, kdf_salt: str) -> dict[str, Any]:
        """Upload encryption keypair for a HITL config."""
        return await self._http.put(
            f"/api/v1/hitl/{quote(hitl_id, safe='')}/keys",
            {"public_key": public_key, "encrypted_private_key": encrypted_private_key, "kdf_salt": kdf_salt},
        )

    async def delete(self, hitl_id: str) -> dict[str, Any]:
        """Delete encryption keypair from a HITL config."""
        return await self._http.delete(f"/api/v1/hitl/{quote(hitl_id, safe='')}/keys")
