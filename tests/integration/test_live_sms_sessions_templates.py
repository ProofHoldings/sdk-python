"""Live coverage for what 1.2.0 adds: SMS sessions and per-project templates.

Skips outside live mode (``PROOF_BASE_URL`` + ``PROOF_API_KEY_TEST``); runs against staging in the
staging deploy and production in the production deploy. Nothing here sends a message or writes a
row: creating an SMS session only stores a code the person would text in, and the template calls read.
"""

from __future__ import annotations

import re
from urllib.parse import quote

import pytest

from proof_sdk import ForbiddenError

from .conftest import is_live_mode

pytestmark = pytest.mark.skipif(not is_live_mode(), reason="live mode only")

# A well-formed project id no account owns: naming it must be refused, which is what proves
# ``profile_id`` reaches the server rather than being dropped on the way.
UNOWNED_PROFILE_ID = "000000000000000000000000"


async def test_sms_session_carries_code_message_numbers_and_deep_link(make_client):
    client = await make_client()
    session = await client.sessions.create(
        channel="sms",
        client_metadata={"test_harness": "sdk-integration", "sdk": "python"},
    )

    assert session["id"]
    assert session["channel"] == "sms"
    assert session["status"] == "pending"
    assert re.fullmatch(r"\S+", session["sms_code"])
    assert session["sms_code"] in session["sms_message"]
    did = session["sms_dids"]["americas"]["did"]
    assert re.fullmatch(r"\+\d+", did)
    assert session["deep_link"] == f"sms:{did}?body={quote(session['sms_message'], safe='')}"

    fetched = await client.sessions.retrieve(session["id"])
    assert fetched["id"] == session["id"]
    assert fetched["status"] == "pending"


async def test_templates_for_the_keys_default_project(make_client):
    client = await make_client()
    listed = await client.templates.list()
    assert re.fullmatch(r"[0-9a-f]{24}", listed["profile_id"])
    assert isinstance(listed["custom_templates"], list)
    assert "sms" in listed["available_channels"]

    template = await client.templates.retrieve("sms", "verification_request")
    assert template["profile_id"] == listed["profile_id"]
    assert template["scope"] in ("project", "default")
    assert isinstance(template["template"]["body"], str)


async def test_templates_for_a_named_project_and_the_name_reaches_the_server(make_client):
    client = await make_client()
    project_id = (await client.templates.list())["profile_id"]

    listed = await client.templates.list(profile_id=project_id)
    assert listed["profile_id"] == project_id
    template = await client.templates.retrieve("sms", "verification_request", profile_id=project_id)
    assert template["profile_id"] == project_id

    with pytest.raises(ForbiddenError) as refused:
        await client.templates.list(profile_id=UNOWNED_PROFILE_ID)
    assert refused.value.code in ("profile_not_owned", "profile_mismatch")
