"""Shared fixtures for proof-sdk tests."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from proof_sdk.http import HttpClient


@pytest.fixture
def mock_http() -> HttpClient:
    """Return an HttpClient with mocked request methods.

    Uses __new__ to skip __init__ and avoid needing a real API key or
    aiohttp session. Private fields are set to safe defaults; the actual
    HTTP methods are replaced with AsyncMocks.
    """
    http = HttpClient.__new__(HttpClient)
    http.base_url = "https://api.example.com"
    http._api_key = "pk_test_123"
    http._timeout = 5.0
    http._max_retries = 0
    http._client = None
    http.get = AsyncMock()
    http.post = AsyncMock()
    http.put = AsyncMock()
    http.patch = AsyncMock()
    http.delete = AsyncMock()
    http.request = AsyncMock()
    return http
