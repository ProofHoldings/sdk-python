"""Deep live-mode lifecycle coverage for the Python SDK.

All tests here skip outside live mode. In live mode they exercise the real
verification lifecycle against staging (or production, for the production
branch pipeline) using test-mode API keys — the pk_test_* key path that
routes through ``/test-verify`` and never triggers a real messaging channel.

Created resources are tagged via ``client_metadata`` so the staging-data
pruner can reclaim them later:

    client_metadata = {
        "test_harness": "sdk-integration",
        "test_run_id":  <CI_PIPELINE_ID or local token>,
        "sdk":          "python",
    }
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any

import pytest

from proof_sdk import NotFoundError, ValidationError

from .conftest import is_live_mode

pytestmark = pytest.mark.skipif(not is_live_mode(), reason="live mode only")


def _test_run_id() -> str:
    return (
        os.environ.get("CI_PIPELINE_ID")
        or os.environ.get("PROOF_TEST_RUN_ID")
        or f"local-{os.environ.get('USER', 'unknown')}-{int(time.time())}"
    )


def _tag_metadata(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    meta = {
        "test_harness": "sdk-integration",
        "test_run_id": _test_run_id(),
        "sdk": "python",
    }
    if extra:
        meta.update(extra)
    return meta


# Real Proof-controlled phone number — staging SMS DID by default. The
# backend's phone validator rejects reserved/fictional ranges, so test
# fixtures must use real numbers we control. Reusing one number across
# concurrent tests is safe because the ``pk_test_*`` key path routes through
# ``/test-verify`` and never triggers real SMS dispatch — the number is
# effectively an opaque label, not a delivery target. Each
# ``verifications.create`` writes a fresh document, and tests key their
# state off the returned ``id``, not off the phone.
TEST_PHONE_IDENTIFIER: str = os.environ.get("TEST_PHONE_IDENTIFIER", "+19295909022")


def _external_user_id() -> str:
    return f"sdk_py_{_test_run_id()}"


async def test_verification_lifecycle_create_retrieve_list_testverify(make_client):
    """The full happy path: create → retrieve → list → test-verify."""
    proof = await make_client()

    created = await proof.verifications.create(
        type="phone",
        channel="sms",
        identifier=TEST_PHONE_IDENTIFIER,
        external_user_id=_external_user_id(),
        client_metadata=_tag_metadata({"stage": "lifecycle"}),
    )
    assert "id" in created, f"response missing id: {created}"
    assert created["status"] == "pending"
    vid = created["id"]

    fetched = await proof.verifications.retrieve(vid)
    assert fetched["id"] == vid
    assert fetched["identifier"] == created["identifier"]

    listed = await proof.verifications.list(limit=5)
    assert isinstance(listed.get("data"), list)
    assert "pagination" in listed
    assert listed["pagination"]["page"] >= 1

    verified = await proof.verifications.test_verify(vid)
    assert verified["status"] == "verified"
    assert verified.get("test_mode") is True
    assert verified.get("proof_token"), "test-verify should return a proof token"


async def test_verification_retrieve_unknown_id_raises_not_found(make_client):
    proof = await make_client()
    with pytest.raises(NotFoundError):
        # 24-hex-char ObjectId that doesn't exist
        await proof.verifications.retrieve("000000000000000000000000")


async def test_verification_create_rejects_invalid_payload(make_client):
    proof = await make_client()
    with pytest.raises(ValidationError):
        # channel missing — server-side Zod validation must 400
        await proof.verifications.create(
            type="phone",
            channel="not_a_real_channel",
            identifier="not-a-phone",
        )


async def test_verifications_list_pagination_envelope_shape(make_client):
    proof = await make_client()
    page = await proof.verifications.list(page=1, limit=3)
    data = page.get("data")
    pg = page.get("pagination")
    assert isinstance(data, list)
    assert pg and isinstance(pg, dict)
    for key in ("page", "limit", "total"):
        assert key in pg, f"pagination missing key {key}"


async def test_verified_users_read_only(make_client):
    """Read-only: list verified users. No side effects."""
    proof = await make_client()
    result = await proof.verifications.list_verified_users(limit=3)
    assert isinstance(result.get("data"), list)


async def test_list_webhook_deliveries_read_only(make_client):
    proof = await make_client()
    page = await proof.webhook_deliveries.list(limit=3)
    # An account may legitimately have zero deliveries; just prove the envelope
    # matches. NOTE: this endpoint is the one outlier in the API surface —
    # backend returns {deliveries: [...], pagination: {...}} instead of the
    # standard {data: [...], pagination: {...}}. See
    # src/controllers/webhookDeliveries.ts.
    assert isinstance(page.get("deliveries"), list)
    assert "pagination" in page


async def test_webhook_deliveries_stats_read_only(make_client):
    proof = await make_client()
    stats = await proof.webhook_deliveries.stats()
    # Shape check — stats vary per-account.
    assert isinstance(stats, dict)


async def test_wait_for_completion_reaches_terminal_state(make_client):
    """Polling round-trip: create → test_verify from another coroutine →
    wait_for_completion returns the terminal record via polling.
    """
    proof = await make_client()

    created = await proof.verifications.create(
        type="phone",
        channel="sms",
        identifier=TEST_PHONE_IDENTIFIER,
        external_user_id=_external_user_id(),
        client_metadata=_tag_metadata({"stage": "polling"}),
    )
    vid = created["id"]

    async def _trigger() -> None:
        await asyncio.sleep(0.3)
        await proof.verifications.test_verify(vid)

    trigger_task = asyncio.create_task(_trigger())
    try:
        final = await proof.verifications.wait_for_completion(
            vid, interval=0.5, timeout=20.0, max_interval=1.0,
        )
    finally:
        # Only suppress the cancellation itself. Anything the trigger raises
        # on its own (AuthenticationError, 409, etc.) should surface as a
        # test failure instead of turning into an unexplained polling
        # timeout.
        trigger_task.cancel()
        try:
            await trigger_task
        except asyncio.CancelledError:
            pass

    assert final["status"] == "verified"


async def test_live_stream_verification_events_first_event(make_client):
    """Subscribe to the verification events stream and observe at least one
    event. ``test_verify`` from a background task nudges the status so we
    don't hang waiting for real channel traffic. Uses an explicit cancel
    event + generator ``aclose()`` so the underlying httpx response is
    torn down even if the consumer breaks out after the first event.
    """
    proof = await make_client()

    created = await proof.verifications.create(
        type="phone",
        channel="sms",
        identifier=TEST_PHONE_IDENTIFIER,
        external_user_id=_external_user_id(),
        client_metadata=_tag_metadata({"stage": "streaming"}),
    )
    vid = created["id"]

    first_event: dict[str, Any] | None = None
    cancel = asyncio.Event()
    stream = proof.verifications.stream(vid, cancel_event=cancel)

    async def _consume() -> None:
        nonlocal first_event
        try:
            async for event in stream:
                first_event = event
                break
        finally:
            cancel.set()
            # Explicit aclose so httpx releases the long-lived SSE response
            # immediately rather than waiting for GC.
            await stream.aclose()

    async def _trigger() -> None:
        await asyncio.sleep(0.5)
        await proof.verifications.test_verify(vid)

    await asyncio.wait_for(
        asyncio.gather(_consume(), _trigger()),
        timeout=20.0,
    )

    assert first_event is not None, "expected at least one SSE event"
    assert isinstance(first_event, dict)
