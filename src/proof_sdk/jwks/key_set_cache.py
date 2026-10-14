"""The issuer's key set as offline verification holds it — the I/O half around ``keyset.py``.

Mirrors ``packages/delegation-verifier/src/jwks.ts``, minus persistence: this SDK keeps tombstones in
memory only. Replaces ``PyJWKClient``, which hid the fetch time and the registry's own JWK members
and so could enforce neither tombstones, windows nor staleness.

- A fetched set is reused for 10 minutes (``PyJWKClient`` used 5; every other verifier, and the
  shared fixtures, use 10). An unknown ``kid`` triggers one refetch per 30 s cooldown, and one fetch
  is in flight at a time.
- A fetch is MERGED into what the verifier knows, never swapped in.
- A failed refetch does not discard the cache. Within ``max_jwks_age`` its CONFIRMED keys keep
  answering; beyond it the answer is stale — except an applied tombstone, which is revoked at any
  age. A set never fetched has nothing to fall back on and stays unavailable.
- A failed refetch of a cached set is retried at most once per cooldown.
- Age is measured on a monotonic clock; claim checks use the wall clock.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Protocol, Union

from .keyset import (
    Candidates,
    ClockReading,
    KeyRecord,
    KeySetEvent,
    KeySetState,
    Revoked,
    Unknown,
    WrongPurpose,
    empty_key_set_state,
    is_registry_live,
    merge_fetched_document,
    select_keys,
    with_confirmed_keys_only,
    without_tombstones,
)

SUPPORTED_ALGORITHMS: tuple[str, ...] = ("RS256", "ES256")

#: How long a ``kid`` miss — or a failed refetch of a cached set — suppresses further fetches.
KEY_MISS_COOLDOWN_MS = 30_000
#: How long a fetched key set is reused without refetching.
KEY_SET_TTL_MS = 10 * 60_000
#: Default ``max_jwks_age``, in seconds.
DEFAULT_MAX_JWKS_AGE_SECONDS = 24 * 3600.0
#: Largest accepted ``max_jwks_age``, in seconds — below the issuer's ~30-day lead on its next key.
MAX_JWKS_AGE_CAP_SECONDS = 25 * 86_400.0

JWKS_TIMEOUT_SECONDS = 5.0
#: A key set is kilobytes; anything larger is not one.
MAX_JWKS_BYTES = 512 * 1024

_logger = logging.getLogger("proof_sdk")


class JwksClock(Protocol):
    def monotonic_ms(self) -> float: ...

    def wall_ms(self) -> float: ...


class _SystemClock:
    def monotonic_ms(self) -> float:
        return time.monotonic() * 1000

    def wall_ms(self) -> float:
        return time.time() * 1000


_SYSTEM_CLOCK = _SystemClock()
_clock: JwksClock = _SYSTEM_CLOCK
_event_listener: Callable[[KeySetEvent], None] | None = None


def set_jwks_clock_for_tests(replacement: JwksClock | None) -> None:
    """Test seam — replaces both clocks; ``None`` restores the system clocks."""
    global _clock
    _clock = replacement if replacement is not None else _SYSTEM_CLOCK


def set_jwks_event_listener_for_tests(listener: Callable[[KeySetEvent], None] | None) -> None:
    """Test seam — receives every key-set event; ``None`` detaches."""
    global _event_listener
    _event_listener = listener


def now_wall_seconds() -> float:
    return _clock.wall_ms() / 1000


def validate_max_jwks_age(value: Any) -> float:
    """``value`` as seconds, or ``ValueError`` unless it is a number in (0, 25 days]."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not (0 < value <= MAX_JWKS_AGE_CAP_SECONDS):
        raise ValueError(
            f"max_jwks_age must be a number of seconds greater than 0 and at most {MAX_JWKS_AGE_CAP_SECONDS:.0f} (25 days)"
        )
    return float(value)


def is_supported_algorithm(alg: Any) -> bool:
    return isinstance(alg, str) and alg in SUPPORTED_ALGORITHMS


@dataclass(frozen=True)
class KeyCandidate:
    key: Any
    record: KeyRecord


@dataclass(frozen=True)
class Keys:
    candidates: list[KeyCandidate]
    registry_live: bool


@dataclass(frozen=True)
class Stale:
    cache_age_seconds: int | None


