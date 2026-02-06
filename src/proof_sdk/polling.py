"""Shared polling helper."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Awaitable, Callable, Collection

from .errors import PollingTimeoutError

DEFAULT_INTERVAL = 3.0
DEFAULT_TIMEOUT = 600.0


async def poll_until_complete(
    retrieve: Callable[[], Awaitable[dict[str, Any]]],
    terminal_states: Collection[str],
    label: str,
    *,
    interval: float = DEFAULT_INTERVAL,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Poll *retrieve* until the returned status is terminal or timeout is reached."""
    start = time.monotonic()
    while True:
        resource = await retrieve()
        if resource.get("status") in terminal_states:
            return resource
        if time.monotonic() - start >= timeout:
            raise PollingTimeoutError(
                f"{label} did not complete within {timeout}s "
                f"(last status: {resource.get('status')})"
            )
        await asyncio.sleep(interval)
