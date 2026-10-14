"""Offline verification follows the issuer's key-rotation rules (h-verifier-jwks-js-python).

The shared cases in ``sdks/shared/fixtures/jwks_rotation/rotation_cases.json`` run here through the
PUBLIC surface — ``Proof(...)``, ``proofs.verify_offline``, ``refresh_jwks``, ``clear_tombstones`` —
with the SDK's own credential-free client routed to the case's documents by an ``httpx`` mock
transport. The same file drives ``delegation-verifier`` and the other SDKs, so a rule read
differently here fails here. Step semantics: the README beside the file.

Two fixture names map onto this SDK's own vocabulary, which predates them: ``bad_signature`` is
``invalid`` (pinned further by its message, so an ``iss`` failure cannot pass for it) and
``jwks_unavailable`` is ``status_unavailable`` — "could not check".

The cases move both clocks together, so they cannot tell them apart; the clock-base tests below set
them apart on purpose.
"""

from __future__ import annotations

import asyncio
import base64
import json
import re
from pathlib import Path
from typing import Any

import httpx
import pytest

import proof_sdk.http
from proof_sdk import Proof
from proof_sdk.jwks.key_set_cache import set_jwks_clock_for_tests, set_jwks_event_listener_for_tests

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads(
    (ROOT.parent / "shared" / "fixtures" / "jwks_rotation" / "rotation_cases.json").read_text()
)
CONTEXT = FIXTURE["context"]
T0 = CONTEXT["t0"]
MIN = 60
HOUR = 3600

#: Token families ``verify_offline`` checks; this SDK has no key-set persistence.
FAMILIES = {"proof", "delegation", "status-list"}
CAPABILITIES: set[str] = set()

RUNNABLE = [
    case
    for case in FIXTURE["cases"]
    if set(case["families"]) <= FAMILIES and set(case.get("requires", [])) <= CAPABILITIES
]


def _outcome(result: dict[str, Any]) -> str:
    """The fixture's name for an SDK answer."""
    if result["valid"]:
        return "valid"
    reason = result.get("reason")
    if reason == "invalid":
        return "bad_signature"
    if reason == "status_unavailable":
        return "jwks_unavailable"
    return reason or "missing reason"


class _Clock:
    def __init__(self) -> None:
        self.monotonic_seconds = 0.0
        self.wall_seconds = 0.0

    def set(self, monotonic_seconds: float, wall_seconds: float) -> None:
        self.monotonic_seconds = monotonic_seconds
        self.wall_seconds = wall_seconds

    def monotonic_ms(self) -> float:
        return self.monotonic_seconds * 1000

    def wall_ms(self) -> float:
        return self.wall_seconds * 1000


class _Issuer:
    """What the issuer's two public documents answer, and how often the key set was asked for."""

    def __init__(self) -> None:
        self.jwks: str | None = None
        self.status_list: str | None = None
        self.jwks_fetches = 0

    def serve(self, step: dict[str, Any]) -> None:
        self.jwks = step.get("jwks")
        self.status_list = step.get("status_list")

    def handle(self, request: httpx.Request) -> httpx.Response:
        # The key set is a public document: no credential, the branded User-Agent.
        assert "authorization" not in request.headers
        assert request.headers.get("user-agent", "").startswith("proof-sdk-python/")
        url = str(request.url)
        if url == CONTEXT["jwks_uri"]:
            self.jwks_fetches += 1
            if self.jwks is None:
                return httpx.Response(503, text="unavailable")
            return httpx.Response(200, json=FIXTURE["documents"][self.jwks])
        if url == CONTEXT["status_list_uri"]:
            if not self.status_list:
                return httpx.Response(404, text="not found")
            return httpx.Response(200, text=FIXTURE["status_lists"][self.status_list]["jwt"])
        raise AssertionError(f"unexpected fetch: {url}")


@pytest.fixture
def clock() -> Any:
    replacement = _Clock()
    set_jwks_clock_for_tests(replacement)
    yield replacement
    set_jwks_clock_for_tests(None)


@pytest.fixture
def events() -> Any:
    seen: list[str] = []
    set_jwks_event_listener_for_tests(lambda event: seen.append(event.type))
    yield seen
    set_jwks_event_listener_for_tests(None)


