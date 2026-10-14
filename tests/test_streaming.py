"""Tests for SSE streaming helpers and Streams resource.

Uses :class:`httpx.MockTransport` to simulate SSE and polling responses
without hitting the network. Covers: event parsing/ordering, cancellation,
polling fallback on 503, and URL formation for all 8 stream endpoints.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
import pytest

from proof_sdk.http import HttpClient
from proof_sdk.resources.streams import Streams
from proof_sdk.resources.verifications import Verifications
from proof_sdk.streaming import _parse_sse_block, stream_endpoint


def _make_http(transport: httpx.MockTransport | None = None) -> HttpClient:
    """Build an HttpClient wired to a mock transport for tests."""
    http = HttpClient(
        api_key="pk_test_abc",
        base_url="https://api.example.com",
        timeout=5.0,
        max_retries=0,
    )
    if transport is not None:
        http._client = httpx.AsyncClient(
            base_url=http.base_url,
            transport=transport,
            headers={"Authorization": f"Bearer {http._api_key}"},
        )
    return http


def _sse_body(frames: list[dict[str, Any]], event: str = "update") -> bytes:
    """Encode a sequence of JSON payloads as a multi-frame SSE body."""
    return (
        "\n\n".join(f"id: {i}\nevent: {event}\ndata: {json.dumps(f)}" for i, f in enumerate(frames))
        + "\n\n"
    ).encode("utf-8")


def _frames(payloads: list[dict[str, Any]], event: str = "update") -> list[dict[str, Any]]:
    """The events the SDK yields for ``_sse_body(payloads, event)``."""
    return [{"event": event, "id": str(i), "data": p} for i, p in enumerate(payloads)]


def _polled(snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The events the polling fallback yields; the last snapshot is the terminal one."""
    return [
        {"event": "terminal" if i == len(snapshots) - 1 else "poll", "id": None, "data": snap}
        for i, snap in enumerate(snapshots)
    ]


class _SilentAfterFirstFrame(httpx.AsyncByteStream):
    """An SSE body that sends one frame and then keeps the socket open and silent."""

    async def __aiter__(self):  # type: ignore[override]
        yield b'id: 0\nevent: connected\ndata: {"status": "pending"}\n\n'
        await asyncio.sleep(3600)


class TestSseParser:
    def test_parses_single_data_line(self) -> None:
        assert _parse_sse_block('data: {"status": "pending"}') == {
            "event": "message",
            "id": None,
            "data": {"status": "pending"},
        }

    def test_keeps_event_name_and_id(self) -> None:
        block = 'id: 3\nevent: connected\ndata: {"status": "pending"}'
        assert _parse_sse_block(block) == {
            "event": "connected",
            "id": "3",
            "data": {"status": "pending"},
        }

    def test_ignores_comments_and_blanks(self) -> None:
        block = ": keep-alive\ndata: {\"n\": 1}"
        assert _parse_sse_block(block) == {"event": "message", "id": None, "data": {"n": 1}}

    def test_multiline_data_concatenates(self) -> None:
        block = "data: line1\ndata: line2"
        # JSON-decode fails so the joined text is surfaced as-is, as the JS SDK does
        assert _parse_sse_block(block) == {"event": "message", "id": None, "data": "line1\nline2"}

    def test_no_data_returns_none(self) -> None:
        assert _parse_sse_block(":heartbeat") is None


@pytest.mark.asyncio
class TestStreamEndpointHappyPath:
    async def test_yields_events_in_order(self) -> None:
        events = [{"status": "pending"}, {"status": "in_progress"}, {"status": "verified"}]

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["accept"] == "text/event-stream"
            return httpx.Response(200, content=_sse_body(events))

        http = _make_http()
        transport = httpx.MockTransport(handler)

        collected: list[dict[str, Any]] = []
        async for event in stream_endpoint(
            http,
            "/api/v1/verifications/v1/events",
            transport=transport,
            terminal_states={"verified"},
        ):
            collected.append(event)

        assert collected == _frames(events)

    async def test_terminal_state_stops_iteration_early(self) -> None:
        events = [{"status": "pending"}, {"status": "verified"}, {"status": "ignored"}]

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=_sse_body(events))

        http = _make_http()
        transport = httpx.MockTransport(handler)

        collected: list[dict[str, Any]] = []
        async for event in stream_endpoint(
            http,
            "/api/v1/verifications/v1/events",
            transport=transport,
            terminal_states={"verified"},
        ):
            collected.append(event)

        assert collected == _frames([{"status": "pending"}, {"status": "verified"}])

    async def test_terminal_request_status_stops_iteration(self) -> None:
        events = [
            {"status": "pending", "request_status": "pending"},
            {"status": "cancelled", "request_status": "cancelled"},
            {"status": "ignored"},
        ]

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=_sse_body(events))

        collected = [
            event
            async for event in stream_endpoint(
                _make_http(),
                "/api/v1/verify/request/vr_1/assets/0/events",
                transport=httpx.MockTransport(handler),
                terminal_states={"verified"},
                request_terminal_states={"cancelled", "expired"},
            )
        ]

        assert collected == _frames(events[:2])


