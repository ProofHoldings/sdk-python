"""Resource round-trip: verification create + retrieve + list.

All handlers consume the shared wire fixtures under
``sdks/shared/fixtures/`` so contract drift surfaces in the backend drift
test (``src/__tests__/drift/sdk-fixtures.test.ts``) rather than silently
poisoning every SDK mock.
"""

from __future__ import annotations

import httpx
import pytest

from .conftest import is_live_mode, shared_fixture


_VERIFICATION = shared_fixture("verification.json")
_VERIFICATION_LIST = shared_fixture("verification_list.json")


def _verification_handler(req: httpx.Request) -> httpx.Response:
    if req.method == "POST" and req.url.path == "/api/v1/verifications":
        return httpx.Response(201, json=_VERIFICATION)
    if req.method == "GET" and req.url.path == f"/api/v1/verifications/{_VERIFICATION['id']}":
        return httpx.Response(200, json=_VERIFICATION)
    if req.method == "GET" and req.url.path == "/api/v1/verifications":
        return httpx.Response(200, json=_VERIFICATION_LIST)
    return httpx.Response(404, json={"error": {"code": "not_found", "message": "no handler"}})


async def test_create_and_retrieve_verification(make_client):
    if is_live_mode():
        pytest.skip("live mode skips mutating SMS flow")
    proof = await make_client(_verification_handler)
    created = await proof.verifications.create(
        type=_VERIFICATION["type"],
        channel=_VERIFICATION["channel"],
        identifier=_VERIFICATION["identifier"],
    )
    assert created["id"] == _VERIFICATION["id"]
    assert created["status"] == _VERIFICATION["status"]

    fetched = await proof.verifications.retrieve(_VERIFICATION["id"])
    assert fetched["identifier"] == _VERIFICATION["identifier"]
    assert fetched["created_at"] == _VERIFICATION["created_at"]


async def test_list_verifications_pagination_envelope(make_client):
    if is_live_mode():
        pytest.skip("live mode skips list-as-shape assertion")
    proof = await make_client(_verification_handler)
    page = await proof.verifications.list()
    assert isinstance(page["data"], list)
    assert page["pagination"]["page"] == 1
    # total_pages is the canonical key name in the shared fixture; if the
    # backend ever switches to `pages`, the drift test catches it first.
    assert "total_pages" in page["pagination"]