@pytest.fixture
def issuer(monkeypatch: pytest.MonkeyPatch) -> _Issuer:
    """Route the SDK's own httpx clients to the fixture, keeping every other setting they are built with."""
    routed = _Issuer()
    real_client = httpx.AsyncClient

    def client_with_routed_transport(*args: Any, **kwargs: Any) -> httpx.AsyncClient:
        assert kwargs.get("follow_redirects") is False
        kwargs["transport"] = httpx.MockTransport(routed.handle)
        return real_client(*args, **kwargs)

    monkeypatch.setattr(proof_sdk.http.httpx, "AsyncClient", client_with_routed_transport)
    return routed


def _client(**kwargs: Any) -> Proof:
    return Proof("pk_test_fixture", base_url=CONTEXT["issuer_origin"], **kwargs)


def _token(name: str) -> str:
    return FIXTURE["tokens"][name]["jwt"]


def test_runs_a_meaningful_share_of_the_shared_cases() -> None:
    """A filter that skips everything must not pass."""
    names = [case["name"] for case in RUNNABLE]
    assert len(names) >= 30
    for expected in (
        "unknown_status_list_kid",
        "tombstone_proof_pull_hint",
        "clear_tombstones_lifts_applied_tombstone",
        "tolerant_mode",
        "max_jwks_age_refetch_failure_over_bound",
    ):
        assert expected in names
    assert [case["name"] for case in FIXTURE["cases"] if case not in RUNNABLE] == ["tombstone_persists_across_reload"]


@pytest.mark.parametrize("case", RUNNABLE, ids=[case["name"] for case in RUNNABLE])
async def test_shared_rotation_case(case: dict[str, Any], clock: _Clock, events: list[str], issuer: _Issuer) -> None:
    max_jwks_age = case.get("max_jwks_age_seconds", CONTEXT["default_max_jwks_age_seconds"])
    proof = _client(max_jwks_age=max_jwks_age)
    try:
        for step in case["steps"]:
            clock.set(step["at"], step["at"])
            issuer.serve(step)
            issuer.jwks_fetches = 0
            events.clear()
            where = f"{case['name']} @ t0{step['at'] - T0:+d}s"

            action = step.get("action")
            if action == "refresh":
                proof.proofs.refresh_jwks()
            elif action == "clear_tombstones":
                proof.proofs.clear_tombstones()
            elif action is not None:
                raise AssertionError(f"{where}: unsupported action {action}")

            expected = step["expect"]
            if "verify" in step:
                result = await proof.proofs.verify_offline(
                    _token(step["verify"]), check_revocation=step.get("status_check") is True
                )
                assert _outcome(result) == expected["result"], f"{where}: {result.get('error')}"
                if expected["result"] == "bad_signature":
                    assert result["error"] == "signature verification failed", where
                if "pull_hint_handle" in expected:
                    assert result.get("pull_hint") == {
                        "issuer_origin": CONTEXT["issuer_origin"],
                        "handle": expected["pull_hint_handle"],
                    }, where
                if "cache_age_seconds" in expected:
                    assert result.get("cache_age_seconds") == expected["cache_age_seconds"], where

            assert issuer.jwks_fetches == expected["fetches"], f"{where}: JWKS fetches"
            for event_type in expected.get("events", []):
                assert event_type in events, f"{where}: events {events}"
            if "vanished_kids" in expected:
                assert proof.proofs._key_set.diagnostics()["vanished_kids"] == expected["vanished_kids"], where
    finally:
        await proof.close()


