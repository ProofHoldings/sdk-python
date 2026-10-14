"""The key-rotation rules, free of I/O.

A function-for-function port of ``packages/delegation-verifier/src/keyset.ts``: how a fetched JWKS
is merged into what the verifier already knows, and which key — if any — may verify a token of a
given family. The shared cases in ``sdks/shared/fixtures/jwks_rotation/`` pin the outcome of every
rule across all five verifiers, so change a rule there first and port it here.

The persistence half of the original (state serialization) is not ported: this SDK keeps its key
set in memory only.

Four properties are load-bearing:

- One response is never trusted for long. Anything that would outlive the next fetch — a key being
  remembered, a window narrowing, a tombstone — takes effect only when a second fetch, at least five
  minutes after the first sighting, says the same. A key verifies from its first sighting, but until
  it is confirmed the next document replaces or drops it.
- A fetch is MERGED, never swapped in. A CONFIRMED registry key that disappears keeps its last-known
  state, never gets new key material, and its window may narrow (by the rule above) but never widen
  — a document that widens one is refused whole.
- An applied tombstone is sticky until every token the key signed is dead.
- "Registry live" is a property of the merged set (some key carries ``proof_purpose``). Until then
  the set is in tolerant mode and behaves exactly as it did before rotation existed.
"""

from __future__ import annotations

import dataclasses
import json
import math
from dataclasses import dataclass, field
from typing import Any, Literal, Union

KeyFamily = Literal["proof", "delegation", "status-list"]
KEY_FAMILIES: tuple[str, ...] = ("proof", "delegation", "status-list")

#: Clock skew tolerated on each edge of a key's ``[not_before, not_after]`` window.
KEY_WINDOW_SKEW_SECONDS = 300
#: Minimum spacing between the two fetches that confirm a key, a narrowed window or a tombstone.
CONFIRM_SPACING_MS = 5 * 60_000
#: An applied tombstone is kept until ``revoked_at`` plus this.
TOMBSTONE_RETENTION_SECONDS = 365 * 86_400


@dataclass(frozen=True)
class ClockReading:
    """Both clocks at one instant: monotonic for in-process intervals, wall for anything persisted."""

    monotonic_ms: float
    wall_ms: float


@dataclass(frozen=True)
class PendingWindow:
    not_before: int
    not_after: int
    first_seen: ClockReading


@dataclass
class KeyRecord:
    #: The JWK as last accepted, with any narrowing of its window applied.
    jwk: dict[str, Any]
    #: Identity of the key material: a protected kid keeps its first material, an unprotected one takes the latest.
    fingerprint: str
    #: ``alg``, ``use`` and ``key_ops`` — the members that decide whether the key may verify at all.
    usage: str
    has_purpose_member: bool
    legacy: bool
    #: When this exact description of the key was first served.
    first_seen: ClockReading
    kid: str | None = None
    purpose: str | None = None
    not_before: int | None = None
    not_after: int | None = None
    max_token_lifetime: int | None = None
    vanished: bool = False
    #: Served unchanged by two fetches at least ``CONFIRM_SPACING_MS`` apart.
    confirmed: bool = False
    #: A narrower window served for a confirmed key, applied once a later fetch confirms it.
    pending_window: PendingWindow | None = None


@dataclass(frozen=True)
class PendingTombstone:
    kid: str
    revoked_at: int
    first_seen: ClockReading


@dataclass(frozen=True)
class AppliedTombstone:
    kid: str
    revoked_at: int


@dataclass
class KeySetState:
    keys: dict[str, KeyRecord] = field(default_factory=dict)
    #: Keys served without a ``kid`` — tolerant mode only ever needs them.
    anonymous: list[KeyRecord] = field(default_factory=list)
    pending: dict[str, PendingTombstone] = field(default_factory=dict)
    applied: dict[str, AppliedTombstone] = field(default_factory=dict)
    fetched_at: ClockReading | None = None
    #: A persisted ``fetched_at`` lay in the future: its age is unknown, so it counts as stale.
    fetched_at_untrusted: bool = False


@dataclass(frozen=True)
class KeySetEvent:
    type: str
    message: str
    kid: str | None = None


@dataclass(frozen=True)
class MergeResult:
    state: KeySetState
    events: list[KeySetEvent]
    #: False when the document was refused whole; ``state`` is then the unchanged input.
    accepted: bool


@dataclass(frozen=True)
class Candidates:
    records: list[KeyRecord]


@dataclass(frozen=True)
class Revoked:
    kid: str


@dataclass(frozen=True)
class WrongPurpose:
    kid: str


@dataclass(frozen=True)
class Unknown:
    pass


