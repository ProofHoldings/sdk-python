"""Shared polling helper implementing the standard polling contract."""

from __future__ import annotations

import asyncio
import math
import random
import time
from typing import Any, Awaitable, Callable, Collection

from .errors import PollingTimeoutError

DEFAULT_INTERVAL = 2.0
DEFAULT_TIMEOUT = 600.0
DEFAULT_BACKOFF = 1.5
DEFAULT_MAX_INTERVAL = 30.0
DEFAULT_JITTER = 0.5


def _require_positive_finite(name: str, value: float) -> float:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive number, got {value!r}")
    return value


def _require_backoff(value: float) -> float:
    if not math.isfinite(value) or value < 1:
        raise ValueError(f"backoff must be a finite number >= 1, got {value!r}")
    return value


def _require_jitter(value: float) -> float:
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"jitter must be a finite non-negative number, got {value!r}")
    return value


async def poll_until_complete(
    retrieve: Callable[[], Awaitable[dict[str, Any]]],
    terminal_states: Collection[str],
    label: str,
    *,
    interval: float = DEFAULT_INTERVAL,
    timeout: float = DEFAULT_TIMEOUT,
    backoff: float = DEFAULT_BACKOFF,
    max_interval: float = DEFAULT_MAX_INTERVAL,
    jitter: float = DEFAULT_JITTER,
    cancel_event: asyncio.Event | None = None,
) -> dict[str, Any]:
    """Poll *retrieve* until the returned status is terminal or timeout is reached.

    Uses exponential backoff with jitter per the standard polling contract
    (docs/POLLING_CONTRACT.md). Pass *cancel_event* to abort polling early;
    when set, :class:`asyncio.CancelledError` is raised.
    """
    current_interval = _require_positive_finite("interval", interval)
    timeout = _require_positive_finite("timeout", timeout)
    backoff = _require_backoff(backoff)
    max_interval = _require_positive_finite("max_interval", max_interval)
    jitter = _require_jitter(jitter)

    start = time.monotonic()
    while True:
        if cancel_event is not None and cancel_event.is_set():
            raise asyncio.CancelledError(f"{label} polling cancelled")

        resource = await retrieve()
        if resource.get("status") in terminal_states:
            return resource
        if time.monotonic() - start >= timeout:
            raise PollingTimeoutError(
                f"{label} did not complete within {timeout}s "
                f"(last status: {resource.get('status')})"
            )

        sleep_for = current_interval + random.uniform(0, jitter)
        if cancel_event is not None:
            try:
                await asyncio.wait_for(cancel_event.wait(), timeout=sleep_for)
            except asyncio.TimeoutError:
                pass
            else:
                raise asyncio.CancelledError(f"{label} polling cancelled")
        else:
            await asyncio.sleep(sleep_for)

        current_interval = min(current_interval * backoff, max_interval)
