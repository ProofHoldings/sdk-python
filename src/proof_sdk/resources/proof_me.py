"""Proof-Me resource (cross-channel identity challenges)."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ..http import HttpClient
from ..types import IdentityChallengeResponse


class ProofMe:
    """Proof-Me reverse verification.

    An enrolled Circle member triggers a cross-channel CONFIRM (identity challenge)
    so the account holder approves on a channel different from the one the
    suspicious contact reached them on. Enrollment of trusted contacts lives on the
    Circle people-primitive — see the ``circles`` resource for member management and
    on-demand drills (``trigger_drill``).
    """

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def create_identity_challenge(
        self,
        *,
        circle_id: str,
        member_id: str,
        suspicious_channel: str | None = None,
    ) -> IdentityChallengeResponse:
        """Create a cross-channel identity challenge (CONFIRM)."""
        body: dict[str, Any] = {"circle_id": circle_id, "member_id": member_id}
        if suspicious_channel is not None:
            body["suspicious_channel"] = suspicious_channel
        return await self._http.post("/api/v1/identity-challenges", body)

    async def get_identity_challenge(self, id: str) -> IdentityChallengeResponse:
        """Get an identity challenge by ID (poll for resolution)."""
        return await self._http.get(f"/api/v1/identity-challenges/{quote(id, safe='')}")