KeySelection = Union[Candidates, Revoked, WrongPurpose, Unknown]

KeyPolicyViolation = Literal["outside_key_window", "token_lifetime_exceeded"]


def empty_key_set_state() -> KeySetState:
    return KeySetState()


def _whole_number(value: Any) -> int | None:
    """The value as an int when it is a whole JSON number (``Number.isInteger`` in the original)."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and math.isfinite(value) and value.is_integer():
        return int(value)
    return None


def _is_record(value: Any) -> bool:
    return isinstance(value, dict)


_MATERIAL_MEMBERS = ("kty", "crv", "x", "y", "n", "e")


def _fingerprint_of(jwk: dict[str, Any]) -> str:
    return json.dumps([jwk.get(member) for member in _MATERIAL_MEMBERS])


def _usage_of(jwk: dict[str, Any]) -> str:
    return json.dumps([jwk.get("alg"), jwk.get("use"), jwk.get("key_ops")], sort_keys=True)


def parse_key_record(jwk: dict[str, Any], first_seen: ClockReading) -> KeyRecord:
    kid = jwk.get("kid")
    purpose = jwk.get("proof_purpose")
    return KeyRecord(
        jwk=jwk,
        fingerprint=_fingerprint_of(jwk),
        usage=_usage_of(jwk),
        has_purpose_member="proof_purpose" in jwk,
        legacy=jwk.get("proof_legacy") is True,
        first_seen=first_seen,
        kid=kid if isinstance(kid, str) and kid else None,
        purpose=purpose if isinstance(purpose, str) and purpose in KEY_FAMILIES else None,
        not_before=_whole_number(jwk.get("not_before")),
        not_after=_whole_number(jwk.get("not_after")),
        max_token_lifetime=_whole_number(jwk.get("max_token_lifetime")),
    )


def _has_window(record: KeyRecord) -> bool:
    return record.not_before is not None and record.not_after is not None and record.max_token_lifetime is not None


def _is_protected_record(record: KeyRecord) -> bool:
    """A registry key (``proof_purpose`` or ``proof_legacy``) that two spaced fetches served unchanged.

    The ONE predicate behind every rule that outlives a fetch: material lock, no widening, pending
    narrowing, retained when it vanishes. Window members alone do not make a registry key.
    """
    return record.confirmed and (record.has_purpose_member or record.legacy)


def _describes_same_key(a: KeyRecord, b: KeyRecord) -> bool:
    """Same material, usage, purpose, legacy marker and window.

    Usage counts because the record kept is the one first seen: a poisoned first sighting marked
    ``use: "enc"`` must be replaced by the honest description, not confirmed by it.
    """
    return (
        a.fingerprint == b.fingerprint
        and a.usage == b.usage
        and a.has_purpose_member == b.has_purpose_member
        and a.purpose == b.purpose
        and a.legacy == b.legacy
        and a.not_before == b.not_before
        and a.not_after == b.not_after
        and a.max_token_lifetime == b.max_token_lifetime
    )


def _spacing_elapsed(since: ClockReading, now: ClockReading) -> bool:
    return now.monotonic_ms - since.monotonic_ms >= CONFIRM_SPACING_MS


def is_registry_live(state: KeySetState) -> bool:
    if any(record.has_purpose_member for record in state.keys.values()):
        return True
    return any(record.has_purpose_member for record in state.anonymous)


def _wall_seconds(reading: ClockReading) -> int:
    return math.floor(reading.wall_ms / 1000)


def _is_live_key(record: KeyRecord, now_seconds: int) -> bool:
    """Whether a kid may still be signing: legacy, window unknown, or not yet past ``not_after``."""
    if record.legacy or not _has_window(record):
        return True
    assert record.not_after is not None
    return now_seconds <= record.not_after + KEY_WINDOW_SKEW_SECONDS


def _parse_tombstones(value: Any) -> list[AppliedTombstone]:
    if not isinstance(value, list):
        return []
    tombstones: list[AppliedTombstone] = []
    for entry in value:
        if not _is_record(entry):
            continue
        kid = entry.get("kid")
        revoked_at = _whole_number(entry.get("revoked_at"))
        if not isinstance(kid, str) or not kid or revoked_at is None:
            continue
        tombstones.append(AppliedTombstone(kid=kid, revoked_at=revoked_at))
    return tombstones


def _clone_state(state: KeySetState) -> KeySetState:
    return KeySetState(
        keys={kid: dataclasses.replace(record) for kid, record in state.keys.items()},
        anonymous=[dataclasses.replace(record) for record in state.anonymous],
        pending=dict(state.pending),
        applied=dict(state.applied),
        fetched_at=state.fetched_at,
        fetched_at_untrusted=state.fetched_at_untrusted,
    )


def merge_fetched_document(state: KeySetState, body: dict[str, Any], now: ClockReading) -> MergeResult:
    """Merge one fetched JWKS body (an object with a ``keys`` array) into ``state``.

    Pure: returns a new state and the events the caller should report.
    """
    now_seconds = _wall_seconds(now)
    raw_keys = body.get("keys")
    candidates = [jwk for jwk in raw_keys if _is_record(jwk)] if isinstance(raw_keys, list) else []
    served: dict[str, KeyRecord] = {}
    anonymous: list[KeyRecord] = []
    for jwk in candidates:
        record = parse_key_record(jwk, now)
        if record.kid:
            served[record.kid] = record
        else:
            anonymous.append(record)

    # Widening is checked before anything is touched: such a document is refused whole.
    for kid, incoming in served.items():
        known = state.keys.get(kid)
        if known is None or not _is_protected_record(known) or not _has_window(known) or not _has_window(incoming):
            continue
        assert known.not_before is not None and known.not_after is not None
        assert incoming.not_before is not None and incoming.not_after is not None
        if incoming.not_before < known.not_before or incoming.not_after > known.not_after:
            return MergeResult(
                state=state,
                accepted=False,
                events=[
                    KeySetEvent(
                        type="window_widening_rejected",
                        kid=kid,
                        message=f'JWKS refused: it widens the window of confirmed key "{kid}"',
                    )
                ],
            )

    nxt = _clone_state(state)
    events: list[KeySetEvent] = []
    tombstones = _parse_tombstones(body.get("proof_tombstones"))
    tombstoned_now = {tombstone.kid for tombstone in tombstones}

    for kid, incoming in served.items():
        known = nxt.keys.get(kid)
        # Not protected yet: the latest document describes the key, exactly as before rotation
        # existed. Serving the same description again, far enough apart, confirms it.
        if known is None or not _is_protected_record(known):
            if known is not None and _describes_same_key(known, incoming):
                if not known.confirmed and _spacing_elapsed(known.first_seen, now):
                    known.confirmed = True
            else:
                nxt.keys[kid] = incoming
            continue
        known.vanished = False
        if known.fingerprint != incoming.fingerprint:
            known.pending_window = None
            events.append(
                KeySetEvent(
                    type="key_material_changed",
                    kid=kid,
                    message=f'JWKS serves different key material for confirmed key "{kid}"; the first-seen key is kept',
                )
            )
            continue
        if not _has_window(known) or not _has_window(incoming):
            continue
        assert incoming.not_before is not None and incoming.not_after is not None
        if incoming.not_before == known.not_before and incoming.not_after == known.not_after:
            known.pending_window = None
            continue
        pending = known.pending_window
        if pending is None or pending.not_before != incoming.not_before or pending.not_after != incoming.not_after:
            known.pending_window = PendingWindow(
                not_before=incoming.not_before, not_after=incoming.not_after, first_seen=now
            )
            events.append(
                KeySetEvent(
                    type="window_narrowing_pending",
                    kid=kid,
                    message=(
                        f'JWKS narrows the window of confirmed key "{kid}"; applied only if a fetch at least '
                        "5 minutes later serves the same window"
                    ),
                )
            )
            continue
        if not _spacing_elapsed(pending.first_seen, now):
            continue
        known.not_before = pending.not_before
        known.not_after = pending.not_after
        known.jwk = {**known.jwk, "not_before": pending.not_before, "not_after": pending.not_after}
        known.pending_window = None
        events.append(
            KeySetEvent(
                type="window_narrowing_applied",
                kid=kid,
                message=f'narrowed window of key "{kid}" confirmed by a second fetch and applied',
            )
        )

    for kid, known in list(nxt.keys.items()):
        if kid in served:
            continue
        if not _is_protected_record(known):
            del nxt.keys[kid]
            continue
        if _has_window(known):
            assert known.not_after is not None and known.max_token_lifetime is not None
            if now_seconds > known.not_after + known.max_token_lifetime + KEY_WINDOW_SKEW_SECONDS:
                del nxt.keys[kid]
                continue
        elif not known.legacy:
            del nxt.keys[kid]
            continue
        # A narrowing is confirmed by consecutive documents serving it; one that omits the kid breaks the run.
        known.pending_window = None
        if not known.vanished and kid not in tombstoned_now:
            known.vanished = True
            events.append(
                KeySetEvent(
                    type="kid_vanished",
                    kid=kid,
                    message=f'key "{kid}" is no longer served before its retention ended; its last-known state is kept',
                )
            )

    nxt.anonymous = anonymous

    for kid in list(nxt.pending):
        if kid not in tombstoned_now:
            del nxt.pending[kid]
    for tombstone in tombstones:
        if tombstone.kid in nxt.applied:
            continue
        pending_tombstone = nxt.pending.get(tombstone.kid)
        if pending_tombstone is not None:
            if _spacing_elapsed(pending_tombstone.first_seen, now):
                del nxt.pending[tombstone.kid]
                nxt.applied[tombstone.kid] = AppliedTombstone(
                    kid=tombstone.kid, revoked_at=pending_tombstone.revoked_at
                )
                events.append(
                    KeySetEvent(
                        type="tombstone_applied",
                        kid=tombstone.kid,
                        message=f'tombstone for key "{tombstone.kid}" confirmed by a second fetch and applied',
                    )
                )
            continue
        nxt.pending[tombstone.kid] = PendingTombstone(
            kid=tombstone.kid, revoked_at=tombstone.revoked_at, first_seen=now
        )
        events.append(
            KeySetEvent(
                type="tombstone_pending",
                kid=tombstone.kid,
                message=(
                    f'tombstone for key "{tombstone.kid}" seen; applied only if a fetch at least '
                    "5 minutes later still carries it"
                ),
            )
        )
        # "Last seen live" is read from what the verifier knew BEFORE this document, which may itself
        # have dropped the key.
        previously_known = state.keys.get(tombstone.kid)
        if previously_known is not None and _is_live_key(previously_known, now_seconds):
            events.append(
                KeySetEvent(
                    type="tombstone_for_live_key",
                    kid=tombstone.kid,
                    message=f'ANOMALY: tombstone names key "{tombstone.kid}", which was last seen live',
                )
            )

    for kid, applied in list(nxt.applied.items()):
        if now_seconds > applied.revoked_at + TOMBSTONE_RETENTION_SECONDS:
            del nxt.applied[kid]

    nxt.fetched_at = now
    nxt.fetched_at_untrusted = False
    return MergeResult(state=nxt, events=events, accepted=True)


def select_keys(state: KeySetState, kid: str | None, family: str) -> KeySelection:
    """Which keys may verify a token of ``family`` carrying ``kid``.

    Checks the applied tombstone and the key's purpose; the signature and the window are the
    caller's next steps, in that order.
    """
    registry_live = is_registry_live(state)
    if kid is not None:
        if kid in state.applied:
            return Revoked(kid=kid)
        record = state.keys.get(kid)
        if record is None:
            return Unknown()
        if record.legacy or not registry_live:
            return Candidates(records=[record])
        if record.purpose != family:
            return WrongPurpose(kid=kid)
        return Candidates(records=[record])

    # No ``kid``: once the registry is live only a key marked legacy may answer — trying every key
    # would let a token borrow any family's key and skip the purpose check.
    every = [
        record
        for record in [*state.anonymous, *state.keys.values()]
        if not (record.kid and record.kid in state.applied)
    ]
    records = [record for record in every if record.legacy] if registry_live else every
    return Candidates(records=records) if records else Unknown()


def check_key_policy(record: KeyRecord, iat: Any, exp: Any, registry_live: bool) -> KeyPolicyViolation | None:
    """The window and lifetime rules for a key whose signature has verified."""
    if not registry_live or record.legacy:
        return None
    if not _has_window(record):
        return "outside_key_window"
    assert record.not_before is not None and record.not_after is not None and record.max_token_lifetime is not None
    issued_at = _whole_number(iat)
    if issued_at is None:
        return "outside_key_window"
    if issued_at < record.not_before - KEY_WINDOW_SKEW_SECONDS:
        return "outside_key_window"
    if issued_at > record.not_after + KEY_WINDOW_SKEW_SECONDS:
        return "outside_key_window"
    if isinstance(exp, bool) or not isinstance(exp, (int, float)) or exp > issued_at + record.max_token_lifetime:
        return "token_lifetime_exceeded"
    return None


def with_confirmed_keys_only(state: KeySetState) -> KeySetState:
    """The part of a cached set that may answer after a refetch FAILED: confirmed keys only.

    An unconfirmed key is trusted until the next document, and a failing fetch must not stretch that
    to ``max_jwks_age``.
    """
    nxt = _clone_state(state)
    for kid, record in list(nxt.keys.items()):
        if not record.confirmed:
            del nxt.keys[kid]
    nxt.anonymous = []
    return nxt


def without_tombstones(state: KeySetState) -> KeySetState:
    """Drop every applied and pending tombstone — the documented manual reset."""
    nxt = _clone_state(state)
    nxt.applied.clear()
    nxt.pending.clear()
    return nxt