@pytest.mark.asyncio
class TestClosedAtConnect:
    async def test_keeps_the_terminal_update_after_a_connected_frame_of_a_closed_request(self) -> None:
        body = (
            'id: 0\nevent: connected\ndata: {"status": "pending", "request_status": "cancelled"}\n\n'
            'id: 1\nevent: update\ndata: {"status": "cancelled", "request_status": "cancelled"}\n\n'
        ).encode("utf-8")

        collected = [
            event
            async for event in stream_endpoint(
                _make_http(),
                "/api/v1/verify/request/vr_1/assets/0/events",
                transport=httpx.MockTransport(lambda request: httpx.Response(200, content=body)),
                terminal_states={"verified"},
                request_terminal_states={"cancelled", "expired"},
            )
        ]

        assert [e["event"] for e in collected] == ["connected", "update"]


@pytest.mark.asyncio
class TestStreamCancellation:
    async def test_cancel_event_terminates_before_connection(self) -> None:
        # Pre-set cancel event: stream_endpoint must raise immediately without
        # issuing the request.
        async def hang(request: httpx.Request) -> httpx.Response:
            await asyncio.sleep(3600)
            return httpx.Response(200)

        http = _make_http()
        transport = httpx.MockTransport(hang)
        cancel = asyncio.Event()
        cancel.set()

        with pytest.raises(asyncio.CancelledError):
            async for _ in stream_endpoint(
                http,
                "/api/v1/verifications/v1/events",
                transport=transport,
                cancel_event=cancel,
                poll_retrieve=None,
            ):
                pass

    async def test_cancel_event_stops_mid_stream(self) -> None:
        events = [{"status": "pending"}] * 20

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=_sse_body(events))

        http = _make_http()
        transport = httpx.MockTransport(handler)
        cancel = asyncio.Event()

        collected: list[dict[str, Any]] = []
        with pytest.raises(asyncio.CancelledError):
            async for event in stream_endpoint(
                http,
                "/api/v1/verifications/v1/events",
                transport=transport,
                cancel_event=cancel,
                terminal_states={"verified"},
            ):
                collected.append(event)
                if len(collected) >= 2:
                    cancel.set()
                    # Loop once more so the generator checks the flag.
                    await asyncio.sleep(0)

        assert len(collected) >= 2

    async def test_cancel_event_stops_a_silent_socket_promptly(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, stream=_SilentAfterFirstFrame())

        cancel = asyncio.Event()
        collected: list[dict[str, Any]] = []

        async def consume() -> None:
            async for event in stream_endpoint(
                _make_http(),
                "/api/v1/verifications/v1/events",
                transport=httpx.MockTransport(handler),
                cancel_event=cancel,
            ):
                collected.append(event)
                asyncio.get_running_loop().call_later(0.05, cancel.set)

        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(consume(), timeout=1.0)

        assert collected == [{"event": "connected", "id": "0", "data": {"status": "pending"}}]


