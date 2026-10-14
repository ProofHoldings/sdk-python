"""Proofs resource."""

from __future__ import annotations

import base64
import json
import math
import zlib
from typing import Any
from urllib.parse import quote, urlsplit

from ..http import HttpClient
from ..jwks.key_set_cache import (
    DEFAULT_MAX_JWKS_AGE_SECONDS,
    KeyCandidate,
    KeySetCache,
    Keys,
    Stale,
    Unavailable,
    is_supported_algorithm,
    now_wall_seconds,
    validate_max_jwks_age,
)
from ..jwks.keyset import Revoked, Unknown, WrongPurpose, check_key_policy

#: Clock skew tolerated on both the proof token and the status list, in seconds.
CLOCK_TOLERANCE_SECONDS = 5

#: Ceiling on a fetched status list, mirroring ``@proof-holdings/delegation-verifier``.
MAX_STATUS_LIST_BYTES = 512 * 1024

STATUS_LIST_TIMEOUT_SECONDS = 5.0

#: The draft's 2-bit slot values (draft-ietf-oauth-status-list).
_SLOT_VALID = 0b00
_SLOT_REVOKED = 0b01
_SLOT_SUSPENDED = 0b10

#: The only ``iss`` a proof token may carry.
PROOF_TOKEN_ISSUER = "proof.holdings"


#: Ports that add nothing to an origin, since they are the scheme's own default.
_DEFAULT_PORTS = {"http": 80, "https": 443}


def _origin(url: str) -> str:
    """The origin of a url, normalized the way ``URL.origin`` does it in the JS SDK.

    Scheme and host lowercased, a port dropped when it is the scheme's default. The four SDKs
    must answer this question identically, or a status-list uri accepted by one is refused by
    another.
    """
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    host = (parts.hostname or "").lower()
    port = parts.port
    suffix = "" if port is None or _DEFAULT_PORTS.get(scheme) == port else f":{port}"
    return f"{scheme}://{host}{suffix}"


def _read_status_list_claim(claims: dict[str, Any]) -> dict[str, Any] | None:
    """The token's own slot reference, or None when it carries none."""
    status = claims.get("status")
    if not isinstance(status, dict):
        return None
    status_list = status.get("status_list")
    if not isinstance(status_list, dict):
        return None
    idx, uri = status_list.get("idx"), status_list.get("uri")
    if not isinstance(idx, int) or isinstance(idx, bool) or idx < 0:
        return None
    if not isinstance(uri, str) or not uri:
        return None
    return {"idx": idx, "uri": uri}


def _read_status_slot(data: bytes, index: int, bits: int) -> int | None:
    """Read one slot: lowest index in the least significant bits, ``bits`` statuses per byte.

    ``None`` means the array does not reach that index — "no answer", never "valid". The byte
    order is pinned across the four SDKs and the issuer by
    ``sdks/shared/fixtures/status_list_slots.json``.
    """
    if index < 0 or bits not in (1, 2, 4, 8):
        return None
    per_byte = 8 // bits
    byte_index = index // per_byte
    if byte_index >= len(data):
        return None
    return (data[byte_index] >> ((index % per_byte) * bits)) & ((1 << bits) - 1)


def _b64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _decode_segment(token: str, index: int) -> dict[str, Any]:
    """One JSON segment of a compact JWT, UNVERIFIED. Raises ``ValueError`` for anything malformed."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("token is not a compact JWT")
    try:
        decoded = json.loads(_b64url_decode(parts[index]))
    except Exception:
        raise ValueError("token segment is not base64url JSON") from None
    if not isinstance(decoded, dict):
        raise ValueError("token segment is not a JSON object")
    return decoded


def _numeric_date(value: Any) -> float | None:
    """A NumericDate as a finite number, or None — ``null``, ``NaN`` and ``Infinity`` are not dates."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    return float(value)


