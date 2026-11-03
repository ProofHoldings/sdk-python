"""Confirmations resource (HITL approval requests)."""

from __future__ import annotations

import base64
import binascii
import hashlib
import re
from typing import Any, Literal
from urllib.parse import quote

from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from ..http import HttpClient
from ..types import ApprovalLinkResponse, Confirmation, ConfirmationListResponse

DecisionSignatureOutcome = Literal["verified", "unsigned", "key_mismatch", "input_mismatch", "signature_invalid"]
"""What ``verify_decision_signature`` found, checked in this order: ``unsigned`` (no decision yet, or one
recorded without signed evidence), ``key_mismatch`` (the key passed is not the key the decision
carries), ``input_mismatch`` (``signed_input`` does not name this confirmation, its action and its
comment, or ``status`` is not the signed action's), ``signature_invalid`` (the signature is not
base64, or does not verify under your key), ``verified``."""

_PEM_WHITESPACE = re.compile(r"[ \t\r\n]")
_BASE64 = re.compile(r"[A-Za-z0-9+/]*")
_LONE_SURROGATE = re.compile("[\ud800-\udfff]")
_SIGNED_STATUS = {"approve": "approved", "deny": "denied"}


_PEM_BLOCK = re.compile(r"-----BEGIN ([^\n-]*)-----([\s\S]*?)-----END \1-----")
_PEM_BODY = re.compile(r"[A-Za-z0-9+/]*={0,2}")
_KEY_FORMATS = {"PUBLIC KEY": serialization.PublicFormat.SubjectPublicKeyInfo, "RSA PUBLIC KEY": serialization.PublicFormat.PKCS1}


def _first_der_element(der: bytes) -> bytes | None:
    """The first DER element (a SEQUENCE) of ``der``, whatever follows it ignored, as OpenSSL reads a key."""
    if len(der) < 2 or der[0] != 0x30:
        return None
    length, start = der[1], 2
    if length & 0x80:
        n = length & 0x7F
        if n < 1 or n > 4 or len(der) < 2 + n:
            return None
        length, start = int.from_bytes(der[2 : 2 + n], "big"), 2 + n
    return der[: start + length] if start + length <= len(der) else None


def _rsa_public_key_from_pem(text: str) -> rsa.RSAPublicKey | None:
    """The RSA key in the first PEM block of ``text``, by the shared rule: label ``PUBLIC KEY`` (SPKI) or
    ``RSA PUBLIC KEY`` (PKCS#1), a base64 body, and a first DER element that is an rsaEncryption key
    re-encoding to itself, with a 4096- to 16384-bit modulus and an odd public exponent from 3 to 2^31 - 1.
    None for anything else."""
    block = _PEM_BLOCK.search(text)
    key_format = _KEY_FORMATS.get(block.group(1)) if block else None
    body = _PEM_WHITESPACE.sub("", block.group(2)) if block else ""
    if key_format is None or not _PEM_BODY.fullmatch(body) or len(body) % 4 != 0:
        return None
    element = _first_der_element(base64.b64decode(body, validate=True))
    if element is None:
        return None
    try:
        key = serialization.load_der_public_key(element)
    except (ValueError, UnsupportedAlgorithm):
        return None
    if not isinstance(key, rsa.RSAPublicKey) or key.public_bytes(serialization.Encoding.DER, key_format) != element:
        return None
    # A key every SDK verifies with: a 4096- to 16384-bit modulus (OpenSSL refuses larger, Go would not) and an odd
    # exponent from 3 to 2^31 - 1 (Go's crypto/rsa refuses larger).
    e = key.public_numbers().e
    return key if 4096 <= key.key_size <= 16384 and 3 <= e <= 2147483647 and e % 2 == 1 else None


