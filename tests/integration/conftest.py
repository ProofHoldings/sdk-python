"""Shared fixtures for the Python SDK integration suite.

Same dual-mode philosophy as the JS suite:

* Live mode — ``PROOF_BASE_URL`` + ``PROOF_API_KEY_TEST`` set → hit staging.
* Mock mode — otherwise → inject an ``httpx.MockTransport`` so the SDK still
  exercises its wire contract deterministically.

In live mode, when ``CF_ACCESS_CLIENT_ID`` and ``CF_ACCESS_CLIENT_SECRET``
are also set, Cloudflare Access service-token headers are added to every
request so the suite can traverse the Access perimeter that fronts staging.

Mirrors the Go SDK's integration scope: client, resources, errors, polling,
streaming parser.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable

import httpx
import pytest
import pytest_asyncio

from proof_sdk import Proof
from proof_sdk.version import VERSION


SHARED_FIXTURES = Path(__file__).resolve().parents[3] / "shared" / "fixtures"


def shared_fixture(name: str) -> dict[str, Any]:
    """Load and strip metadata from a fixture under ``sdks/shared/fixtures``.

    Metadata keys (``_note``, ``_source``, ...) are dropped so callers get
    exactly the wire shape the SDK is expected to see. The canonical
    validator lives in ``src/__tests__/drift/sdk-fixtures.test.ts`` — adding
    a key here that the server doesn't actually return will surface as a
    drift-test failure the next time the backend suite runs.
    """
    with (SHARED_FIXTURES / name).open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return {k: v for k, v in raw.items() if not k.startswith("_")}


LIVE_MODE = bool(os.environ.get("PROOF_BASE_URL") and os.environ.get("PROOF_API_KEY_TEST"))


def is_live_mode() -> bool:
    return LIVE_MODE


def cf_access_headers() -> dict[str, str]:
    """Cloudflare Access + visual-test-secret headers, if the credentials are in env.

    Returned as a dict (possibly empty) so call sites can splat into any
    ``headers=`` mapping without conditionals.
    """
    headers: dict[str, str] = {}
    cid = os.environ.get("CF_ACCESS_CLIENT_ID")
    secret = os.environ.get("CF_ACCESS_CLIENT_SECRET")
    if cid and secret:
        headers["CF-Access-Client-Id"] = cid
        headers["CF-Access-Client-Secret"] = secret
    visual_secret = os.environ.get("VISUAL_TEST_SECRET")
    if visual_secret:
        headers["X-Visual-Test-Secret"] = visual_secret
    return headers


Handler = Callable[[httpx.Request], httpx.Response]


def _default_handler(_req: httpx.Request) -> httpx.Response:
    return httpx.Response(404, json={"error": {"code": "not_found", "message": "no handler"}})


def _sdk_default_headers(api_key: str) -> dict[str, str]:
    # Keep this mirrored against ``proof_sdk/http.py`` — the staging origin's
    # marketing nginx (``frontend.conf``) returns 444 for library-default UAs
    # like ``python-httpx/*``, surfacing as CF 520. Any test that rebuilds the
    # SDK's httpx client must carry the branded UA through.
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": f"proof-sdk-python/{VERSION}",
    }


async def _patch_client_with_transport(proof: Proof, handler: Handler) -> None:
    """Replace the internal httpx.AsyncClient with one using MockTransport.

    Closes the pre-existing client (if any) before swapping so file descriptors
    don't leak. All four attributes (_http, _client, _timeout, _api_key) are
    intentionally private — we own both sides of this seam.
    """
    transport = httpx.MockTransport(handler)
    http = proof._http
    previous = http._client
    http._client = httpx.AsyncClient(
        base_url=http.base_url,
        timeout=http._timeout,
        headers=_sdk_default_headers(http._api_key),
        transport=transport,
    )
    if previous is not None and not previous.is_closed:
        await previous.aclose()


async def _patch_client_with_cf_access(proof: Proof) -> None:
    """Wrap the internal httpx.AsyncClient with CF Access service-token headers.

    The SDK's own ``_get_client`` doesn't know about Cloudflare Access, so we
    replace the internal client with one whose default headers include the
    service-token pair. This keeps all Access plumbing in the test harness
    and out of the shipped SDK.

    No-op when CF Access credentials aren't set (e.g. running against a
    non-Access-gated origin).
    """
    access = cf_access_headers()
    if not access:
        return
    http = proof._http
    previous = http._client
    http._client = httpx.AsyncClient(
        base_url=http.base_url,
        timeout=http._timeout,
        headers={**_sdk_default_headers(http._api_key), **access},
    )
    if previous is not None and not previous.is_closed:
        await previous.aclose()


@pytest_asyncio.fixture
async def make_client():
    """Factory returning a configured Proof client.

    In live mode, returns a real client against ``PROOF_BASE_URL`` with CF
    Access headers injected when available. In mock mode, returns a client
    whose httpx transport is driven by ``handler``.
    """
    created: list[Proof] = []

    async def _factory(handler: Handler | None = None, **overrides: Any) -> Proof:
        api_key = os.environ.get("PROOF_API_KEY_TEST", "pk_test_integration")
        base_url = os.environ.get("PROOF_BASE_URL", "https://mock.proof.test")
        proof = Proof(
            api_key,
            base_url=base_url,
            timeout=overrides.get("timeout", 15.0),
            max_retries=overrides.get("max_retries", 0),
        )
        # Track for teardown BEFORE any patching so a raised AttributeError
        # (e.g. SDK renamed a private field) still results in cleanup.
        created.append(proof)
        if LIVE_MODE:
            await _patch_client_with_cf_access(proof)
        else:
            await _patch_client_with_transport(proof, handler or _default_handler)
        return proof

    yield _factory

    # Close every tracked client; ignore per-client close errors so one bad
    # close doesn't prevent the others from releasing sockets.
    for p in created:
        try:
            await p.close()
        except Exception:
            pass