def _claims_failure(
    payload: dict[str, Any], *, issuer: str | None, require_exp: bool, reject_audience: bool
) -> tuple[str, str] | None:
    """The token's own claims against the SDK's wall clock, the way ``jwt.decode`` checked them before.

    Checked here rather than by ``jwt.decode`` because the clock must be the one the key set ages
    on, which PyJWT cannot take. A registered claim that is present is held to its type even when
    its value is ``null``. One deliberate difference: a NumericDate must be a JSON number — PyJWT
    coerced a numeric string through ``int()``, jose (the JS SDK) does not, and neither does this.
    Returns ``(reason, message)`` or None.
    """
    now = now_wall_seconds()
    if "iat" in payload:
        iat = _numeric_date(payload["iat"])
        if iat is None:
            return "invalid", "Issued At claim (iat) must be a number"
        if iat > now + CLOCK_TOLERANCE_SECONDS:
            return "invalid", "The token is not yet valid (iat)"
    if "nbf" in payload:
        nbf = _numeric_date(payload["nbf"])
        if nbf is None:
            return "invalid", "Not Before claim (nbf) must be a number"
        if nbf > now + CLOCK_TOLERANCE_SECONDS:
            return "invalid", "The token is not yet valid (nbf)"
    if "exp" in payload:
        exp = _numeric_date(payload["exp"])
        if exp is None:
            return "invalid", "Expiration Time claim (exp) must be a number"
        if exp <= now - CLOCK_TOLERANCE_SECONDS:
            return "expired", "Signature has expired"
    elif require_exp:
        return "invalid", 'Token is missing the "exp" claim'
    if issuer is not None and payload.get("iss") != issuer:
        return "invalid", "Invalid issuer"
    # No audience is asked for, so a token addressed to one is not for this caller. An empty `aud`
    # names nobody and passes, as it did under `jwt.decode`.
    if reject_audience and payload.get("aud"):
        return "invalid", "Invalid audience"
    if "sub" in payload and not isinstance(payload["sub"], str):
        return "invalid", "Subject (sub) must be a string"
    if "jti" in payload and not isinstance(payload["jti"], str):
        return "invalid", "JWT ID (jti) must be a string"
    return None


