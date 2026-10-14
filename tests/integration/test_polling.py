"""Polling helper: terminal-state detection, timeout, cancellation."""

from __future__ import annotations

import asyncio

import pytest

from proof_sdk import PollingTimeoutError
from proof_sdk.polling import poll_until_complete

from .conftest import is_live_mode


async def test_returns_on_terminal_state():
    if is_live_mode():
        pytest.skip()
    calls = {"n": 0}

    async def retrieve():
        calls["n"] += 1
        return {"status": "pending" if calls["n"] < 3 else "verified"}

    result = await poll_until_complete(
        retrieve,
        terminal_states=["verified", "failed"],
        label="verification",
        interval=0.005,
        backoff=1.0,
        jitter=0.0,
        max_interval=0.005,
        timeout=2.0,
    )
    assert result["status"] == "verified"
    assert calls["n"] == 3


async def test_timeout_raises_polling_timeout_error():
    if is_live_mode():
        pytest.skip()

    async def retrieve():
        return {"status": "pending"}

    with pytest.raises(PollingTimeoutError):
        await poll_until_complete(
            retrieve,
            terminal_states=["verified"],
            label="verification",
            interval=0.005,
            backoff=1.0,
            jitter=0.0,
            max_interval=0.005,
            timeout=0.02,
        )


async def test_cancel_event_aborts_polling():
    if is_live_mode():
        pytest.skip()
    cancel = asyncio.Event()

    async def retrieve():
        return {"status": "pending"}

    async def abort_soon():
        await asyncio.sleep(0.01)
        cancel.set()

    # Hold the task reference so asyncio can't GC it mid-flight.
    aborter = asyncio.create_task(abort_soon())
    try:
        with pytest.raises(asyncio.CancelledError):
            await poll_until_complete(
                retrieve,
                terminal_states=["verified"],
                label="verification",
                interval=0.005,
                backoff=1.0,
                jitter=0.0,
                max_interval=0.005,
                timeout=5.0,
                cancel_event=cancel,
            )
    finally:
        await aborter
