"""Error classes for the proof.holdings SDK."""

from __future__ import annotations

from typing import Any


class ProofError(Exception):
    """Base error for all proof.holdings API errors."""

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
        details: Any = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details
        self.request_id = request_id

    @staticmethod
    def from_response(status_code: int, error: dict[str, Any] | None = None) -> ProofError:
        code = error.get("code", f"http_{status_code}") if error else f"http_{status_code}"
        message = error.get("message", f"Request failed with status {status_code}") if error else f"Request failed with status {status_code}"
        details = error.get("details") if error else None
        request_id = error.get("request_id") if error else None

        error_map: dict[int, type[ProofError]] = {
            400: ValidationError,
            401: AuthenticationError,
            403: ForbiddenError,
            404: NotFoundError,
            409: ConflictError,
            429: RateLimitError,
        }

        cls = error_map.get(status_code)
        if cls:
            return cls(message, code, details, request_id)
        if status_code >= 500:
            return ServerError(message, code, status_code, details, request_id)
        return ProofError(message, code, status_code, details, request_id)


class ValidationError(ProofError):
    def __init__(self, message: str, code: str, details: Any = None, request_id: str | None = None) -> None:
        super().__init__(message, code, 400, details, request_id)


class AuthenticationError(ProofError):
    def __init__(self, message: str, code: str, details: Any = None, request_id: str | None = None) -> None:
        super().__init__(message, code, 401, details, request_id)


class ForbiddenError(ProofError):
    def __init__(self, message: str, code: str, details: Any = None, request_id: str | None = None) -> None:
        super().__init__(message, code, 403, details, request_id)


class NotFoundError(ProofError):
    def __init__(self, message: str, code: str, details: Any = None, request_id: str | None = None) -> None:
        super().__init__(message, code, 404, details, request_id)


class ConflictError(ProofError):
    def __init__(self, message: str, code: str, details: Any = None, request_id: str | None = None) -> None:
        super().__init__(message, code, 409, details, request_id)


class RateLimitError(ProofError):
    def __init__(self, message: str, code: str, details: Any = None, request_id: str | None = None) -> None:
        super().__init__(message, code, 429, details, request_id)


class ServerError(ProofError):
    def __init__(self, message: str, code: str, status_code: int = 500, details: Any = None, request_id: str | None = None) -> None:
        super().__init__(message, code, status_code, details, request_id)


class NetworkError(ProofError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "network_error", 0)


class RequestTimeoutError(ProofError):
    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message, "timeout", 0)


class PollingTimeoutError(ProofError):
    def __init__(self, message: str = "Polling timed out waiting for completion") -> None:
        super().__init__(message, "polling_timeout", 0)
