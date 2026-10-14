"""Client construction and resource surface."""

from __future__ import annotations

import pytest

from proof_sdk import Proof
from .conftest import cf_access_headers, is_live_mode


async def test_client_exposes_every_resource(make_client):
    proof = await make_client()
    assert proof.verifications is not None
    assert proof.verification_requests is not None
    assert proof.proofs is not None
    assert proof.sessions is not None
    assert proof.streams is not None
    assert proof.webhook_deliveries is not None
    assert proof.authorizations is not None
    assert proof.confirmations is not None
    assert proof.hitl_keys is not None


def test_client_rejects_empty_api_key():
    with pytest.raises(ValueError, match="api_key is required"):
        Proof("")


def test_client_honors_custom_options():
    proof = Proof(
        "pk_test_xyz",
        base_url="https://example.test",
        timeout=1.0,
        max_retries=5,
    )
    assert proof._http.base_url == "https://example.test"


async def test_live_health_reachable():
    if not is_live_mode():
        pytest.skip("live mode not configured")
    import asyncio
    import os
    import httpx

    base = os.environ["PROOF_BASE_URL"].rstrip("/")
    # Cloudflare-fronted origins can transiently return 5xx (520 "origin
    # returned empty response" is the classic one when the edge ↔ origin
    # handshake jitters during a pod rotation or keepalive close). The
    # JS/PHP harnesses use the SDK's HTTP client which retries on 5xx;
    # this raw probe didn't, producing flaky Python-only failures. Retry
    # a small handful of times on 5xx before asserting, so a single
    # transient blip doesn't block the release pipeline.
    #
    # On staging the API subdomain (staging-api.proof.holdings) is NOT
    # behind Cloudflare Access — the Access perimeter was removed so the
    # frontend's XHR calls could reach the API. CF Access headers are
    # still sent when configured because production-branch pipelines may
    # point at an Access-gated origin, and extra headers are harmless on
    # non-Access origins.
    async with httpx.AsyncClient(
        headers={"User-Agent": "proof-sdk-integration-tests/1.0", **cf_access_headers()},
        timeout=15.0,
        http2=False,  # staging origin has occasionally mishandled HTTP/2 keep-alive
    ) as c:
        # range(1, 4) always runs at least once, so attempts / last_status /
        # last_body are guaranteed to be bound before the AssertionError reads them.
        for attempts in range(1, 4):
            r = await c.get(f"{base}/health")
            last_status = r.status_code
            last_body = r.text[:200]
            if r.status_code == 200:
                return
            if r.status_code < 500:
                # Non-5xx is an immediate failure — no retry masks real bugs.
                break
            # Skip the sleep on the last iteration: no 4th attempt follows,
            # so sleeping here just pads the failure path with dead wait.
            if attempts < 3:
                await asyncio.sleep(1.0 * attempts)
    raise AssertionError(
        f"expected 200, got {last_status} after {attempts} attempt(s): {last_body}"
    )
