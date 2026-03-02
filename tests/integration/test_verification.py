"""
Python SDK — Live API integration tests.

Run against a real server using pk_test_* keys.
NOT included in the default test suite.

Prerequisites:
    PROOF_API_KEY_TEST — Required, must start with "pk_test_"
    PROOF_BASE_URL     — Optional, defaults to "https://api.proof.holdings"

Run:
    PROOF_API_KEY_TEST=pk_test_xxx pytest tests/integration/ -v
"""

from __future__ import annotations

import os

import pytest

API_KEY = os.environ.get("PROOF_API_KEY_TEST", "")
BASE_URL = os.environ.get("PROOF_BASE_URL", "https://api.proof.holdings")

import time

_counter = 0

def unique_email(prefix: str) -> str:
    global _counter
    _counter += 1
    return f"{prefix}-{int(time.time())}-{_counter}@example.com"

pytestmark = pytest.mark.skipif(
    not API_KEY.startswith("pk_test_"),
    reason="PROOF_API_KEY_TEST not set or not a test key",
)


@pytest.fixture
def client():
    from proof_sdk import Proof

    return Proof(API_KEY, base_url=BASE_URL)


class TestVerificationCRUD:
    def test_create_phone_verification(self, client) -> None:
        verification = client.verifications.create(
            type="phone", channel="sms", identifier="+14155550100"
        )
        assert verification.id
        assert verification.status == "pending"

    def test_list_verifications(self, client) -> None:
        result = client.verifications.list(limit=5)
        assert isinstance(result.data, list)
        assert result.pagination is not None

    def test_retrieve_verification(self, client) -> None:
        created = client.verifications.create(
            type="email", channel="email", identifier=unique_email("py-sdk-test")
        )
        retrieved = client.verifications.retrieve(created.id)
        assert retrieved.id == created.id


class TestProofRoundTrip:
    def test_verify_and_validate(self, client) -> None:
        verification = client.verifications.create(
            type="email", channel="email", identifier=unique_email("py-sdk-proof")
        )
        verified = client.verifications.test_verify(verification.id)
        assert verified.proof_token

        proof = client.proofs.validate(verified.proof_token)
        assert proof.valid is True


class TestVerificationRequests:
    def test_create_and_retrieve(self, client) -> None:
        vr = client.verification_requests.create(
            assets=[{"type": "email", "identifier": unique_email("py-sdk-vr")}]
        )
        assert vr.id

        retrieved = client.verification_requests.retrieve(vr.id)
        assert retrieved.id == vr.id


class TestProofs:
    def test_list_revoked(self, client) -> None:
        result = client.proofs.list_revoked()
        assert isinstance(result.revoked, list)
        assert isinstance(result.count, int)