class TestClockBases:
    """h-verifier-jwks-js-python SC-8: the two clocks on different bases."""

    async def test_reuses_the_key_set_on_the_monotonic_clock(self, clock: _Clock, issuer: _Issuer) -> None:
        proof = _client()
        issuer.serve({"jwks": "registry_v1"})
        clock.set(T0, T0)
        assert (await proof.proofs.verify_offline(_token("dlg_active")))["valid"] is True
        clock.set(T0 + MIN, T0 + 11 * MIN)
        assert (await proof.proofs.verify_offline(_token("dlg_active")))["valid"] is True
        assert issuer.jwks_fetches == 1
        clock.set(T0 + 11 * MIN, T0 + 11 * MIN)
        assert (await proof.proofs.verify_offline(_token("dlg_active")))["valid"] is True
        assert issuer.jwks_fetches == 2
        await proof.close()

    async def test_measures_staleness_on_the_monotonic_clock(self, clock: _Clock, issuer: _Issuer) -> None:
        proof = _client()
        issuer.serve({"jwks": "registry_v1"})
        clock.set(T0, T0)
        await proof.proofs.verify_offline(_token("dlg_active"))
        issuer.serve({"jwks": None})
        clock.set(T0 + 25 * HOUR, T0 + HOUR)
        result = await proof.proofs.verify_offline(_token("dlg_active"))
        assert result["reason"] == "jwks_stale"
        assert result["cache_age_seconds"] == 25 * HOUR
        await proof.close()

    async def test_spaces_a_tombstone_confirmation_on_the_monotonic_clock(self, clock: _Clock, issuer: _Issuer) -> None:
        async def confirmed_then_tombstoned(monotonic: int, wall: int) -> dict[str, Any]:
            proof = _client()
            issuer.serve({"jwks": "registry_v1"})
            for at in (T0 - 11 * MIN, T0):
                clock.set(at, at)
                await proof.proofs.verify_offline(_token("dlg_retired"))
            issuer.serve({"jwks": "registry_tombstone_retired_delegation"})
            clock.set(T0 + 11 * MIN, T0 + 11 * MIN)
            await proof.proofs.verify_offline(_token("dlg_retired"))
            clock.set(monotonic, wall)
            proof.proofs.refresh_jwks()
            result = await proof.proofs.verify_offline(_token("dlg_retired"))
            await proof.close()
            return result

        assert (await confirmed_then_tombstoned(T0 + 17 * MIN, T0 + 12 * MIN))["reason"] == "key_revoked"
        assert (await confirmed_then_tombstoned(T0 + 12 * MIN, T0 + 17 * MIN))["valid"] is True

    async def test_checks_exp_against_the_wall_clock(self, clock: _Clock, issuer: _Issuer) -> None:
        proof = _client()
        issuer.serve({"jwks": "registry_v1"})
        clock.set(T0, T0 + 40 * 86_400)
        result = await proof.proofs.verify_offline(_token("dlg_active"))
        assert result["reason"] == "expired"
        await proof.close()


def _with_kid(token: str, kid: str) -> str:
    """The same token re-addressed to a kid no key set publishes; its signature never gets checked."""
    header, *rest = token.split(".")
    decoded = json.loads(base64.urlsafe_b64decode(header + "=" * (-len(header) % 4)))
    readdressed = base64.urlsafe_b64encode(json.dumps({**decoded, "kid": kid}).encode()).rstrip(b"=").decode()
    return ".".join([readdressed, *rest])


class TestOneFetchInFlight:
    """D-JP1: concurrent verifications share one key-set fetch."""

    async def test_concurrent_verifications_on_a_cold_cache_share_one_fetch(self, clock: _Clock, issuer: _Issuer) -> None:
        proof = _client()
        issuer.serve({"jwks": "registry_v1"})
        clock.set(T0, T0)
        results = await asyncio.gather(*(proof.proofs.verify_offline(_token("dlg_active")) for _ in range(20)))
        assert all(result["valid"] for result in results)
        assert issuer.jwks_fetches == 1
        await proof.close()

    async def test_concurrent_unknown_kids_cost_one_refetch(self, clock: _Clock, issuer: _Issuer) -> None:
        proof = _client()
        issuer.serve({"jwks": "registry_v1"})
        clock.set(T0, T0)
        await proof.proofs.verify_offline(_token("dlg_active"))
        issuer.jwks_fetches = 0
        clock.set(T0 + 60, T0 + 60)
        junk = [_with_kid(_token("dlg_active"), f"junk-{i}") for i in range(20)]
        results = await asyncio.gather(*(proof.proofs.verify_offline(token) for token in junk))
        assert not any(result["valid"] for result in results)
        assert issuer.jwks_fetches == 1
        await proof.close()

    async def test_a_cancelled_waiter_does_not_cancel_the_shared_fetch(self, clock: _Clock, issuer: _Issuer) -> None:
        proof = _client()
        issuer.serve({"jwks": "registry_v1"})
        clock.set(T0, T0)
        gate = asyncio.Event()
        real_fetch_public = proof._http.fetch_public

        async def gated_fetch_public(url: str, **kwargs: Any) -> Any:
            await gate.wait()
            return await real_fetch_public(url, **kwargs)

        proof._http.fetch_public = gated_fetch_public  # type: ignore[method-assign]
        waiters = [asyncio.ensure_future(proof.proofs.verify_offline(_token("dlg_active"))) for _ in range(3)]
        for _ in range(5):
            await asyncio.sleep(0)
        waiters[0].cancel()
        gate.set()
        results = await asyncio.gather(*waiters[1:])
        assert waiters[0].cancelled()
        assert all(result["valid"] for result in results)
        assert issuer.jwks_fetches == 1
        assert proof.proofs._key_set._in_flight is None
        await proof.close()