@pytest.mark.asyncio
class TestPollingFallback:
    async def test_503_triggers_polling(self) -> None:
        snapshots = [
            {"status": "pending"},
            {"status": "verified"},
        ]
        call_count = 0

        async def retrieve() -> dict[str, Any]:
            nonlocal call_count
            result = snapshots[min(call_count, len(snapshots) - 1)]
            call_count += 1
            return result

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(503, text="sse disabled")

        http = _make_http()
        transport = httpx.MockTransport(handler)

        collected: list[dict[str, Any]] = []
        async for event in stream_endpoint(
            http,
            "/api/v1/verifications/v1/events",
            transport=transport,
            poll_retrieve=retrieve,
            terminal_states={"verified"},
            poll_interval=0.01,
            poll_timeout=1.0,
            poll_jitter=0.0,
        ):
            collected.append(event)

        assert collected == _polled(snapshots)

    async def test_polling_stops_on_a_terminal_request_status(self) -> None:
        snapshots = [
            {"status": "pending", "request_status": "pending"},
            {"status": "pending", "request_status": "cancelled"},
        ]
        call_count = 0

        async def retrieve() -> dict[str, Any]:
            nonlocal call_count
            result = snapshots[min(call_count, len(snapshots) - 1)]
            call_count += 1
            return result

        collected = [
            event
            async for event in stream_endpoint(
                _make_http(),
                "/api/v1/verify/request/vr_1/assets/0/events",
                transport=httpx.MockTransport(lambda request: httpx.Response(503)),
                poll_retrieve=retrieve,
                terminal_states={"verified"},
                request_terminal_states={"cancelled", "expired"},
                poll_interval=0.01,
                poll_timeout=5.0,
                poll_jitter=0.0,
            )
        ]

        assert collected == _polled(snapshots)
        assert call_count == 2

    async def test_transport_error_triggers_polling(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("boom")

        async def retrieve() -> dict[str, Any]:
            return {"status": "verified"}

        http = _make_http()
        transport = httpx.MockTransport(handler)

        collected = [
            event
            async for event in stream_endpoint(
                http,
                "/api/v1/verifications/v1/events",
                transport=transport,
                poll_retrieve=retrieve,
                terminal_states={"verified"},
                poll_interval=0.01,
                poll_timeout=0.5,
                poll_jitter=0.0,
            )
        ]
        assert collected == _polled([{"status": "verified"}])


@pytest.mark.asyncio
class TestStreamsResourceUrls:
    """One test per endpoint verifying the SDK forms the correct SSE URL."""

    async def _run(
        self,
        expected_url: str,
        invoke: Any,
    ) -> None:
        observed: dict[str, str] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            observed["url"] = str(request.url)
            observed["auth"] = request.headers.get("authorization", "")
            observed["accept"] = request.headers.get("accept", "")
            return httpx.Response(200, content=_sse_body([{"status": "verified"}]))

        http = _make_http()
        transport = httpx.MockTransport(handler)

        # Monkey-patch the transport into stream_endpoint by passing it via
        # the resource. The resource itself doesn't expose a transport arg,
        # so we patch stream_endpoint from the module the resource imports.
        from proof_sdk.resources import streams as streams_mod

        original = streams_mod.stream_endpoint

        async def patched(http_arg: Any, url: str, **kwargs: Any):
            async for event in original(http_arg, url, transport=transport, **kwargs):
                yield event

        streams_mod.stream_endpoint = patched  # type: ignore[assignment]
        try:
            collected = [event async for event in invoke(Streams(http))]
        finally:
            streams_mod.stream_endpoint = original  # type: ignore[assignment]

        assert observed["url"].endswith(expected_url), observed["url"]
        assert observed["accept"] == "text/event-stream"
        assert observed["auth"] == "Bearer pk_test_abc"
        assert collected == _frames([{"status": "verified"}])

    async def test_verification_events_url(self) -> None:
        await self._run(
            "/api/v1/verifications/ver_1/events",
            lambda s: s.verification_events("ver_1"),
        )

    async def test_confirmation_events_url(self) -> None:
        await self._run(
            "/api/v1/confirmations/cnf_1/events",
            lambda s: s.confirmation_events("cnf_1"),
        )

    async def test_auth_session_events_url(self) -> None:
        await self._run(
            "/api/v1/auth/sessions/as_1/events",
            lambda s: s.auth_session_events("as_1"),
        )

    async def test_twofa_events_url(self) -> None:
        await self._run(
            "/api/v1/me/2fa/tfs_1/events",
            lambda s: s.twofa_events("tfs_1"),
        )

    async def test_phone_add_events_url(self) -> None:
        await self._run(
            "/api/v1/me/phones/add/pas_1/events",
            lambda s: s.phone_add_events("pas_1"),
        )

    async def test_email_add_events_url(self) -> None:
        await self._run(
            "/api/v1/me/emails/add/eas_1/events",
            lambda s: s.email_add_events("eas_1"),
        )

    async def test_hitl_chat_id_discovery_events_url(self) -> None:
        await self._run(
            "/api/v1/hitl/chat-id-discovery/tok_abc/events",
            lambda s: s.hitl_chat_id_discovery_events("tok_abc"),
        )

    async def test_verification_request_asset_events_url(self) -> None:
        await self._run(
            "/api/v1/verify/request/vr_1/assets/2/events",
            lambda s: s.verification_request_asset_events("vr_1", 2),
        )


@pytest.mark.asyncio
class TestVerificationsStreamShortcut:
    """The Verifications resource exposes a ``stream()`` convenience method."""

    async def test_stream_calls_correct_url(self) -> None:
        observed: dict[str, str] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            observed["url"] = str(request.url)
            return httpx.Response(200, content=_sse_body([{"status": "verified"}]))

        http = _make_http()
        transport = httpx.MockTransport(handler)

        from proof_sdk.resources import verifications as v_mod

        original = v_mod.stream_endpoint

        async def patched(http_arg: Any, url: str, **kwargs: Any):
            async for event in original(http_arg, url, transport=transport, **kwargs):
                yield event

        v_mod.stream_endpoint = patched  # type: ignore[assignment]
        try:
            collected = [event async for event in Verifications(http).stream("ver_abc")]
        finally:
            v_mod.stream_endpoint = original  # type: ignore[assignment]

        assert observed["url"].endswith("/api/v1/verifications/ver_abc/events")
        assert collected == _frames([{"status": "verified"}])


@pytest.mark.asyncio
class TestTerminalStatesMatchBackend:
    """Terminal sets must match the backend's actual status values.

    Backend reality: CONFIRMATION_STATUS is pending/approved/denied
    (src/constants/statuses.ts) — a timeout resolves server-side to
    ``denied``, never ``expired``. Chat-id discovery polls return
    pending/completed (src/services/redis.ts getChatIdDiscovery).
    A wrong terminal value means the poll fallback never stops and
    exhausts its timeout instead.
    """

    def _capture_terminal_states(self, invoke: Any) -> set[str]:
        from proof_sdk.resources import streams as streams_mod

        captured: dict[str, Any] = {}
        original = streams_mod.stream_endpoint

        def patched(http_arg: Any, url: str, **kwargs: Any) -> Any:
            captured["terminal_states"] = kwargs.get("terminal_states")

            async def _empty():
                if False:  # pragma: no cover
                    yield

            return _empty()

        streams_mod.stream_endpoint = patched  # type: ignore[assignment]
        try:
            invoke(Streams(_make_http()))
        finally:
            streams_mod.stream_endpoint = original  # type: ignore[assignment]
        return captured["terminal_states"]

    async def test_confirmation_terminal_uses_denied(self) -> None:
        states = self._capture_terminal_states(lambda s: s.confirmation_events("cnf_1"))
        assert "denied" in states  # backend's denial status must stop the poll fallback
        assert "declined" not in states  # not a real backend status

    async def test_hitl_chat_terminal_uses_completed(self) -> None:
        states = self._capture_terminal_states(
            lambda s: s.hitl_chat_id_discovery_events("tok_1")
        )
        assert "completed" in states  # backend value from getChatIdDiscovery
        assert "discovered" not in states  # not a real backend status


@pytest.mark.asyncio
class TestVerificationRequestAssetStream:
    """The asset stream polls the real status route and ends on the asset's real outcomes."""

    def _capture(self, invoke: Any) -> dict[str, Any]:
        from proof_sdk.resources import streams as streams_mod

        captured: dict[str, Any] = {}
        original = streams_mod.stream_endpoint

        def patched(http_arg: Any, url: str, **kwargs: Any) -> Any:
            captured.update(kwargs)

            async def _empty():
                if False:  # pragma: no cover
                    yield

            return _empty()

        streams_mod.stream_endpoint = patched  # type: ignore[assignment]
        try:
            invoke(Streams(_make_http()))
        finally:
            streams_mod.stream_endpoint = original  # type: ignore[assignment]
        return captured

    async def test_polling_fallback_uses_the_status_route(self) -> None:
        observed: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            observed.append(request.url.path)
            if request.url.path.endswith("/events"):
                return httpx.Response(503)
            return httpx.Response(200, json={"status": "verified", "request_status": "completed"})

        http = _make_http(httpx.MockTransport(handler))
        from proof_sdk.resources import streams as streams_mod

        original = streams_mod.stream_endpoint

        async def patched(http_arg: Any, url: str, **kwargs: Any):
            async for event in original(http_arg, url, transport=httpx.MockTransport(handler), **kwargs):
                yield event

        streams_mod.stream_endpoint = patched  # type: ignore[assignment]
        try:
            collected = [
                event async for event in Streams(http).verification_request_asset_events("vr_1", 2)
            ]
        finally:
            streams_mod.stream_endpoint = original  # type: ignore[assignment]

        assert observed == [
            "/api/v1/verify/request/vr_1/assets/2/events",
            "/api/v1/verify/request/vr_1/assets/2/status",
        ]
        assert collected == _polled([{"status": "verified", "request_status": "completed"}])

    async def test_terminal_statuses_are_the_asset_outcomes(self) -> None:
        kwargs = self._capture(lambda s: s.verification_request_asset_events("vr_1", 0))

        assert set(kwargs["terminal_states"]) == {"verified", "failed", "expired", "revoked"}
        assert set(kwargs["request_terminal_states"]) == {"cancelled", "expired"}
