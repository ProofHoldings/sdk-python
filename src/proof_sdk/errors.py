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
        default_msg = f"Request failed with status {status_code}"
        code = error.get("code", f"http_{status_code}") if error else f"http_{status_code}"
        message = error.get("message", default_msg) if error else default_msg
        details = error.get("details") if error else None
        request_id = error.get("request_id") if error else None

        # 429 handled separately to preserve retry_after / remaining_attempts
        if status_code == 429:
            if error:
                return RateLimitError.from_api_error(error)
            return RateLimitError(message, code, details, request_id)

        error_map: dict[int, type[ProofError]] = {
            400: ValidationError,
            401: AuthenticationError,
            403: ForbiddenError,
            404: NotFoundError,
            409: ConflictError,
        }

        if status_code == 402:
            if error:
                return BalanceEmptyError.from_api_error(error)
            return BalanceEmptyError(message, code, details, request_id)

        cls = error_map.get(status_code)
        if cls:
            return cls(message, code, details, request_id)
        if code == BILLING_UNAVAILABLE:
            return BillingUnavailableError(message, status_code, details, request_id)
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
    """Rate limit or auth lockout error with optional retry/attempt fields."""

    def __init__(self, message: str, code: str, details: Any = None, request_id: str | None = None) -> None:
        super().__init__(message, code, 429, details, request_id)
        self.retry_after: int | None = None  # Seconds to wait before retrying
        self.remaining_attempts: int | None = None  # Remaining attempts before lockout

    @classmethod
    def from_api_error(cls, error: dict[str, Any]) -> RateLimitError:
        """Create a RateLimitError from an API error body, preserving lockout fields."""
        instance = cls(
            error.get("message", "Rate limited"),
            error.get("code", "rate_limited"),
            error.get("details"),
            error.get("request_id"),
        )
        instance.retry_after = error.get("retryAfter")
        instance.remaining_attempts = error.get("remaining_attempts")
        return instance


class ServerError(ProofError):
    def __init__(self, message: str, code: str, status_code: int = 500, details: Any = None, request_id: str | None = None) -> None:
        super().__init__(message, code, status_code, details, request_id)


#: The code of the billing kill switch's refusal: checkout, portal and top-up while billing is not live.
BILLING_UNAVAILABLE = "billing_unavailable"


class BillingUnavailableError(ServerError):
    """``503 billing_unavailable`` — billing is not live, so checkout, the portal and top-ups are refused.

    A ``ServerError``, so an existing ``except ServerError`` still catches it; unlike other 5xx
    answers it is never retried, because asking again cannot change it.
    """

    def __init__(self, message: str, status_code: int = 503, details: Any = None, request_id: str | None = None) -> None:
        super().__init__(message, BILLING_UNAVAILABLE, status_code, details, request_id)


class BalanceEmptyError(ProofError):
    """``402 balance_empty`` — the plan's included proofs are used and the prepaid balance is empty.

    Any method that creates a proof request can raise it once billing is live; proofs already
    issued keep working. ``top_up_url`` is where the owner tops up.
    """

    def __init__(self, message: str, code: str, details: Any = None, request_id: str | None = None) -> None:
        super().__init__(message, code, 402, details, request_id)
        self.top_up_url: str | None = None  # Where the owner tops up the balance
        self.used: int | None = None  # This period's production proofs
        self.included: int | None = None  # Proofs the plan includes per period
        self.balance: int | None = None  # The prepaid balance in euro cents, at or below zero

    @classmethod
    def from_api_error(cls, error: dict[str, Any]) -> BalanceEmptyError:
        """Create a BalanceEmptyError from the 402 body, keeping its four fields."""
        instance = cls(
            error.get("message", "The prepaid balance is empty"),
            error.get("code", "balance_empty"),
            error.get("details"),
            error.get("request_id"),
        )
        instance.top_up_url = error.get("top_up_url")
        instance.used = error.get("used")
        instance.included = error.get("included")
        instance.balance = error.get("balance")
        return instance


class NetworkError(ProofError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "network_error", 0)


class RequestTimeoutError(ProofError):
    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message, "timeout", 0)


class PollingTimeoutError(ProofError):
    def __init__(self, message: str = "Polling timed out waiting for completion") -> None:
        super().__init__(message, "polling_timeout", 0)