class TestClientSurface:
    """h-verifier-jwks-js-python SC-1, SC-3, SC-4, SC-5."""

    async def test_an_unexpected_error_answers_rather_than_raises(self, clock: _Clock, issuer: _Issuer) -> None:
        """``verify_offline`` returns a result dict whatever happens below it, as it did before."""
        proof = _client()
        clock.set(T0, T0)

        async def broken_resolve(*_: Any) -> Any:
            raise RuntimeError("bound to another event loop")

        proof.proofs._key_set.resolve = broken_resolve  # type: ignore[method-assign]
        result = await proof.proofs.verify_offline(_token("dlg_active"))
        assert result["valid"] is False
        assert result["reason"] == "invalid"
        assert result["revocation_checked"] is False
        await proof.close()

    @pytest.mark.parametrize("bad", [25 * 86_400 + 1, 0, -1, float("nan"), float("inf"), True, "3600", None])
    def test_rejects_an_unusable_max_jwks_age_at_construction(self, bad: Any) -> None:
        with pytest.raises(ValueError, match="max_jwks_age"):
            Proof("pk_test_x", max_jwks_age=bad)

    def test_accepts_the_cap_and_the_default(self) -> None:
        Proof("pk_test_x", max_jwks_age=25 * 86_400)
        Proof("pk_test_x")

    async def test_exposes_verified_at(self, clock: _Clock, issuer: _Issuer) -> None:
        proof = _client()
        issuer.serve({"jwks": "registry_v1"})
        clock.set(T0, T0)
        token = _token("prf_active")
        segment = token.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4)))
        result = await proof.proofs.verify_offline(token)
        assert result["valid"] is True
        assert isinstance(claims["verified_at"], str)
        assert result["payload"]["verified_at"] == claims["verified_at"]
        await proof.close()

    async def test_refresh_keeps_an_applied_tombstone_and_only_clear_lifts_it(
        self, clock: _Clock, issuer: _Issuer
    ) -> None:
        proof = _client()
        issuer.serve({"jwks": "registry_v1"})
        for at in (T0 - 11 * MIN, T0):
            clock.set(at, at)
            await proof.proofs.verify_offline(_token("dlg_retired"))
        issuer.serve({"jwks": "registry_tombstone_retired_delegation"})
        for at in (T0 + 11 * MIN, T0 + 16 * MIN):
            clock.set(at, at)
            proof.proofs.refresh_jwks()
            await proof.proofs.verify_offline(_token("dlg_retired"))
        assert (await proof.proofs.verify_offline(_token("dlg_retired")))["reason"] == "key_revoked"

        issuer.serve({"jwks": "registry_v1"})
        clock.set(T0 + 17 * MIN, T0 + 17 * MIN)
        proof.proofs.refresh_jwks()
        assert (await proof.proofs.verify_offline(_token("dlg_retired")))["reason"] == "key_revoked"
        assert issuer.jwks_fetches == 5

        proof.proofs.clear_tombstones()
        assert (await proof.proofs.verify_offline(_token("dlg_retired")))["valid"] is True
        await proof.close()

    def test_offline_verify_modules_no_longer_import_pyjwkclient(self) -> None:
        pattern = re.compile(r"^\s*(from\s+jwt\b.*\bimport\b.*\bPyJWKClient\b|import\s+jwt\.jwks_client\b)", re.M)
        modules = ["resources/proofs.py", "jwks/key_set_cache.py", "jwks/keyset.py"]
        for module in modules:
            source = (ROOT / "src" / "proof_sdk" / module).read_text()
            assert source, module
            assert not pattern.search(source), module
            assert "PyJWKClient(" not in source, module
        # Positive control: the pattern matches the import this task removed.
        assert pattern.search("            from jwt import PyJWKClient\n")

    def test_readme_states_that_tombstones_are_kept_in_memory_only(self) -> None:
        readme = (ROOT / "README.md").read_text()
        sections = [part for part in re.split(r"^### ", readme, flags=re.M) if part.startswith("Signing-key rotation")]
        assert sections, 'README heading "### Signing-key rotation"'
        assert "in memory" in sections[0]
        assert "not persisted" in sections[0]
        assert "clear_tombstones()" in sections[0]
