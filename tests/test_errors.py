"""Tests for error hierarchy and fromResponse mapping."""

import pytest

from proof_sdk.errors import (
    ProofError,
    ValidationError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ServerError,
    NetworkError,
    RequestTimeoutError,
    PollingTimeoutError,
)


class TestFromResponse:
    def test_maps_400_to_validation(self) -> None:
        err = ProofError.from_response(400, {"code": "invalid_param", "message": "Bad input"})
        assert isinstance(err, ValidationError)
        assert err.status_code == 400
        assert err.code == "invalid_param"
        assert str(err) == "Bad input"

    def test_maps_401_to_authentication(self) -> None:
        err = ProofError.from_response(401)
        assert isinstance(err, AuthenticationError)
        assert err.status_code == 401

    def test_maps_403_to_forbidden(self) -> None:
        err = ProofError.from_response(403)
        assert isinstance(err, ForbiddenError)

    def test_maps_404_to_not_found(self) -> None:
        err = ProofError.from_response(404, {"code": "not_found", "message": "Not found"})
        assert isinstance(err, NotFoundError)

    def test_maps_409_to_conflict(self) -> None:
        err = ProofError.from_response(409)
        assert isinstance(err, ConflictError)

    def test_maps_429_to_rate_limit(self) -> None:
        err = ProofError.from_response(429)
        assert isinstance(err, RateLimitError)

    def test_maps_429_with_lockout_fields(self) -> None:
        err = ProofError.from_response(429, {
            "code": "auth_lockout",
            "message": "Too many attempts",
            "retryAfter": 3600,
            "remaining_attempts": 0,
        })
        assert isinstance(err, RateLimitError)
        assert err.retry_after == 3600
        assert err.remaining_attempts == 0
        assert err.code == "auth_lockout"

    def test_maps_500_to_server(self) -> None:
        err = ProofError.from_response(500)
        assert isinstance(err, ServerError)
        assert err.status_code == 500

    def test_maps_502_to_server_with_status(self) -> None:
        err = ProofError.from_response(502)
        assert isinstance(err, ServerError)
        assert err.status_code == 502

    def test_defaults_when_no_error_body(self) -> None:
        err = ProofError.from_response(418)
        assert err.code == "http_418"
        assert "418" in str(err)

    def test_preserves_details_and_request_id(self) -> None:
        err = ProofError.from_response(400, {
            "code": "validation",
            "message": "Bad",
            "details": {"field": "email"},
            "request_id": "req_abc",
        })
        assert err.details == {"field": "email"}
        assert err.request_id == "req_abc"


class TestErrorHierarchy:
    def test_all_extend_base(self) -> None:
        assert isinstance(ValidationError("", "", None), ProofError)
        assert isinstance(AuthenticationError("", "", None), ProofError)
        assert isinstance(ForbiddenError("", "", None), ProofError)
        assert isinstance(NotFoundError("", "", None), ProofError)
        assert isinstance(ConflictError("", "", None), ProofError)
        assert isinstance(RateLimitError("", "", None), ProofError)
        assert isinstance(ServerError("", ""), ProofError)
        assert isinstance(NetworkError(""), ProofError)
        assert isinstance(RequestTimeoutError(), ProofError)
        assert isinstance(PollingTimeoutError(), ProofError)

    def test_all_extend_exception(self) -> None:
        assert isinstance(ProofError("", "", 0), Exception)
        assert isinstance(PollingTimeoutError(), Exception)

    def test_timeout_not_shadows_builtin(self) -> None:
        """RequestTimeoutError should NOT shadow Python's builtin TimeoutError."""
        assert not issubclass(RequestTimeoutError, TimeoutError)
