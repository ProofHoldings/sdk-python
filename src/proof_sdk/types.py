"""Type definitions for the proof.holdings API."""

from __future__ import annotations

from typing import Any, Literal

# ============================================================================
# Core Types
# ============================================================================

VerificationType = Literal["phone", "email", "domain", "social", "wallet", "account", "waba", "telegram_bot"]

VerificationChannel = Literal[
    "whatsapp", "telegram", "viber", "sms",
    "email",
    "dns", "http", "auto",
    "github", "google", "facebook", "x", "linkedin", "instagram", "youtube", "tiktok",
    "ethereum", "solana", "bitcoin",
    "coinbase", "kraken",
    "waba_otp", "telegram_bot_token",
]

VerificationStatus = Literal["pending", "verified", "failed", "expired", "revoked"]

SessionChannel = Literal["telegram", "whatsapp", "viber", "sms"]

VerificationRequestStatus = Literal["pending", "partial", "completed", "expired", "cancelled"]

ActionType = Literal["verification", "2fa", "login", "custom"]

# ============================================================================
# TypedDict definitions for API responses
# ============================================================================
# We use plain dicts with type aliases rather than TypedDict to keep
# the SDK lightweight (no pydantic dependency). The API returns JSON
# dicts and users can access fields with standard dict syntax.
#
# Type aliases below document the expected shapes.
# ============================================================================

# All API responses are dict[str, Any]. These aliases document expected shapes.

ChallengeInstructions = dict[str, Any]
"""Challenge instructions dict with keys: code, expires_at, instruction?, send_to?,
send_to_formatted?, deep_link?, message?, record_type?, record_name?, record_value?,
file_path?, file_content?, file_url?, method?, magic_link?, email_sent?, email_to?"""

ProofToken = dict[str, Any]
"""Proof token dict with keys: token, expires_at"""

Verification = dict[str, Any]
"""Verification dict with keys: id, type, channel, status, identifier,
attempts?, max_attempts?, challenge?, proof?, verified_at?, verified_data?, created_at"""

VerificationRequest = dict[str, Any]
"""Verification request dict with keys: id, reference_id?, status, action_type,
action_context?, assets, partial_ok?, validity_requirement?, verification_url,
redirect_url?, callback_url?, expires_at, completed_at?, created_at"""

Session = dict[str, Any]
"""Session dict with keys: id, channel, status, deep_link?, qr_code?,
instructions?, phone_number?, verified_at?, verification_id?, proof?, expires_at, created_at?"""

ProofValidation = dict[str, Any]
"""Proof validation dict with keys: valid, reason?, message?, verification?, revoked_at?, revoked_reason?"""

RevokedProof = dict[str, Any]
"""Revoked proof dict with keys: proof_id, revoked_at, reason?"""

RevocationList = dict[str, Any]
"""Revocation list dict with keys: revoked, issued_at, count, signature, kid"""

RevokeResponse = dict[str, Any]
"""Revoke response dict with keys: success, verification_id, revoked_at, reason"""

WebhookDelivery = dict[str, Any]
"""Webhook delivery dict with keys: id, url, event_type, status, attempts, max_attempts,
response_status, error_message, last_attempt_at, next_retry_at, delivered_at,
verification_request_id, payload?, response_body?, created_at, updated_at?"""

WebhookRetryResponse = dict[str, Any]
"""Webhook retry response dict with keys: success, message, delivery_id, next_retry_at"""

WebhookDeliveryList = dict[str, Any]
"""Webhook delivery list dict with keys: deliveries, pagination"""

PaginatedList = dict[str, Any]
"""Paginated list dict with keys: data, pagination"""

OfflineVerificationResult = dict[str, Any]
"""Offline verification result dict with keys: valid, payload?, error?"""

ProofStatus = dict[str, Any]
"""Proof status dict with keys: proof_id, status, is_valid, is_revoked,
revoked_at?, revoked_reason?, expires_at?, is_expired, verified_at?"""

WebhookDeliveryStats = dict[str, Any]
"""Webhook delivery stats dict with keys: total, by_status
(pending, delivered, failed), delivery_rate, recent_failures_24h"""

ResendResponse = dict[str, Any]
"""Resend response dict with keys: success, message, expires_at"""

TestVerifyResponse = dict[str, Any]
"""Test verify response dict with keys: id, type, channel, status, identifier,
verified_at?, proof_token?, proof_expires_at?, test_mode"""

DomainVerification = dict[str, Any]
"""Domain verification dict with keys: id, domain, status, verification_method?,
dns_record?, http_file?, provider?, verified_at?"""

DomainCheckResponse = dict[str, Any]
"""Domain check response dict with keys: id, domain, status, verified?,
verified_at?, check_count?"""

VerifiedUser = dict[str, Any]
"""Verified user dict with keys: external_user_id, verification_count,
types_verified, verifications, first_verified_at?, last_verified_at?"""