class Proofs:
    def __init__(self, http: HttpClient, *, max_jwks_age: float = DEFAULT_MAX_JWKS_AGE_SECONDS) -> None:
        self._http = http
        self._key_set = KeySetCache(
            http, f"{http.base_url}/.well-known/jwks.json", validate_max_jwks_age(max_jwks_age)
        )
        #: The last status list read, reusable until the issuer's own ``ttl``/``exp`` runs out.
        self._status_list_cache: dict[str, Any] | None = None

    async def validate(self, proof_token: str, identifier: str | None = None) -> dict[str, Any]:
        """Validate a proof token online (checks revocation status).

        Pass ``identifier`` to also bind the proof to the identifier you expect it to be
        about: a proof about anything else answers ``valid: False`` with reason
        ``identifier_mismatch``, and a proof of an encrypted decision — whose hash is over
        ciphertext — answers ``identifier_unverifiable``. For a proof about a verified
        identifier any format is accepted and canonicalized as it was at issuance; a proof of
        an approval decision binds only on the exact recipient value it was issued for.
        """
        body: dict[str, Any] = {"proof_token": proof_token}
        if identifier is not None:
            body["identifier"] = identifier
        return await self._http.post("/api/v1/proofs/validate", body)

    async def revoke(self, id: str, reason: str | None = None) -> dict[str, Any]:
        """Revoke a proof by public handle (``ph_ctl_*``/``ph_dlg_*``) or verification id.

        Revoking a PROOF does not withdraw the asset, consent or delegation it is about —
        those have their own surfaces.
        """
        body: dict[str, Any] = {}
        if reason is not None:
            body["reason"] = reason
        return await self._http.post(f"/api/v1/proofs/{quote(id, safe="")}/revoke", body)

    async def status(self, id: str) -> dict[str, Any]:
        """Get the status of a proof by public handle (``ph_ctl_*``/``ph_dlg_*``) or verification id.

        A live proof reads ``active``.
        """
        return await self._http.get(f"/api/v1/proofs/{quote(id, safe="")}/status")

    async def list_revoked(self) -> dict[str, Any]:
        """Get the revocation list."""
        return await self._http.get("/api/v1/proofs/revoked")

    async def verify_offline(self, token: str, *, check_revocation: bool = True) -> dict[str, Any]:
        """Verify a proof token without calling the Proof API with your key.

        Two public documents are read, both cacheable and neither revealing which proof you are
        checking: the JWKS (for the signature) and the issuer's Token Status List (for
        revocation).

        By default the proof's status-list slot IS checked, so a revoked or suspended proof
        answers ``valid: False`` with ``reason`` ``revoked``/``suspended``. A list that cannot be
        read — unreachable, failing its own checks, or not covering this slot — answers
        ``status_unavailable``: the refusal to guess, not a claim that the proof is withdrawn. A
        token carrying no slot at all stays valid with ``revocation_checked: False``, which is
        exactly what the issuer's own ``POST /proofs/validate`` answers for it.

        Pass ``check_revocation=False`` to check the signature alone; the result then reports
        ``revocation_checked: False``.

        The key set follows the issuer's key-rotation rules (``sdks/shared/fixtures/jwks_rotation/``):
        a key the issuer revoked answers ``key_revoked`` with a ``pull_hint`` naming where a re-issued
        token can be fetched; a key set that could not be refreshed for longer than ``max_jwks_age``
        answers ``jwks_stale`` with its ``cache_age_seconds``; a key of another family, a token signed
        outside its key's window or living longer than the key allows answer ``wrong_key_purpose``,
        ``outside_key_window`` and ``token_lifetime_exceeded``; a ``kid`` the issuer does not publish
        answers ``unknown_key``. A key set that could not be read at all answers ``status_unavailable``.

        Requires the ``PyJWT`` package (the ``jwt`` extra).
        Install with: ``pip install 'proof-holdings-sdk[jwt]'``
        """
        try:
            import jwt  # noqa: F401
        except ImportError:
            raise ImportError(
                "Offline verification requires PyJWT. "
                "Install with: pip install 'proof-holdings-sdk[jwt]'"
            )

        try:
            unverified = _decode_segment(token, 1)
        except ValueError as e:
            return {"valid": False, "error": str(e), "reason": "invalid", "revocation_checked": False}
        # The family only selects which key may answer; the signature still has to match that key.
        family = "delegation" if unverified.get("token_type") == "delegation" else "proof"

        try:
            checked = await self._verify_against_key_set(token, family, issuer=PROOF_TOKEN_ISSUER, require_exp=False)
        except Exception as e:
            checked = {"ok": False, "reason": "invalid", "message": str(e) or "Token verification failed"}
        if not checked["ok"]:
            failure: dict[str, Any] = {
                "valid": False,
                "error": checked["message"],
                "reason": checked["reason"],
                "revocation_checked": False,
            }
            if checked["reason"] == "key_revoked":
                handle = unverified.get("sub") if family == "delegation" else unverified.get("proof_id")
                failure["pull_hint"] = {
                    "issuer_origin": _origin(self._http.base_url),
                    "handle": handle if isinstance(handle, str) else None,
                }
            if checked["reason"] == "jwks_stale":
                failure["cache_age_seconds"] = checked.get("cache_age_seconds")
            return failure
        payload = checked["payload"]

        verified: dict[str, Any] = {
            "valid": True,
            "payload": {
                "iss": payload.get("iss"),
                "sub": payload.get("sub"),
                "iat": payload.get("iat"),
                "exp": payload.get("exp"),
                "type": payload.get("type"),
                "channel": payload.get("channel"),
                "identifier_hash": payload.get("identifier_hash"),
                "verified_at": payload.get("verified_at"),
                "user_id": payload.get("user_id"),
                "decision": payload.get("decision"),
            },
            "revocation_checked": False,
        }

        if not check_revocation:
            return verified

        claim = _read_status_list_claim(payload)
        if claim is None:
            return verified

        state, message = await self._check_status_list(claim)
        if state == "valid":
            return {**verified, "revocation_checked": True}
        if state in ("revoked", "suspended"):
            return {
                "valid": False,
                "payload": verified["payload"],
                "reason": state,
                "error": message,
                "revocation_checked": True,
            }
        return {
            "valid": False,
            "payload": verified["payload"],
            "reason": "status_unavailable",
            "error": message,
            "revocation_checked": False,
        }

    def refresh_jwks(self) -> None:
        """Make the next verification refetch the key set, and drop the cached status list.

        The refetch ignores the key set's 10-minute reuse window and the 30-second cooldowns, and a
        successful one resets the set's age — the remedy a ``jwks_stale`` answer names. What the
        verifier knows is kept: key confirmations and tombstones survive (``clear_tombstones()`` is
        the separate, deliberate reset).
        """
        self._key_set.force_refresh()
        self._status_list_cache = None

    def clear_tombstones(self) -> None:
        """Forget every revoked-key tombstone this client has applied or is waiting to confirm.

        They are held in memory only — a restart forgets them too — and otherwise kept until a year
        after the revocation, whatever later key sets say.
        """
        self._key_set.clear_tombstones()

    async def _verify_against_key_set(
        self, token: str, family: str, *, issuer: str | None, require_exp: bool
    ) -> dict[str, Any]:
        """The signature against the issuer's key set, then the window and lifetime of the key that
        made it, then the token's own claims — so a forgery reads as a bad signature, never as a
        policy violation of a key it did not come from, and a policy violation outranks an expired
        token.
        """
        import jwt

        try:
            header = _decode_segment(token, 0)
        except ValueError as e:
            return {"ok": False, "reason": "invalid", "message": str(e)}
        alg = header.get("alg")
        # Chosen from the allow-list, never trusted from the header: ``none`` and HMAC die here.
        if not is_supported_algorithm(alg):
            return {"ok": False, "reason": "invalid", "message": f"token algorithm {alg!r} is not accepted"}
        kid = header.get("kid") if isinstance(header.get("kid"), str) else None

        resolution = await self._key_set.resolve(kid, alg, family)
        if isinstance(resolution, Unavailable):
            return {"ok": False, "reason": "status_unavailable", "message": resolution.message}
        if isinstance(resolution, Stale):
            return {
                "ok": False,
                "reason": "jwks_stale",
                "message": (
                    "the issuer key set could not be refreshed and the cached copy is older than "
                    "max_jwks_age; call refresh_jwks() once the issuer is reachable"
                ),
                "cache_age_seconds": resolution.cache_age_seconds,
            }
        if isinstance(resolution, Revoked):
            return {"ok": False, "reason": "key_revoked", "message": f'the issuer revoked signing key "{resolution.kid}"'}
        if isinstance(resolution, WrongPurpose):
            return {
                "ok": False,
                "reason": "wrong_key_purpose",
                "message": f'signing key "{resolution.kid}" is not a {family} key',
            }
        if isinstance(resolution, Unknown) or not isinstance(resolution, Keys):
            return {"ok": False, "reason": "unknown_key", "message": "no key in the issuer key set matches this token"}

        matched: KeyCandidate | None = None
        for candidate in resolution.candidates:
            try:
                jwt.PyJWS().decode(token, candidate.key, algorithms=[alg])
            except Exception:
                # Not this key; a token matching none of them is a bad signature.
                continue
            matched = candidate
            break
        if matched is None:
            return {"ok": False, "reason": "invalid", "message": "signature verification failed"}

        try:
            payload = _decode_segment(token, 1)
        except ValueError as e:
            return {"ok": False, "reason": "invalid", "message": str(e)}
        violation = check_key_policy(matched.record, payload.get("iat"), payload.get("exp"), resolution.registry_live)
        if violation == "outside_key_window":
            return {"ok": False, "reason": violation, "message": "token iat lies outside the signing key's window"}
        if violation == "token_lifetime_exceeded":
            return {
                "ok": False,
                "reason": violation,
                "message": "token exp lies beyond iat plus the signing key's max_token_lifetime",
            }

        claims_failure = _claims_failure(
            payload, issuer=issuer, require_exp=require_exp, reject_audience=issuer is not None
        )
        if claims_failure is not None:
            return {"ok": False, "reason": claims_failure[0], "message": claims_failure[1]}
        return {"ok": True, "payload": payload}

    async def _check_status_list(self, claim: dict[str, Any]) -> tuple[str, str]:
        """Resolve one token's slot against the issuer's signed status list."""
        uri = claim["uri"]

        # The uri arrives INSIDE the artifact being verified, so fetching whatever it names would
        # hand a forged token both the status authority and a request from your network. Only the
        # origin this client is configured against is honoured.
        try:
            uri_origin = _origin(uri)
        except ValueError:
            # `urlsplit(...).port` raises for a port outside 0-65535 and `urlsplit` itself for a
            # malformed IPv6 literal. The other three SDKs answer rather than raise here, and an
            # unparseable uri is exactly a case to fail closed on.
            return "unavailable", "status list uri is not a valid absolute URL"

        configured_origin = _origin(self._http.base_url)
        if uri_origin != configured_origin:
            return (
                "unavailable",
                f"status list uri origin {uri_origin} is not the configured issuer origin "
                f"{configured_origin}",
            )

        loaded = await self._load_status_list(uri)
        if isinstance(loaded, str):
            return "unavailable", loaded

        data, bits = loaded
        slot = _read_status_slot(data, claim["idx"], bits)
        if slot is None:
            return "unavailable", f"status list has no slot {claim['idx']}"
        if slot == _SLOT_REVOKED:
            return "revoked", "This proof has been revoked"
        if slot == _SLOT_SUSPENDED:
            return "suspended", "This proof is currently suspended"
        if slot == _SLOT_VALID:
            return "valid", ""
        # 0b11 is reserved for application-specific use by the draft; the issuer packs it when it
        # could not resolve a delegation's control proof. It is an absence of an answer.
        return "unavailable", f"status list slot carries unknown status {slot}"

    async def _load_status_list(self, uri: str) -> tuple[bytes, int] | str:
        """The decompressed list and its bit width, or a message saying why it is unavailable."""
        cached = self._status_list_cache
        if cached and cached["uri"] == uri and cached["expires_at"] > now_wall_seconds():
            return cached["data"], cached["bits"]

        try:
            status, headers, body = await self._http.fetch_public(
                uri,
                timeout=STATUS_LIST_TIMEOUT_SECONDS,
                headers={"accept": "application/statuslist+jwt, application/jwt, text/plain"},
                max_bytes=MAX_STATUS_LIST_BYTES,
            )
        except Exception as e:
            return f"status list fetch failed: {e}"

        if status != 200:
            return f"status list fetch failed with HTTP {status}"

        declared_length = headers.get("content-length")
        if declared_length and declared_length.isdigit() and int(declared_length) > MAX_STATUS_LIST_BYTES:
            return "status list response is too large"

        list_token = body.decode("utf-8", errors="replace").strip()
        if len(body) > MAX_STATUS_LIST_BYTES:
            return "status list response is too large"

        try:
            header = _decode_segment(list_token, 0)
        except ValueError as e:
            return f"status list is not a JWT: {e}"

        # The draft mandates this `typ`, and it is the one header that separates a status list
        # from every other JWT the issuer signs.
        if header.get("typ") != "statuslist+jwt":
            return f"status list must carry typ statuslist+jwt, got {header.get('typ')!r}"

        # Held to its own key family (`status-list`) and that key's window. `exp` is REQUIRED: a
        # freshness channel without one would be honoured forever. `iss` is deliberately NOT
        # required — the issuer does not put one in the list.
        try:
            checked = await self._verify_against_key_set(list_token, "status-list", issuer=None, require_exp=True)
        except Exception as e:
            return f"status list did not verify: {e}"
        if not checked["ok"]:
            return f"status list did not verify: {checked['message']}"
        payload = checked["payload"]

        # The list must say it is the list we asked for, or a valid list from the same issuer
        # could be replayed in place of another one.
        if payload.get("sub") != uri:
            return "status list `sub` does not match the uri it was fetched from"

        status_list = payload.get("status_list")
        if not isinstance(status_list, dict) or not isinstance(status_list.get("lst"), str):
            return "status list payload has no `lst`"
        bits = status_list.get("bits") if isinstance(status_list.get("bits"), int) else 2

        try:
            data = zlib.decompress(_b64url_decode(status_list["lst"]))
        except Exception as e:
            return f"status list payload could not be decompressed: {e}"

        # Honour the shorter of the issuer's published `ttl` and the token's own `exp`.
        exp = payload.get("exp") if isinstance(payload.get("exp"), int) else 0
        ttl = payload.get("ttl") if isinstance(payload.get("ttl"), int) else 0
        expires_at = min(exp, now_wall_seconds() + ttl) if ttl > 0 else exp
        self._status_list_cache = {"uri": uri, "data": data, "bits": bits, "expires_at": expires_at}

        return data, bits
