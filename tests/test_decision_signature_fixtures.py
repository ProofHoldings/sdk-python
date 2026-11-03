"""The shared decision-signature cases (``sdks/shared/fixtures/decision_signature/cases.json``)
through ``Proof(...).confirmations.verify_decision_signature`` — a local check, so the client is
never asked to send anything."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import httpx
import pytest

from proof_sdk import Proof

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT.parent / "shared" / "fixtures" / "decision_signature" / "cases.json").read_text())


def _refuse(request: httpx.Request) -> httpx.Response:
    raise AssertionError(f"verify_decision_signature must not reach the network: {request.url}")


@pytest.fixture
def proof() -> Proof:
    client = Proof("pk_test_decision_signature")
    client._http._client = httpx.AsyncClient(transport=httpx.MockTransport(_refuse))
    return client


def test_reads_every_case() -> None:
    assert len(FIXTURE["cases"]) > 0


@pytest.mark.parametrize("case", FIXTURE["cases"], ids=[c["name"] for c in FIXTURE["cases"]])
def test_case(proof: Proof, case: dict) -> None:
    outcome = proof.confirmations.verify_decision_signature(case["confirmation"], case["public_key"])
    assert outcome == case["expected"]


def test_lone_surrogate_in_the_signed_input_is_read_as_node_and_go_read_it(proof: Proof) -> None:
    # Not a shared case: PHP's json_decode refuses a lone surrogate in the whole file (and in an API body).
    # Node signs one as U+FFFD and Go's JSON decoder reads one as U+FFFD; Python must hash the same bytes.
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    pem = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    signed_input = "decision.c\ud800x.approve.n\ud800.-"
    as_node_signs = signed_input.replace("\ud800", "�").encode("utf-8")
    signature = base64.b64encode(key.sign(as_node_signs, padding.PKCS1v15(), hashes.SHA256())).decode()
    confirmation = {
        "id": "c\ud800x",
        "status": "approved",
        "response": {"action": "approve", "text": None, "public_key": pem, "signed_input": signed_input, "signature": signature},
    }
    assert proof.confirmations.verify_decision_signature(confirmation, pem) == "verified"
