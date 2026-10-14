"""Offline verification reads the token's status list (h-sdk-offline-revocation).

Before this task ``verify_offline`` checked the signature, ``iss`` and ``exp`` and stopped, so a
REVOKED proof verified as valid — measured against production on 2026-09-20. These cases pin that
the token's status-list slot is now read, that an unreadable list fails closed, and that a token
carrying no slot at all stays valid, which is what the issuer's own ``POST /proofs/validate``
answers for it.

The suite runs against a real loopback HTTP server rather than a mock transport, so the key set and
the list travel over a real socket through the SDK's own credential-free client.

The packed list comes from ``sdks/shared/fixtures/status_list_slots.json``, the same fixture the
issuer's drift suite and the other three SDKs read.

Which status-list origins may be fetched comes from ``sdks/shared/fixtures/status_list_origin.json``,
shared with the other three SDKs and ``delegation-verifier``. Those cases need a fixed https origin,
a default port and an uppercase host, none of which a loopback server can be, so they run through
an ``httpx.MockTransport`` on the credential-free client instead.
"""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec

from proof_sdk.http import HttpClient
from proof_sdk.resources.proofs import Proofs
from proof_sdk.version import VERSION

FIXTURE = json.loads(
    (Path(__file__).resolve().parents[2] / "shared" / "fixtures" / "status_list_slots.json").read_text()
)
ORIGIN_FIXTURE = json.loads(
    (Path(__file__).resolve().parents[2] / "shared" / "fixtures" / "status_list_origin.json").read_text()
)

KID = "test-key-1"

_private_key = ec.generate_private_key(ec.SECP256R1())
_foreign_key = ec.generate_private_key(ec.SECP256R1())


def _jwks() -> dict[str, Any]:
    jwk = json.loads(jwt.algorithms.ECAlgorithm.to_jwk(_private_key.public_key()))
    jwk.update({"kid": KID, "alg": "ES256", "use": "sig"})
    return {"keys": [jwk]}


class _State:
    """What the status-list route answers for the case currently running."""

    reply: str = "token"
    overrides: dict[str, Any] = {}
    status_list_url: str = ""
    status_list_requests: int = 0
    jwks_reply: str = "keys"
    captured_jwks_user_agent: str | None = None


STATE = _State()


