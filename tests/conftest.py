"""Shared fixtures for proof-sdk tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from proof_sdk.http import HttpClient


@pytest.fixture
def mock_http() -> HttpClient:
    """Return an HttpClient with mocked request methods."""
    http = HttpClient.__new__(HttpClient)
    http.base_url = "https://api.example.com"
    http._api_key = "pk_test_123"
    http._timeout = 5.0
    http._max_retries = 0
    http._client = None
    http.get = AsyncMock()
    http.post = AsyncMock()
    http.delete = AsyncMock()
    return http