@dataclass(frozen=True)
class Unavailable:
    message: str


KeyResolution = Union[Keys, Revoked, WrongPurpose, Unknown, Stale, Unavailable]


def _emit(event: KeySetEvent) -> None:
    if event.type == "tombstone_for_live_key":
        _logger.warning("proof_sdk offline verification: %s", event.message)
    if _event_listener is None:
        return
    try:
        _event_listener(event)
    except Exception:
        # A throwing listener must not turn into a verification failure.
        pass


def _candidate_count(state: KeySetState, family: str) -> int:
    selection = select_keys(state, None, family)
    return len(selection.records) if isinstance(selection, Candidates) else 0


class _FetchOutcome:
    __slots__ = ("ok", "message")

    def __init__(self, ok: bool, message: str = "") -> None:
        self.ok = ok
        self.message = message


class KeySetCache:
    def __init__(self, http: Any, jwks_uri: str, max_jwks_age_seconds: float) -> None:
        self._http = http
        self._jwks_uri = jwks_uri
        self._max_jwks_age_ms = max_jwks_age_seconds * 1000
        self._state: KeySetState = empty_key_set_state()
        #: Imported keys by key material + algorithm; ``None`` records a JWK that failed to import.
        self._imported: dict[str, Any] = {}
        self._last_miss_at: float | None = None
        self._last_failed_at: float | None = None
        self._in_flight: asyncio.Task[_FetchOutcome] | None = None
        self._force_next = False

    async def resolve(self, kid: str | None, alg: str, family: str) -> KeyResolution:
        """The keys that may verify a token of ``family`` carrying ``kid`` — or why none may.

        Fetches when the set is older than the TTL, after ``force_refresh()``, or once per cooldown
        when ``kid`` is unknown.
        """
        now = _clock.monotonic_ms()
        forced = self._force_next
        if not forced and self._is_fresh(now):
            cached = self._resolve_from_state(self._state, kid, family, alg)
            if not isinstance(cached, Unknown):
                return cached
            if self._last_miss_at is not None and now - self._last_miss_at < KEY_MISS_COOLDOWN_MS:
                # The kid may have been published since the last refetch: "could not check".
                return Unavailable("unknown key; the key set is refetched again after the cooldown")

        recently_failed = (
            not forced
            and self._state.fetched_at is not None
            and self._last_failed_at is not None
            and now - self._last_failed_at < KEY_MISS_COOLDOWN_MS
        )
        if recently_failed:
            outcome = _FetchOutcome(False, "JWKS refetch failed recently; it is retried after the cooldown")
        else:
            outcome = await self._run_fetch()

        if not outcome.ok:
            if self._state.fetched_at is None:
                return Unavailable(outcome.message)
            # An applied tombstone is final whatever the cache's age: no refetch could lift it.
            known = select_keys(self._state, kid, family)
            if isinstance(known, Revoked):
                return known
            age = self._cache_age_ms(_clock.monotonic_ms())
            if age > self._max_jwks_age_ms:
                return Stale(int(age // 1000) if age != float("inf") else None)
            fallback = with_confirmed_keys_only(self._state)
            # A no-kid token tries every candidate: if the fallback lost one, a signature matching
            # none of the rest may still be that key's — "could not check", not a forgery.
            if kid is None and _candidate_count(fallback, family) < _candidate_count(self._state, family):
                return Unavailable(outcome.message)
            cached = self._resolve_from_state(fallback, kid, family, alg)
            return Unavailable(outcome.message) if isinstance(cached, Unknown) else cached

        resolved = self._resolve_from_state(self._state, kid, family, alg)
        if isinstance(resolved, Unknown):
            self._last_miss_at = _clock.monotonic_ms()
        return resolved

    def force_refresh(self) -> None:
        """Make the next resolution refetch, ignoring the TTL and both cooldowns. Keeps what is known."""
        self._force_next = True

    def clear_tombstones(self) -> None:
        """Forget every applied and pending tombstone — the documented manual reset."""
        self._state = without_tombstones(self._state)

    def diagnostics(self) -> dict[str, Any]:
        """What the cache holds, for tests."""
        age = self._cache_age_ms(_clock.monotonic_ms())
        return {
            "cache_age_seconds": int(age // 1000) if age != float("inf") else None,
            "registry_live": is_registry_live(self._state),
            "vanished_kids": [record.kid for record in self._state.keys.values() if record.vanished and record.kid],
        }

    def _cache_age_ms(self, now: float) -> float:
        if self._state.fetched_at is None or self._state.fetched_at_untrusted:
            return float("inf")
        return now - self._state.fetched_at.monotonic_ms

    def _is_fresh(self, now: float) -> bool:
        return self._cache_age_ms(now) < KEY_SET_TTL_MS

    async def _run_fetch(self) -> _FetchOutcome:
        """One fetch at a time; concurrent callers await the same outcome."""
        in_flight = self._in_flight
        if in_flight is None or in_flight.done():
            self._force_next = False
            in_flight = asyncio.ensure_future(self._fetch_and_merge())
            self._in_flight = in_flight
        return await asyncio.shield(in_flight)

    async def _fetch_and_merge(self) -> _FetchOutcome:
        try:
            try:
                body = await self._fetch_document()
                merged = merge_fetched_document(
                    self._state, body, ClockReading(monotonic_ms=_clock.monotonic_ms(), wall_ms=_clock.wall_ms())
                )
                for event in merged.events:
                    _emit(event)
                if merged.accepted:
                    self._state = merged.state
                    self._last_failed_at = None
                    return _FetchOutcome(True)
                failure = merged.events[0].message if merged.events else "JWKS refused"
            except Exception as error:
                failure = str(error) or "JWKS fetch failed"
            # Only a set with a cache to fall back on is held back; one never fetched is retried every call.
            if self._state.fetched_at is not None:
                self._last_failed_at = _clock.monotonic_ms()
            return _FetchOutcome(False, failure)
        finally:
            if self._in_flight is asyncio.current_task():
                self._in_flight = None

    async def _fetch_document(self) -> dict[str, Any]:
        status, headers, body = await self._http.fetch_public(
            self._jwks_uri,
            timeout=JWKS_TIMEOUT_SECONDS,
            headers={"accept": "application/json"},
            max_bytes=MAX_JWKS_BYTES,
        )
        if not 200 <= status < 300:
            raise ValueError(f"JWKS fetch failed with HTTP {status}")
        declared_length = headers.get("content-length")
        if declared_length and declared_length.isdigit() and int(declared_length) > MAX_JWKS_BYTES:
            raise ValueError("JWKS response is too large")
        if len(body) > MAX_JWKS_BYTES:
            raise ValueError("JWKS response is too large")
        try:
            parsed = json.loads(body)
        except ValueError:
            raise ValueError("JWKS response is not JSON") from None
        if not isinstance(parsed, dict) or not isinstance(parsed.get("keys"), list):
            raise ValueError("JWKS response has no `keys` array")
        return parsed

    def _resolve_from_state(self, state: KeySetState, kid: str | None, family: str, alg: str) -> KeyResolution:
        selection = select_keys(state, kid, family)
        if not isinstance(selection, Candidates):
            return selection
        candidates: list[KeyCandidate] = []
        for record in selection.records:
            key = self._import_record(record, alg)
            if key is not None:
                candidates.append(KeyCandidate(key=key, record=record))
        if not candidates:
            return Unknown()
        return Keys(candidates=candidates, registry_live=is_registry_live(state))

    def _import_record(self, record: KeyRecord, alg: str) -> Any:
        # A key declared for another algorithm, or for anything but signatures (RFC 7517 §4.2, §4.3),
        # is not a candidate. Checked before the import cache, which is keyed by material.
        jwk = record.jwk
        if isinstance(jwk.get("alg"), str) and jwk["alg"] != alg:
            return None
        if "use" in jwk and jwk["use"] != "sig":
            return None
        if "key_ops" in jwk and not (isinstance(jwk["key_ops"], list) and "verify" in jwk["key_ops"]):
            return None
        cache_key = f"{record.fingerprint}|{alg}"
        if cache_key in self._imported:
            return self._imported[cache_key]
        key: Any = None
        try:
            import jwt

            material = {
                member: jwk[member] for member in ("kty", "crv", "x", "y", "n", "e") if jwk.get(member) is not None
            }
            key = jwt.PyJWK(material, algorithm=alg).key
        except Exception:
            key = None
        self._imported[cache_key] = key
        return key
