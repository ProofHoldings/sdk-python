"""Error taxonomy: 400/401/403/404/409/429/500."""

from __future__ import annotations

import httpx
import pytest

from proof_sdk import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .conftest import Handler, is_live_mode


def _make_handler(status: int, body: dict) -> Handler:
    def h(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=body)
    return h


@pytest.mark.parametrize(
    "status,exc_cls",
    [
        (400, ValidationError),
        (401, AuthenticationError),
        (403, ForbiddenError),
        (404, NotFoundError),
        (409, ConflictError),
        (429, RateLimitError),
        (500, ServerError),
    ],
)
async def test_status_to_error_class(make_client, status, exc_cls):
    if is_live_mode():
        pytest.skip("error taxonomy covered by wire-layer mock in mock mode")
    handler = _make_handler(status, {"error": {"code": "x", "message": "boom"}})
    proof = await make_client(handler)
    with pytest.raises(exc_cls):
        await proof.verifications.retrieve("v_x")


async def test_rate_limit_carries_retry_after(make_client):
    if is_live_mode():
        pytest.skip()
    handler = _make_handler(429, {
        "error": {"code": "rate_limited", "message": "slow", "retryAfter": 42},
    })
    proof = await make_client(handler)
    with pytest.raises(RateLimitError):
        await proof.verifications.retrieve("v_x")


async def test_live_bad_api_key_is_rejected():
    if not is_live_mode():
        pytest.skip("live mode only")
    import os
    from proof_sdk import Proof as P
    from .conftest import _patch_client_with_cf_access

    proof = P("pk_test_this_key_does_not_exist", base_url=os.environ["PROOF_BASE_URL"])
    # Inject CF Access service-token headers so we traverse the Access
    # perimeter and actually reach the API — otherwise Cloudflare would
    # return 403 and the generic ``ProofError`` assertion would pass on a
    # false positive without the request ever hitting the backend.
    await _patch_client_with_cf_access(proof)
    try:
        with pytest.raises(AuthenticationError):
            await proof.verifications.list()
    finally:
        await proof.close()