class Confirmations:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        hitl_id: str,
        message: str,
        proof_expiry_days: int | None = None,
    ) -> Confirmation:
        """Create a confirmation request.

        ``message`` is the client-encrypted ciphertext envelope — the server
        never sees plaintext. Encrypt with :mod:`proof_sdk.crypto.hitl_crypto`
        against the HITL config's public key before calling.
        """
        body: dict[str, Any] = {"hitl_id": hitl_id, "message": message}
        if proof_expiry_days is not None:
            body["proof_expiry_days"] = proof_expiry_days
        return await self._http.post("/api/v1/confirmations", body)

    async def retrieve(self, id: str) -> Confirmation:
        """Get a confirmation by ID."""
        return await self._http.get(f"/api/v1/confirmations/{quote(id, safe='')}")

    def verify_decision_signature(self, confirmation: Confirmation, public_key: str) -> DecisionSignatureOutcome:
        """Check the decider's own signature on a confirmation's decision, locally (no request is made).

        The proof token is Proof's signed word about the decision; this checks the approver's, against
        ``public_key`` — the key YOU hold (SPKI or PKCS#1 PEM): for an owner decision, your HITL config's
        own public key; for an approver, the key you recorded from ``hitl.get_approver_keys()`` when they
        enrolled. The key the response carries must be that key; ``signed_input`` must be
        ``decision.<id>.<action>.<nonce>.<sha256 hex of response["text"], or ->`` for this confirmation's
        ``id``, its action and its comment, and ``status`` must be the signed action's (``approved`` for
        ``approve``, ``denied`` for ``deny``) — so a valid signature copied from another decision, or a
        status that contradicts it, does not pass; and ``signature`` must be base64 (either alphabet; padding
        and line breaks optional) of an RSASSA-PKCS1-v1_5 / SHA-256 signature that verifies under your key. Compare ``confirmation["id"]``
        with the id you asked for yourself. The key is required because a key the server sent is no
        evidence against the server. Never raises for anything inside the confirmation; the shared rule is
        ``sdks/shared/fixtures/decision_signature/README.md``.
        """
        fields: Any = confirmation if isinstance(confirmation, dict) else {}
        r = fields.get("response")
        if not isinstance(r, dict):
            return "unsigned"
        carried, signed_input, signature = r.get("public_key"), r.get("signed_input"), r.get("signature")
        if not (isinstance(carried, str) and isinstance(signed_input, str) and isinstance(signature, str)):
            return "unsigned"
        if not _PEM_WHITESPACE.sub("", carried) or not signed_input or not signature:
            return "unsigned"
        caller_key = _PEM_WHITESPACE.sub("", public_key) if isinstance(public_key, str) else ""
        if not caller_key or caller_key != _PEM_WHITESPACE.sub("", carried):
            return "key_mismatch"

        cid, status, action, text = fields.get("id"), fields.get("status"), r.get("action"), r.get("text")
        if not isinstance(cid, str) or not isinstance(action, str) or (text is not None and not isinstance(text, str)):
            return "input_mismatch"
        if status != _SIGNED_STATUS.get(action) or action not in _SIGNED_STATUS:
            return "input_mismatch"
        parts = signed_input.split(".")
        nonce = parts[3] if len(parts) > 3 else ""
        # Node hashes a lone surrogate as U+FFFD; so must this, or a server-written comment answers differently.
        digest = hashlib.sha256(_LONE_SURROGATE.sub("\ufffd", text).encode("utf-8")).hexdigest() if text else "-"
        if signed_input != f"decision.{cid}.{action}.{nonce}.{digest}":
            return "input_mismatch"

        try:
            b64 = re.sub(r"={1,2}$", "", _PEM_WHITESPACE.sub("", signature).replace("-", "+").replace("_", "/"))
            if not _BASE64.fullmatch(b64) or len(b64) % 4 == 1:
                return "signature_invalid"
            raw = base64.b64decode(b64 + "=" * (-len(b64) % 4), validate=True)
            key = _rsa_public_key_from_pem(public_key)
            if key is None:
                return "signature_invalid"
            # Node signs a lone surrogate as U+FFFD (and Go's JSON decoder reads one so): hash those bytes.
            key.verify(raw, _LONE_SURROGATE.sub("\ufffd", signed_input).encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
        except (InvalidSignature, UnsupportedAlgorithm, ValueError, TypeError, UnicodeError, binascii.Error):
            return "signature_invalid"
        return "verified"

    async def approval_link(self, id: str) -> ApprovalLinkResponse:
        """Get the HMAC approval link for a pending confirmation.

        It is the HITL config owner's link, decided with the config's own key. It is not an
        approver's link: an approver's goes only to their own channel, and
        ``POST /api/v1/confirmations/{id}/resend`` ("Send again") is what sends it there again.
        Every call returns the same owner link until "Send again" reaches the owner; "Send again"
        replaces it, and the next call returns a new one.
        """
        return await self._http.post(f"/api/v1/confirmations/{quote(id, safe='')}/approval-link")

    async def list(
        self,
        *,
        status: str | None = None,
        hitl_id: str | None = None,
        profile_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> ConfirmationListResponse:
        """List confirmations with optional filters."""
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if hitl_id is not None:
            params["hitl_id"] = hitl_id
        if profile_id is not None:
            params["profile_id"] = profile_id
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page
        return await self._http.get("/api/v1/confirmations", params)
