"""SSE frame parser: contract-level assertions.

The parser is a pure function — no network involvement — so these tests run
identically in live and mock modes.
"""

from __future__ import annotations

from proof_sdk.streaming import _parse_sse_block


def test_parses_json_data_frame():
    result = _parse_sse_block("id: 1\nevent: status_changed\ndata: {\"status\":\"pending\"}")
    assert result == {"event": "status_changed", "id": "1", "data": {"status": "pending"}}


def test_joins_multiline_data_lines():
    frame = "data: {\"status\":\ndata: \"verified\"}"
    result = _parse_sse_block(frame)
    assert result == {"event": "message", "id": None, "data": {"status": "verified"}}


def test_returns_none_for_comment_only_frame():
    assert _parse_sse_block(": heartbeat") is None


def test_returns_raw_when_data_is_not_json():
    result = _parse_sse_block("data: not-json-just-a-string")
    assert result == {"event": "message", "id": None, "data": "not-json-just-a-string"}
