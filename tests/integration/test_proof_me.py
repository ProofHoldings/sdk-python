"""Proof-Me resource round-trip: identity challenge create + poll."""

from __future__ import annotations

import json

import httpx
import pytest

from .conftest import is_live_mode


_CIRCLE_ID = "0123456789abcdef01234567"
_MEMBER_ID = "fedcba9876543210fedcba98"
_CHALLENGE_ID = "aaaabbbbccccddddeeeeffff"

_CHALLENGE = {
    "id": _CHALLENGE_ID,
    "status": "pending",
    "confirm_channel": "whatsapp",
    "single_channel_warning": False,
    "created_at": "2026-06-23T00:00:00.000Z",
}


async def test_identity_challenge_round_trip(make_client):
    if is_live_mode():
        pytest.skip("live mode skips Proof-Me mutating flow")

    sent_body: dict[str, object] = {}

    def _handler(req: httpx.Request) -> httpx.Response:
        path = req.url.path
        if req.method == "POST" and path == "/api/v1/identity-challenges":
            sent_body.update(json.loads(req.content))
            return httpx.Response(201, json=_CHALLENGE)
        if req.method == "GET" and path == f"/api/v1/identity-challenges/{_CHALLENGE_ID}":
            return httpx.Response(200, json={**_CHALLENGE, "status": "active"})
        return httpx.Response(404, json={"error": {"code": "not_found", "message": "no handler"}})

    proof = await make_client(_handler)
    created = await proof.proof_me.create_identity_challenge(
        circle_id=_CIRCLE_ID, member_id=_MEMBER_ID
    )
    assert sent_body == {"circle_id": _CIRCLE_ID, "member_id": _MEMBER_ID}
    assert created["confirm_channel"] == "whatsapp"

    fetched = await proof.proof_me.get_identity_challenge(_CHALLENGE_ID)
    assert fetched["status"] == "active"
