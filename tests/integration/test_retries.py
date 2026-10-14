"""Retry logic: 5xx retry once then succeed."""

from __future__ import annotations

import httpx
import pytest

from .conftest import is_live_mode


async def test_retries_once_on_503_then_succeeds(make_client):
    if is_live_mode():
        pytest.skip("mock-only — exercises HttpClient retry path")

    attempts = {"n": 0}

    def handler(_req: httpx.Request) -> httpx.Response:
        attempts["n"] += 1
        if attempts["n"] == 1:
            return httpx.Response(503, json={"error": {"code": "service_unavailable", "message": "retry"}})
        return httpx.Response(200, json={
            "data": [],
            "pagination": {"page": 1, "limit": 20, "total": 0, "pages": 0},
        })

    proof = await make_client(handler, max_retries=1)
    page = await proof.verifications.list()
    assert page["data"] == []
    assert attempts["n"] == 2
