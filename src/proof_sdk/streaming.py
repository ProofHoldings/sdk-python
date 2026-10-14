"""Server-Sent Events (SSE) streaming helpers.

Provides an async generator that connects to an SSE endpoint and yields
each frame as ``{"event", "id", "data"}`` (``data`` JSON-decoded when it
parses), and falls back to contract-compliant polling when SSE is
unavailable (503) or fails — polled snapshots arrive as ``poll`` events and
the last one as ``terminal``. Matches the streaming contract used by the
JS/Go/PHP SDKs.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import random
from typing import Any, AsyncGenerator, AsyncIterator, Awaitable, Callable, Collection

import httpx

from .http import HttpClient
from .version import VERSION

DEFAULT_POLL_INTERVAL = 2.0
DEFAULT_POLL_TIMEOUT = 600.0
DEFAULT_POLL_BACKOFF = 1.5
DEFAULT_POLL_MAX_INTERVAL = 30.0
DEFAULT_POLL_JITTER = 0.5


def _parse_sse_block(block: str) -> dict[str, Any] | None:
    """Parse a single SSE frame (lines joined by ``\\n``).

    Returns ``{"event", "id", "data"}`` — ``event`` defaults to ``message``,
    ``id`` to ``None``, and ``data`` is the JSON-decoded payload of the joined
    ``data:`` lines, or the joined text when it is not JSON. Returns ``None``
    if the frame has no data.
    """
    event = "message"
    event_id: str | None = None
    data_lines: list[str] = []
    for raw_line in block.split("\n"):
        line = raw_line.rstrip("\r")
        if not line or line.startswith(":"):
            continue
        field, _, value = line.partition(":")
        if value.startswith(" "):
            value = value[1:]
        if field == "data":
            data_lines.append(value)
        elif field == "event":
            event = value
        elif field == "id":
            event_id = value
    if not data_lines:
        return None
    payload = "\n".join(data_lines)
    try:
        data: Any = json.loads(payload)
    except json.JSONDecodeError:
        data = payload
    return {"event": event, "id": event_id, "data": data}


def _is_terminal(
    payload: Any,
    terminal_states: Collection[str] | None,
    request_terminal_states: Collection[str] | None,
) -> bool:
    if not isinstance(payload, dict):
        return False
    if terminal_states and payload.get("status") in terminal_states:
        return True
    return bool(request_terminal_states) and payload.get("request_status") in request_terminal_states


async def _until_cancelled(
    chunks: AsyncIterator[str], cancel_event: asyncio.Event | None
) -> AsyncGenerator[str, None]:
    """Yield ``chunks`` until exhausted, raising as soon as ``cancel_event`` is set.

    The read is raced against the event, so a silent socket (the server only
    sends a keepalive every 30 s) cannot hold a cancellation back.
    """
    if cancel_event is None:
        async for chunk in chunks:
            yield chunk
        return
    while True:
        if cancel_event.is_set():
            raise asyncio.CancelledError("stream cancelled")
        read = asyncio.ensure_future(chunks.__anext__())
        cancelled = asyncio.ensure_future(cancel_event.wait())
        try:
            await asyncio.wait({read, cancelled}, return_when=asyncio.FIRST_COMPLETED)
        finally:
            cancelled.cancel()
            if not read.done():
                read.cancel()
                with contextlib.suppress(asyncio.CancelledError, StopAsyncIteration):
                    await read
        if read.cancelled():
            raise asyncio.CancelledError("stream cancelled")
        try:
            chunk = read.result()
        except StopAsyncIteration:
            return
        yield chunk


async def _fallback_poll(
    retrieve: Callable[[], Awaitable[dict[str, Any]]],
    terminal_states: Collection[str] | None,
    request_terminal_states: Collection[str] | None,
    cancel_event: asyncio.Event | None,
    interval: float,
    timeout: float,
    backoff: float,
    max_interval: float,
    jitter: float,
) -> AsyncGenerator[dict[str, Any], None]:
    """Poll ``retrieve`` and yield each snapshot as a ``poll`` event.

    Terminates after yielding a snapshot whose ``status`` is in
    ``terminal_states`` or whose ``request_status`` is in
    ``request_terminal_states`` — that one as a ``terminal`` event — or
    after ``timeout`` seconds. Raises :class:`asyncio.CancelledError` when
    ``cancel_event`` is set.
    """
    current_interval = interval
    loop = asyncio.get_running_loop()
    start = loop.time()
    while True:
        if cancel_event is not None and cancel_event.is_set():
            raise asyncio.CancelledError("stream cancelled")
        snapshot = await retrieve()
        if _is_terminal(snapshot, terminal_states, request_terminal_states):
            yield {"event": "terminal", "id": None, "data": snapshot}
            return
        yield {"event": "poll", "id": None, "data": snapshot}
        if loop.time() - start >= timeout:
            return
        sleep_for = current_interval + random.uniform(0, jitter)
        if cancel_event is not None:
            try:
                await asyncio.wait_for(cancel_event.wait(), timeout=sleep_for)
            except asyncio.TimeoutError:
                pass
            else:
                raise asyncio.CancelledError("stream cancelled")
        else:
            await asyncio.sleep(sleep_for)
        current_interval = min(current_interval * backoff, max_interval)


async def stream_endpoint(
    http: HttpClient,
    url: str,
    *,
    cancel_event: asyncio.Event | None = None,
    poll_retrieve: Callable[[], Awaitable[dict[str, Any]]] | None = None,
    terminal_states: Collection[str] | None = None,
    request_terminal_states: Collection[str] | None = None,
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    poll_timeout: float = DEFAULT_POLL_TIMEOUT,
    poll_backoff: float = DEFAULT_POLL_BACKOFF,
    poll_max_interval: float = DEFAULT_POLL_MAX_INTERVAL,
    poll_jitter: float = DEFAULT_POLL_JITTER,
    transport: httpx.AsyncBaseTransport | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """Connect to an SSE endpoint and yield ``{"event", "id", "data"}`` events.

    The stream ends when the server closes it, or after a frame whose
    ``data.status`` is in ``terminal_states`` or — for any frame but
    ``connected`` — whose ``data.request_status`` is in
    ``request_terminal_states``. Falls back to ``poll_retrieve`` (if
    provided) on HTTP 503 or any transport-level failure. Pass
    ``cancel_event`` (an :class:`asyncio.Event`) to stop the generator —
    promptly, even while the socket is silent; :class:`asyncio.CancelledError`
    is raised so callers can distinguish cancellation from normal end-of-stream.

    The ``url`` may be absolute or relative to the HTTP client's base URL.
    The optional ``transport`` argument is primarily used for testing with
    :class:`httpx.MockTransport`.
    """
    headers = {
        "Accept": "text/event-stream",
        "Authorization": f"Bearer {http._api_key}",
        "User-Agent": f"proof-sdk-python/{VERSION}",
        "Cache-Control": "no-cache",
    }

    full_url = (
        url
        if url.startswith("http://") or url.startswith("https://")
        else f"{http.base_url}{url}"
    )

    if cancel_event is not None and cancel_event.is_set():
        raise asyncio.CancelledError("stream cancelled")

    should_fallback = False
    client_kwargs: dict[str, Any] = {"timeout": None}
    if transport is not None:
        client_kwargs["transport"] = transport

    async with httpx.AsyncClient(**client_kwargs) as client:
        try:
            async with client.stream("GET", full_url, headers=headers) as response:
                if response.status_code >= 400:
                    # 503 explicitly indicates SSE disabled / unavailable;
                    # any other 4xx/5xx is treated the same for resilience.
                    should_fallback = True
                else:
                    buffer = ""
                    async for chunk in _until_cancelled(response.aiter_text(), cancel_event):
                        if not chunk:
                            continue
                        buffer += chunk
                        while "\n\n" in buffer:
                            if cancel_event is not None and cancel_event.is_set():
                                raise asyncio.CancelledError("stream cancelled")
                            block, buffer = buffer.split("\n\n", 1)
                            event = _parse_sse_block(block)
                            if event is None:
                                continue
                            yield event
                            request_states = (
                                None if event["event"] == "connected" else request_terminal_states
                            )
                            if _is_terminal(event["data"], terminal_states, request_states):
                                return
                    # Stream ended cleanly; drain trailing frame if any.
                    if buffer.strip():
                        tail = _parse_sse_block(buffer)
                        if tail is not None:
                            yield tail
                    return
        except asyncio.CancelledError:
            raise
        except httpx.HTTPError:
            should_fallback = True

    if should_fallback and poll_retrieve is not None:
        async for snapshot in _fallback_poll(
            poll_retrieve,
            terminal_states,
            request_terminal_states,
            cancel_event,
            poll_interval,
            poll_timeout,
            poll_backoff,
            poll_max_interval,
            poll_jitter,
        ):
            yield snapshot