def _mint_proof(
    *,
    status_list: dict[str, Any] | None = ...,  # type: ignore[assignment]
    key: Any = None,
    issuer: str = "proof.holdings",
    extra: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(tz=timezone.utc)
    claims: dict[str, Any] = {
        "iss": issuer,
        "sub": "ph_ctl_0123456789abcdef0123456789abcdef",
        "iat": now,
        "exp": now + timedelta(hours=1),
        "type": "phone",
        "channel": "whatsapp",
        "identifier_hash": "abc123",
        "verified_at": now.isoformat(),
        "user_id": "usr_1",
    }
    if status_list is not ...:
        if status_list is not None:
            claims["status"] = {"status_list": status_list}
    else:
        claims["status"] = {"status_list": {"idx": 1, "uri": STATE.status_list_url}}

    claims.update(extra or {})
    return jwt.encode(claims, key or _private_key, algorithm="ES256", headers={"kid": KID})


def _mint_status_list(overrides: dict[str, Any] | None = None) -> str:
    overrides = overrides or {}
    now = datetime.now(tz=timezone.utc)
    claims: dict[str, Any] = {
        "sub": overrides.get("sub", STATE.status_list_url),
        "iat": now,
        "ttl": 55,
        "status_list": {"bits": FIXTURE["bits"], "lst": FIXTURE["lst"]},
    }
    if not overrides.get("omit_exp"):
        claims["exp"] = now + timedelta(seconds=overrides.get("expires_in", 300))

    headers = {"kid": KID, "typ": overrides.get("typ", "statuslist+jwt")}
    return jwt.encode(claims, overrides.get("key") or _private_key, algorithm="ES256", headers=headers)


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 — BaseHTTPRequestHandler's own naming
        if self.path == "/.well-known/jwks.json":
            STATE.captured_jwks_user_agent = self.headers.get("User-Agent")
            if STATE.jwks_reply == "error":
                self.send_response(503)
                self.send_header("content-length", "0")
                self.end_headers()
                return
            body = json.dumps(_jwks()).encode()
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/api/v1/proofs/status-list":
            STATE.status_list_requests += 1
            if STATE.reply == "hangup":
                self.close_connection = True
                self.connection.close()
                return
            if STATE.reply == "error":
                self.send_response(503)
                self.send_header("content-length", "0")
                self.end_headers()
                return
            declare_length = True
            if STATE.reply in ("oversized", "oversized_undeclared"):
                body = b"x" * (600 * 1024)
                # The declared-length check and the read-length ceiling are two separate guards;
                # a fixture that trips both pins neither on its own.
                declare_length = STATE.reply == "oversized"
            else:
                body = _mint_status_list(STATE.overrides).encode()

            self.send_response(200)
            self.send_header("content-type", "application/statuslist+jwt")
            if declare_length:
                self.send_header("content-length", str(len(body)))
            else:
                self.close_connection = True
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.send_header("content-length", "0")
        self.end_headers()

    def log_message(self, *args: Any) -> None:  # keep the test output readable
        return


@pytest.fixture(scope="module", autouse=True)
def server() -> Iterator[str]:
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{httpd.server_address[1]}"
    STATE.status_list_url = f"{base_url}/api/v1/proofs/status-list"
    try:
        yield base_url
    finally:
        httpd.shutdown()
        httpd.server_close()


@pytest.fixture(autouse=True)
def reset_state() -> Iterator[None]:
    STATE.reply = "token"
    STATE.overrides = {}
    STATE.status_list_requests = 0
    STATE.jwks_reply = "keys"
    STATE.captured_jwks_user_agent = None
    yield


def _proofs(base_url: str) -> Proofs:
    """A fresh resource per case — the key-set and status-list caches live on it."""
    http = HttpClient(api_key="pk_test_123", base_url=base_url, timeout=5.0, max_retries=0)
    return Proofs(http)


class TestRevocationCheckedByDefault:
    async def test_refuses_a_revoked_slot(self, server: str) -> None:
        result = await _proofs(server).verify_offline(
            _mint_proof(status_list={"idx": 1, "uri": STATE.status_list_url})
        )

        assert result["valid"] is False
        assert result["reason"] == "revoked"
        assert result["revocation_checked"] is True

    async def test_refuses_a_suspended_slot(self, server: str) -> None:
        result = await _proofs(server).verify_offline(
            _mint_proof(status_list={"idx": 2, "uri": STATE.status_list_url})
        )

        assert result["valid"] is False
        assert result["reason"] == "suspended"
        assert result["revocation_checked"] is True

    async def test_accepts_a_clear_slot(self, server: str) -> None:
        result = await _proofs(server).verify_offline(
            _mint_proof(status_list={"idx": 0, "uri": STATE.status_list_url})
        )

        assert result.get("error") is None
        assert result["valid"] is True
        assert result["revocation_checked"] is True
        assert result["payload"]["user_id"] == "usr_1"

    async def test_jwks_request_carries_the_sdk_user_agent(self, server: str) -> None:
        """The prod edge 520s a library-default UA (A1) — the key-set fetch must not send one."""
        await _proofs(server).verify_offline(
            _mint_proof(status_list={"idx": 0, "uri": STATE.status_list_url})
        )

        assert STATE.captured_jwks_user_agent == f"proof-sdk-python/{VERSION}"

    async def test_refuses_the_application_reserved_value(self, server: str) -> None:
        result = await _proofs(server).verify_offline(
            _mint_proof(status_list={"idx": 3, "uri": STATE.status_list_url})
        )

        assert result["valid"] is False
        assert result["reason"] == "status_unavailable"
        assert result["revocation_checked"] is False

    async def test_refuses_a_slot_beyond_the_list(self, server: str) -> None:
        result = await _proofs(server).verify_offline(
            _mint_proof(
                status_list={"idx": FIXTURE["beyond_end_index"], "uri": STATE.status_list_url}
            )
        )

        assert result["valid"] is False
        assert result["reason"] == "status_unavailable"


class TestTokenWithNoSlot:
    async def test_stays_valid_and_says_revocation_was_not_checked(self, server: str) -> None:
        result = await _proofs(server).verify_offline(_mint_proof(status_list=None))

        # The issuer answers valid:true for a token it cannot resolve in the registry
        # (src/controllers/proofs.ts) — a client refusing it would be stricter than the server.
        assert result["valid"] is True
        assert result["revocation_checked"] is False
        assert result.get("reason") is None


class TestUnreadableListFailsClosed:
    async def test_connection_dropped(self, server: str) -> None:
        STATE.reply = "hangup"

        result = await _proofs(server).verify_offline(_mint_proof())

        assert result["valid"] is False
        assert result["reason"] == "status_unavailable"
        assert result["revocation_checked"] is False

    async def test_http_error(self, server: str) -> None:
        STATE.reply = "error"

        assert (await _proofs(server).verify_offline(_mint_proof()))["reason"] == "status_unavailable"

    async def test_oversized_body(self, server: str) -> None:
        STATE.reply = "oversized"

        # The MESSAGE is asserted, not just the reason: a 600 KiB run of "x" also fails to parse
        # as a JWT, so the reason alone stays green with the size ceiling deleted.
        result = await _proofs(server).verify_offline(_mint_proof())
        assert result["reason"] == "status_unavailable"
        assert "too large" in result["error"]

    async def test_foreign_origin_is_never_contacted(self, server: str) -> None:
        token = _mint_proof(
            status_list={"idx": 1, "uri": "https://evil.example.net/api/v1/proofs/status-list"}
        )

        proofs = _proofs(server)
        # Every public read — the key set and the status list alike — goes through `fetch_public`,
        # so recording its urls is recording every request the verification made.
        requested: list[str] = []
        real_fetch_public = proofs._http.fetch_public

        async def recording_fetch_public(url: str, **kwargs: Any) -> Any:
            requested.append(url)
            return await real_fetch_public(url, **kwargs)

        proofs._http.fetch_public = recording_fetch_public  # type: ignore[method-assign]
        result = await proofs.verify_offline(token)

        assert result["valid"] is False
        assert result["reason"] == "status_unavailable"
        # An unreachable host would answer status_unavailable too, so the claim under test is
        # that the foreign origin was never contacted. Positive control: the recorder did see the
        # one request this verification legitimately makes, the issuer's own key set.
        assert requested == [f"{server}/.well-known/jwks.json"]
        assert "origin" in result["error"]


class TestWhatMakesAListAcceptable:
    async def test_refuses_a_list_without_the_status_list_typ(self, server: str) -> None:
        STATE.overrides = {"typ": "JWT"}

        assert (await _proofs(server).verify_offline(_mint_proof()))["reason"] == "status_unavailable"

    async def test_refuses_a_list_whose_sub_is_another_uri(self, server: str) -> None:
        STATE.overrides = {"sub": "https://api.example.com/other-list"}

        assert (await _proofs(server).verify_offline(_mint_proof()))["reason"] == "status_unavailable"

    async def test_refuses_an_expired_list(self, server: str) -> None:
        STATE.overrides = {"expires_in": -3600}

        assert (await _proofs(server).verify_offline(_mint_proof()))["reason"] == "status_unavailable"

    async def test_refuses_a_list_with_no_exp(self, server: str) -> None:
        STATE.overrides = {"omit_exp": True}

        assert (await _proofs(server).verify_offline(_mint_proof()))["reason"] == "status_unavailable"

    async def test_refuses_a_list_signed_by_an_unpublished_key(self, server: str) -> None:
        STATE.overrides = {"key": _foreign_key}

        assert (await _proofs(server).verify_offline(_mint_proof()))["reason"] == "status_unavailable"

    async def test_accepts_a_list_carrying_no_iss(self, server: str) -> None:
        # The issuer signs its list without an `iss` claim (src/services/statusList.ts), so
        # requiring one would refuse every real list.
        result = await _proofs(server).verify_offline(
            _mint_proof(status_list={"idx": 0, "uri": STATE.status_list_url})
        )

        assert result["valid"] is True
        assert result["revocation_checked"] is True


class TestOptOut:
    async def test_signature_only_on_request(self, server: str) -> None:
        revoked = _mint_proof(status_list={"idx": 1, "uri": STATE.status_list_url})

        result = await _proofs(server).verify_offline(revoked, check_revocation=False)

        assert result["valid"] is True
        assert result["revocation_checked"] is False


class TestSignatureFailures:
    async def test_foreign_signing_key(self, server: str) -> None:
        result = await _proofs(server).verify_offline(_mint_proof(key=_foreign_key))

        assert result["valid"] is False
        assert result["reason"] == "invalid"
        assert result["revocation_checked"] is False

    async def test_a_token_addressed_to_an_audience_is_refused(self, server: str) -> None:
        """PyJWT refused a non-empty ``aud`` when no audience was asked for; the SDK's own claim checks keep that."""
        refused = await _proofs(server).verify_offline(
            _mint_proof(status_list=None, extra={"aud": "someone-else"})
        )
        assert refused["valid"] is False
        assert refused["reason"] == "invalid"
        assert refused["error"] == "Invalid audience"
        # Positive controls: the same token without `aud`, or with an empty one — which PyJWT let
        # through as naming nobody — verifies.
        assert (await _proofs(server).verify_offline(_mint_proof(status_list=None)))["valid"] is True
        for empty in ("", [], None):
            accepted = await _proofs(server).verify_offline(_mint_proof(status_list=None, extra={"aud": empty}))
            assert accepted["valid"] is True, empty

    @pytest.mark.parametrize(
        "claims",
        [
            {"exp": None},
            {"iat": None},
            {"nbf": None},
            {"exp": float("nan")},
            {"exp": float("inf")},
            {"iat": float("nan")},
            {"nbf": float("nan")},
            {"sub": 5},
            {"jti": 5},
        ],
        ids=[
            "exp-null", "iat-null", "nbf-null", "exp-nan", "exp-infinity", "iat-nan", "nbf-nan",
            "sub-number", "jti-number",
        ],
    )
    async def test_a_malformed_registered_claim_is_refused(self, server: str, claims: dict[str, Any]) -> None:
        """What ``jwt.decode`` refused before the SDK checked claims on its own clock, it still refuses."""
        result = await _proofs(server).verify_offline(_mint_proof(status_list=None, extra=claims))
        assert result["valid"] is False
        assert result["reason"] == "invalid"

    async def test_foreign_issuer(self, server: str) -> None:
        result = await _proofs(server).verify_offline(_mint_proof(issuer="evil.example.net"))

        assert result["valid"] is False
        assert result["reason"] == "invalid"


class TestSharedSlotFixture:
    async def test_reads_every_named_slot(self, server: str) -> None:
        expected = {
            "valid": (True, None),
            "revoked": (False, "revoked"),
            "suspended": (False, "suspended"),
            "unavailable": (False, "status_unavailable"),
        }

        for index, name in FIXTURE["slots"].items():
            result = await _proofs(server).verify_offline(
                _mint_proof(status_list={"idx": int(index), "uri": STATE.status_list_url})
            )

            assert (index, result["valid"], result.get("reason")) == (index, *expected[name])


class TestTheCaches:
    async def test_status_list_is_read_once_across_two_verifications(self, server: str) -> None:
        proofs = _proofs(server)

        await proofs.verify_offline(_mint_proof(status_list={"idx": 0, "uri": STATE.status_list_url}))
        await proofs.verify_offline(_mint_proof(status_list={"idx": 1, "uri": STATE.status_list_url}))

        assert STATE.status_list_requests == 1

    async def test_status_list_is_reread_once_its_window_passes(self, server: str) -> None:
        # That window is what keeps the product's 60-second revocation-visibility promise on the
        # client side: past it the list must be re-read, or a revocation stays invisible for as
        # long as the proof itself lives.
        proofs = _proofs(server)
        await proofs.verify_offline(_mint_proof(status_list={"idx": 0, "uri": STATE.status_list_url}))

        assert proofs._status_list_cache["expires_at"] > time.time()
        proofs._status_list_cache["expires_at"] = time.time() - 1

        await proofs.verify_offline(_mint_proof(status_list={"idx": 0, "uri": STATE.status_list_url}))

        assert STATE.status_list_requests == 2

    async def test_refresh_jwks_drops_the_status_list_too(self, server: str) -> None:
        proofs = _proofs(server)
        await proofs.verify_offline(_mint_proof(status_list={"idx": 0, "uri": STATE.status_list_url}))

        proofs.refresh_jwks()
        await proofs.verify_offline(_mint_proof(status_list={"idx": 0, "uri": STATE.status_list_url}))

        assert STATE.status_list_requests == 2


class TestTheRemainingCeilingHalfAndTheOriginRule:
    async def test_oversized_body_without_content_length(self, server: str) -> None:
        STATE.reply = "oversized_undeclared"

        result = await _proofs(server).verify_offline(_mint_proof())

        assert result["reason"] == "status_unavailable"
        assert "too large" in result["error"]

    async def test_default_port_and_host_case_are_the_same_origin(self, server: str) -> None:
        # One rule across the four SDKs: host compared case-insensitively, an explicit default
        # port the same origin as none. Asserted on `_origin` directly because this server runs
        # on a loopback address and a non-default port, which can express neither spelling.
        from proof_sdk.resources.proofs import _origin

        assert _origin("https://API.Proof.Holdings/x") == _origin("https://api.proof.holdings/y")
        assert _origin("https://api.proof.holdings:443/x") == _origin("https://api.proof.holdings/y")
        assert _origin("http://api.proof.holdings:80/x") == _origin("http://api.proof.holdings/y")
        assert _origin("https://api.proof.holdings:8443/x") != _origin("https://api.proof.holdings/y")


class TestAnUnreadableKeySet:
    async def test_is_not_reported_as_a_forgery(self, server: str) -> None:
        STATE.jwks_reply = "error"

        result = await _proofs(server).verify_offline(_mint_proof())

        # `invalid` is a forged signature's answer; an outage at the key set is "I could not
        # check", and the two must stay distinguishable to a caller deciding what to do next.
        assert result["valid"] is False
        assert result["reason"] == "status_unavailable"
        assert result["revocation_checked"] is False


class TestAnUnparseableStatusListUri:
    @pytest.mark.parametrize(
        "uri",
        [
            "https://api.proof.holdings:99999/api/v1/proofs/status-list",
            "https://[::1/api/v1/proofs/status-list",
        ],
    )
    async def test_answers_instead_of_raising(self, server: str, uri: str) -> None:
        # `urlsplit(...).port` raises for a port outside 0-65535 and `urlsplit` itself for a
        # malformed IPv6 literal. This SDK was the only one of the four that let that escape
        # `verify_offline` as a ValueError instead of failing closed.
        result = await _proofs(server).verify_offline(
            _mint_proof(status_list={"idx": 1, "uri": uri})
        )

        assert result["valid"] is False
        assert result["reason"] == "status_unavailable"


class TestSharedStatusListOriginFixture:
    @staticmethod
    def _proofs_with_routed_transport() -> tuple[Proofs, list[str]]:
        """A client configured against the fixture's origin, whose public reads serve only the key set."""
        configured = ORIGIN_FIXTURE["configured_origin"]
        jwks_url = f"{configured}/.well-known/jwks.json"
        requested: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requested.append(str(request.url))
            if str(request.url) == jwks_url:
                return httpx.Response(200, json=_jwks())
            return httpx.Response(404, text="not found")

        http = HttpClient(api_key="pk_test_123", base_url=configured, timeout=5.0, max_retries=0)
        http._public_client = httpx.AsyncClient(
            transport=httpx.MockTransport(handler),
            follow_redirects=False,
            headers={"User-Agent": f"proof-sdk-python/{VERSION}"},
        )
        return Proofs(http), requested

    @pytest.mark.parametrize("case", ORIGIN_FIXTURE["cases"], ids=lambda case: case["name"])
    async def test_the_status_list_origin_rule(self, case: dict[str, Any]) -> None:
        configured = ORIGIN_FIXTURE["configured_origin"]
        proofs, requested = self._proofs_with_routed_transport()
        list_path = httpx.URL(case["uri"]).path

        result = await proofs.verify_offline(_mint_proof(status_list={"idx": 1, "uri": case["uri"]}))
        list_requests = [url for url in requested if httpx.URL(url).path == list_path]

        # The key set was read and the signature passed, so the origin rule decided the rest.
        assert f"{configured}/.well-known/jwks.json" in requested
        assert result["payload"] is not None
        assert result["valid"] is False
        assert result["reason"] == "status_unavailable"
        assert result["revocation_checked"] is False

        if case["sdk"] == "accepted":
            # The list itself is a 404 here: what is pinned is that the origin rule let the request go.
            assert len(list_requests) == 1
            assert list_requests[0].startswith(f"{configured}/")
            assert "configured issuer origin" not in result["error"]
        else:
            assert list_requests == []
            assert result["error"] == (
                f"status list uri origin {case['uri_origin']} is not the configured issuer origin {configured}"
            )
