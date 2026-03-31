"""Type definitions for the proof.holdings API.

AUTO-GENERATED — DO NOT EDIT
Source: npm run sdk:generate-types (scripts/generate-sdk-types.ts)
Generated from OpenAPI spec via src/openapi/registry.ts
"""

from __future__ import annotations

from typing import Any, Literal, Optional, Union
from typing_extensions import NotRequired, TypedDict

# ============================================================================
# Common
# ============================================================================

class APIInfo(TypedDict):
    name: str
    version: str
    description: str
    links: dict[str, Any]

class ErrorDetail(TypedDict):
    """Field-level validation error detail"""

    field: str
    message: str
    code: str

class ErrorResponse(TypedDict):
    """Standard error response format"""

    error: dict[str, Any]

class HealthResponse(TypedDict):
    """Detailed health check response"""

    status: Literal["ok", "healthy", "degraded", "unhealthy"]
    timestamp: Union[str, float]

class LivenessResponse(TypedDict):
    """Liveness probe response — always returns ok if the process is alive"""

    status: Literal["ok"]
    timestamp: str

ObjectId = str

class IdParam(TypedDict):
    id: "ObjectId"

class PaginationResponse(TypedDict):
    """Pagination info in list responses"""

    page: NotRequired[int]
    limit: NotRequired[int]
    total: NotRequired[int]
    pages: NotRequired[int]
    hasMore: NotRequired[bool]
    nextCursor: NotRequired[str]

RevocationReason = Literal[
    "user_request", "fraud", "key_compromise", "asset_transferred", "other",
]

class SuccessResponse(TypedDict):
    """Generic success response"""

    success: bool
    message: NotRequired[str]

# ============================================================================
# Verification Requests
# ============================================================================

class ActionContext(TypedDict):
    """Context for custom and confirmation action types"""

    title: NotRequired[str]
    description: NotRequired[str]
    amount: NotRequired[float]
    currency: NotRequired[str]
    entity: NotRequired[str]

ActionType = Literal[
    "verification", "2fa", "login", "custom", "confirmation", "authorization",
]

class CancelRequestResponse(TypedDict):
    success: bool
    status: Literal["cancelled"]

class ReferenceIdParam(TypedDict):
    referenceId: str

class RequestedAsset(TypedDict):
    """Asset to be verified in a multi-asset request"""

    type: "VerificationType"
    identifier: NotRequired[Optional[str]]
    channel: NotRequired[Any]
    allowed_channels: NotRequired[list["VerificationChannel"]]
    required: NotRequired[bool]

# ============================================================================
# Domains
# ============================================================================

class AddDomainRequest(TypedDict):
    """Request body for adding a domain"""

    domain: str
    project_id: NotRequired[str]
    for_email_sending: NotRequired[bool]
    verification_method: NotRequired[Literal["auto_dns", "manual_dns", "http_file", "email"]]

class ConnectCloudflareRequest(TypedDict):
    """Request body for connecting a Cloudflare API token"""

    api_token: str

class ConnectGoDaddyRequest(TypedDict):
    """Request body for connecting GoDaddy API credentials"""

    api_key: str
    api_secret: str

class ConnectProviderRequest(TypedDict):
    """Request body for connecting a generic DNS provider"""

    credentials: dict[str, Any]

DomainStatus = Literal["pending", "verified", "failed"]

class Domain(TypedDict):
    """Domain record"""

    id: "ObjectId"
    domain: str
    status: "DomainStatus"
    verification_method: NotRequired[str]
    provider: NotRequired[str]
    email_sending_enabled: NotRequired[bool]
    project_id: NotRequired["ObjectId"]
    created_at: str
    updated_at: str
    verified_at: NotRequired[str]

class DomainCheckResponse(TypedDict):
    """Domain verification check result"""

    id: "ObjectId"
    domain: str
    status: Literal["pending", "verified"]
    verified: bool
    verified_at: Optional[str]
    check_count: int

class DomainVerificationResponse(TypedDict):
    """Domain verification initiation response"""

    id: "ObjectId"
    domain: str
    status: Literal["pending", "verified"]
    verification_method: str
    dns_record: dict[str, Any]
    http_file: dict[str, Any]
    provider: dict[str, Any]

class ProviderParam(TypedDict):
    id: "ObjectId"
    provider: str

class SetupEmailSendingRequest(TypedDict):
    """Request body for setting up email sending on a domain"""

    from_email: NotRequired[str]

class StartDomainVerificationRequest(TypedDict):
    """Request body for starting B2B domain verification"""

    domain: str
    customer_id: NotRequired[str]
    verification_method: NotRequired[Literal["manual_dns", "http_file"]]

class StartEmailVerificationRequest(TypedDict):
    """Request body for starting email-based domain verification"""

    email_prefix: NotRequired[Literal["admin", "administrator", "webmaster", "hostmaster", "postmaster"]]

class StartUserDomainVerificationRequest(TypedDict):
    """Request body for starting user domain verification"""

    domain: str
    channel: NotRequired[Literal["dns", "http"]]

# ============================================================================
# Emails
# ============================================================================

class AddEmailRequest(TypedDict):
    """Request body for adding a new email"""

    email: str

class UserEmail(TypedDict):
    """User email address"""

    id: "ObjectId"
    email: str
    is_primary: bool
    verified_at: NotRequired[str]
    created_at: str

class VerifyCodeRequest(TypedDict):
    """OTP code submission"""

    code: str

# ============================================================================
# Phones
# ============================================================================

class AddPhoneRequest(TypedDict):
    """Request body for adding a new phone"""

    channel: Literal["telegram", "whatsapp", "sms"]

class UserPhone(TypedDict):
    """User phone number"""

    id: "ObjectId"
    phone: str
    is_primary: bool
    verified_at: NotRequired[str]
    created_at: str
    channel_metadata: NotRequired[dict[str, Any]]

# ============================================================================
# Assets
# ============================================================================

AssetStatus = Literal["active", "expired", "revoked"]

class ListAssetsQuery(TypedDict):
    """Query parameters for listing assets"""

    type: NotRequired[Literal["phone", "email", "domain", "social", "wallet"]]
    status: NotRequired["AssetStatus"]

class AssetIndexParam(TypedDict):
    id: "ObjectId"
    assetIndex: str

class UserAsset(TypedDict):
    """User verified asset"""

    id: "ObjectId"
    type: "VerificationType"
    channel: "VerificationChannel"
    identifier: str
    status: "AssetStatus"
    verified_at: NotRequired[str]
    expires_at: NotRequired[str]
    created_at: str

# ============================================================================
# Auth
# ============================================================================

AuthChannel = Literal["telegram", "whatsapp", "sms", "email"]

class AuthSessionIdParam(TypedDict):
    sessionId: str

class AuthSessionListItem(TypedDict):
    """Active session entry"""

    id: str
    channel: "AuthChannel"
    user_agent: NotRequired[str]
    created_at: str
    expires_at: str
    is_current: bool

AuthSessionStatus = Literal["pending", "verified", "expired"]

class AuthSessionResponse(TypedDict):
    """Auth session response"""

    id: str
    type: Literal["login"]
    channel: "AuthChannel"
    status: "AuthSessionStatus"
    deep_link: NotRequired[str]
    qr_code: NotRequired[str]
    expires_at: str
    instructions: NotRequired[str]
    verified_at: NotRequired[str]
    user_id: NotRequired[str]

class CreateAuthSessionRequest(TypedDict):
    """Request body for creating a new auth session (login)"""

    channel: "AuthChannel"
    phone_number: NotRequired[str]
    email: NotRequired[str]

class ExchangeTokenRequest(TypedDict):
    """Request body for exchanging a one-time token for JWT"""

    token: str

class ExchangeTokenResponse(TypedDict):
    """Token exchange response"""

    success: bool
    jwt: str
    expiresAt: str

class ListSessionsResponse(TypedDict):
    """List of active sessions"""

    sessions: list["AuthSessionListItem"]
    total: int

class LogoutAllResponse(TypedDict):
    """Logout all devices response"""

    success: bool
    message: str
    invalidated: int

class AuthUser(TypedDict):
    """Authenticated user profile"""

    id: "ObjectId"
    phone_numbers: NotRequired[list[dict[str, Any]]]
    emails: NotRequired[list[dict[str, Any]]]
    created_at: str

class SubmitAuthCodeRequest(TypedDict):
    """Request body for submitting an auth OTP code"""

    code: str

class TokenParam(TypedDict):
    token: str

class TransferTokenResponse(TypedDict):
    """Transfer token generation response"""

    success: bool
    token: str
    url: str
    expiresIn: int

# ============================================================================
# Authorizations
# ============================================================================

AuthorizationChannel = Literal["whatsapp", "telegram", "sms", "email"]

AuthorizationScope = Literal["confirmations"]

AuthorizationStatus = Literal[
    "pending", "active", "expired", "revoked", "denied",
]

class AuthorizationExportQuery(TypedDict):
    format: NotRequired[Literal["csv", "json"]]
    from_: NotRequired[str]
    to: NotRequired[str]
    status: NotRequired["AuthorizationStatus"]

class AuthorizationListQuery(TypedDict):
    page: NotRequired[int]
    limit: NotRequired[int]
    status: NotRequired["AuthorizationStatus"]
    phone: NotRequired[str]
    channel: NotRequired["AuthorizationChannel"]

class Authorization(TypedDict):
    """Authorization granting permission to send confirmations via a specific channel"""

    id: "ObjectId"
    status: "AuthorizationStatus"
    hitl_id: Any
    recipient: NotRequired[Optional[str]]
    phone: NotRequired[Optional[str]]
    channel: "AuthorizationChannel"
    scope: "AuthorizationScope"
    business_name: str
    verification_id: NotRequired["ObjectId"]
    authorized_at: NotRequired[str]
    expires_at: str
    revoked_at: NotRequired[str]
    revocation_reason: NotRequired[str]
    confirmations_sent: int
    last_used_at: NotRequired[str]
    created_at: str
    updated_at: str

class AuthorizationListResponse(TypedDict):
    data: list["Authorization"]
    pagination: dict[str, Any]

class CreateAuthorizationBody(TypedDict):
    """Request body for creating an authorization"""

    hitl_id: Any
    recipient: str
    phone: str
    channel: "AuthorizationChannel"
    scope: NotRequired[Any]
    business_name: str
    business_profile_id: NotRequired[Any]
    expires_in: NotRequired[int]

class CreateAuthorizationResponse(TypedDict):
    """Response from creating an authorization request"""

    id: "ObjectId"
    status: "AuthorizationStatus"
    hitl_id: Any
    recipient: NotRequired[Optional[str]]
    phone: NotRequired[Optional[str]]
    channel: "AuthorizationChannel"
    scope: "AuthorizationScope"
    business_name: str
    authorization_url: str
    expires_at: str
    created_at: str

class RevokeAuthorizationBody(TypedDict):
    reason: NotRequired[str]

# ============================================================================
# Billing
# ============================================================================

BillingPlan = Literal["pro", "business", "white_label", "enterprise"]

class CheckoutRequest(TypedDict):
    """Request body for creating a Stripe checkout session"""

    plan: "BillingPlan"
    success_url: str
    cancel_url: str

class CheckoutResponse(TypedDict):
    """Checkout session creation response"""

    url: str

class PortalRequest(TypedDict):
    """Request body for creating a Stripe billing portal session"""

    return_url: str

class PortalResponse(TypedDict):
    """Billing portal session creation response"""

    url: str

# ============================================================================
# Settings
# ============================================================================

class BrandingSettings(TypedDict):
    """Branding settings"""

    business_name: NotRequired[str]
    logo_url: NotRequired[Optional[str]]
    primary_color: NotRequired[str]
    support_email: NotRequired[str]
    email_theme: NotRequired[Literal["dark", "light"]]

class UpdateSettingsRequest(TypedDict):
    """Request body for updating user settings"""

    branding: NotRequired["BrandingSettings"]

class UsageQueryParams(TypedDict):
    """Usage query parameters"""

    period: NotRequired[str]
    months: NotRequired[int]

# ============================================================================
# Verifications
# ============================================================================

class Challenge(TypedDict):
    """Challenge details for verification"""

    code: NotRequired[str]
    instruction: NotRequired[str]
    expires_at: NotRequired[str]

class DNSProviderCredentials(TypedDict):
    """DNS provider credentials for auto-DNS verification"""

    provider: str
    api_token: NotRequired[str]
    api_key: NotRequired[str]
    api_secret: NotRequired[str]
    account_id: NotRequired[str]
    username: NotRequired[str]
    access_key_id: NotRequired[str]
    secret_access_key: NotRequired[str]
    region: NotRequired[str]

class ResendVerificationResponse(TypedDict):
    """Response after resending verification email"""

    success: bool
    message: str
    expires_at: str

class SubmitChallengeRequest(TypedDict):
    """Request body for submitting a challenge code"""

    challenge_code: str
    source_identifier: NotRequired[str]

class SubmitVerificationCodeRequest(TypedDict):
    """Request body for submitting a verification code"""

    code: str

VerificationChannel = Literal[
    "whatsapp", "telegram", "viber", "sms", "email", "dns", "http", "auto", "github", "google", "facebook", "x", "linkedin", "instagram", "youtube", "tiktok", "ethereum", "solana", "bitcoin", "coinbase", "kraken", "telegram_bot_token",
]

VerificationRequestStatus = Literal[
    "pending", "partial", "completed", "expired", "cancelled",
]

class VerificationRequestListQuery(TypedDict):
    page: NotRequired[int]
    limit: NotRequired[int]
    status: NotRequired["VerificationRequestStatus"]
    reference_id: NotRequired[str]

VerificationStatus = Literal[
    "pending", "verified", "failed", "expired", "revoked",
]

VerificationType = Literal[
    "phone", "email", "domain", "social", "wallet", "account", "telegram_bot",
]

class CreateVerificationRequest(TypedDict):
    """Request body for creating a new verification"""

    type: "VerificationType"
    channel: "VerificationChannel"
    identifier: str
    external_user_id: NotRequired[str]
    client_metadata: NotRequired[dict[str, Any]]
    dns_provider: NotRequired[Any]
    email_prefix: NotRequired[Literal["admin", "administrator", "webmaster", "hostmaster", "postmaster"]]
    bot_token: NotRequired[str]
    proof_expiry_days: NotRequired[int]

class CreateVerificationRequestBody(TypedDict):
    """Request body for creating a multi-asset verification request"""

    reference_id: NotRequired[str]
    project_id: NotRequired[Any]
    public_profile_id: NotRequired[Any]
    assets: list["RequestedAsset"]
    action_type: NotRequired[Any]
    action_context: NotRequired["ActionContext"]
    validity_requirement: NotRequired[str]
    partial_ok: NotRequired[bool]
    redirect_url: NotRequired[str]
    callback_url: NotRequired[str]
    expires_in: NotRequired[int]
    proof_expiry_days: NotRequired[int]

class TestVerifyResponse(TypedDict):
    id: "ObjectId"
    type: "VerificationType"
    channel: str
    status: Literal["verified"]
    identifier: str
    verified_at: str
    proof_token: str
    proof_expires_at: str
    test_mode: bool

class Verification(TypedDict):
    """Verification object"""

    id: "ObjectId"
    type: "VerificationType"
    channel: "VerificationChannel"
    identifier: str
    status: "VerificationStatus"
    challenge: NotRequired["Challenge"]
    proof: NotRequired["Proof"]
    external_user_id: NotRequired[str]
    attempts: NotRequired[int]
    max_attempts: NotRequired[int]
    created_at: str
    updated_at: NotRequired[str]
    verified_at: NotRequired[str]

class VerificationListQuery(TypedDict):
    page: NotRequired[int]
    limit: NotRequired[int]
    status: NotRequired["VerificationStatus"]
    type: NotRequired["VerificationType"]

class VerificationListResponse(TypedDict):
    """Paginated list of verifications"""

    data: list["Verification"]
    pagination: "PaginationResponse"

class VerificationRequest(TypedDict):
    """Multi-asset verification request"""

    id: "ObjectId"
    reference_id: NotRequired[str]
    status: "VerificationRequestStatus"
    assets: list[dict[str, Any]]
    action_type: "ActionType"
    action_context: NotRequired["ActionContext"]
    partial_ok: bool
    verification_url: NotRequired[str]
    redirect_url: NotRequired[str]
    progress: NotRequired[dict[str, Any]]
    expires_at: str
    completed_at: NotRequired[str]
    created_at: str
    updated_at: NotRequired[str]

class VerificationRequestListResponse(TypedDict):
    data: list["VerificationRequest"]
    pagination: dict[str, Any]

class VerificationRequestProofsResponse(TypedDict):
    """Proof tokens for verified assets in a verification request"""

    proofs: list[dict[str, Any]]

# ============================================================================
# Other
# ============================================================================

class ChatIdDiscoveryPollResponse(TypedDict):
    """Chat ID discovery poll result"""

    status: Literal["pending", "completed"]
    chat_id: NotRequired[str]

class ChatIdDiscoveryResponse(TypedDict):
    """Chat ID discovery token and Telegram deeplink"""

    token: str
    deep_link: str
    qr_code: str
    expires_in: int

ConfirmationStatus = Literal["pending", "approved", "denied"]

HitlChannelType = Literal["telegram", "whatsapp", "browser"]

class HitlChannel(TypedDict):
    """A messaging channel configured for HITL approvals"""

    type: "HitlChannelType"
    config: dict[str, Any]

class CreateHitlBody(TypedDict):
    """Request body for creating a HITL configuration"""

    name: str
    channels: list["HitlChannel"]
    timeout_seconds: NotRequired[float]

HitlStatus = Literal["active", "archived"]

class HitlListQuery(TypedDict):
    """Query parameters for listing HITL configurations"""

    page: NotRequired[int]
    limit: NotRequired[int]
    status: NotRequired["HitlStatus"]

class Confirmation(TypedDict):
    """A HITL confirmation request"""

    id: "ObjectId"
    hitl_id: Any
    message: str
    metadata: NotRequired[Optional[dict[str, Any]]]
    status: "ConfirmationStatus"
    timeout_seconds: int
    response: NotRequired[Optional[dict[str, Any]]]
    timeout_at: NotRequired[Optional[str]]
    proof_token: NotRequired[Optional[str]]
    resolved_at: NotRequired[Optional[str]]
    environment: Literal["production", "test"]
    created_at: str
    updated_at: str

class ConfirmationListQuery(TypedDict):
    """Query parameters for listing confirmations"""

    page: NotRequired[int]
    limit: NotRequired[int]
    status: NotRequired["ConfirmationStatus"]
    hitl_id: NotRequired["ObjectId"]

class ConfirmationListResponse(TypedDict):
    """Paginated list of confirmations"""

    data: list["Confirmation"]
    pagination: dict[str, Any]

class CreateConfirmationBody(TypedDict):
    """Request body for creating a confirmation"""

    hitl_id: Any
    message: str
    proof_expiry_days: NotRequired[int]

class Hitl(TypedDict):
    """HITL configuration with messaging channels and timeout"""

    id: "ObjectId"
    user_id: Any
    name: NotRequired[Optional[str]]
    profile_id: NotRequired[Any]
    channels: list["HitlChannel"]
    timeout_seconds: int
    status: "HitlStatus"
    keypair: Optional[dict[str, Any]]
    created_at: str
    updated_at: str

class HitlAuthorizationResponse(TypedDict):
    """Response from requesting authorization consent for HITL channels"""

    hitl_id: "ObjectId"
    results: list[dict[str, Any]]
    message: str

class HitlListResponse(TypedDict):
    """Paginated list of HITL configurations"""

    data: list["Hitl"]
    pagination: dict[str, Any]

class UpdateHitlBody(TypedDict):
    """Request body for updating a HITL configuration"""

    name: NotRequired[Optional[str]]
    channels: NotRequired[list["HitlChannel"]]
    timeout_seconds: NotRequired[float]

# ============================================================================
# Profiles
# ============================================================================

class ClaimUsernameRequest(TypedDict):
    """Request body for claiming a username"""

    username: str

class CustomLink(TypedDict):
    """Custom link on a public profile"""

    title: str
    url: str
    icon: NotRequired[str]
    is_visible: NotRequired[bool]
    display_order: NotRequired[int]

class ProfileIdParam(TypedDict):
    profileId: str

class ProfileProofEntry(TypedDict):
    """Proof display configuration for a profile"""

    asset_id: str
    is_visible: NotRequired[bool]
    mask_level: NotRequired[Literal["full", "partial", "hidden"]]
    display_order: NotRequired[int]
    label: NotRequired[str]

class ProfileTheme(TypedDict):
    """Profile theme customization"""

    primary_color: NotRequired[str]
    background_type: NotRequired[Literal["solid", "gradient"]]
    background_color: NotRequired[str]
    gradient_start: NotRequired[str]
    gradient_end: NotRequired[str]
    font_style: NotRequired[Literal["default", "modern", "classic"]]

class CreateProfileRequest(TypedDict):
    """Request body for creating a new profile"""

    display_name: NotRequired[str]
    bio: NotRequired[str]
    avatar_url: NotRequired[str]
    business_name: NotRequired[str]
    is_business: NotRequired[bool]
    is_public: NotRequired[bool]
    is_primary: NotRequired[bool]
    theme: NotRequired["ProfileTheme"]

class UpdateProfileProofsRequest(TypedDict):
    """Request body for updating which proofs are displayed on a profile"""

    proofs: list["ProfileProofEntry"]

class UpdateProfileRequest(TypedDict):
    """Request body for updating a profile"""

    display_name: NotRequired[str]
    bio: NotRequired[str]
    avatar_url: NotRequired[Optional[str]]
    business_name: NotRequired[str]
    is_business: NotRequired[bool]
    is_public: NotRequired[bool]
    is_primary: NotRequired[bool]
    show_verification_dates: NotRequired[bool]
    show_proof_channels: NotRequired[bool]
    theme: NotRequired["ProfileTheme"]
    custom_links: NotRequired[list["CustomLink"]]

class UsernameParam(TypedDict):
    username: str

class PublicProfile(TypedDict):
    """Public profile"""

    id: "ObjectId"
    display_name: NotRequired[str]
    bio: NotRequired[str]
    avatar_url: NotRequired[str]
    business_name: NotRequired[str]
    is_business: NotRequired[bool]
    is_public: bool
    is_primary: NotRequired[bool]
    username: NotRequired[str]
    theme: NotRequired["ProfileTheme"]
    custom_links: NotRequired[list["CustomLink"]]
    proofs: NotRequired[list[dict[str, Any]]]
    created_at: str
    updated_at: str

# ============================================================================
# API Keys
# ============================================================================

class CreateAPIKeyRequest(TypedDict):
    """Request body for creating an API key"""

    name: NotRequired[str]
    environment: NotRequired[Literal["production", "test"]]
    scopes: NotRequired[list[str]]

class APIKeyResponse(TypedDict):
    """API key (key value only shown on creation)"""

    id: "ObjectId"
    name: str
    key_prefix: str
    environment: Literal["production", "test"]
    scopes: list[str]
    created_at: str
    last_used_at: NotRequired[str]

# ============================================================================
# DNS Credentials
# ============================================================================

class CreateProviderCredentialRequest(TypedDict):
    """Request body for creating stored DNS provider credentials"""

    provider: str
    credentials: dict[str, Any]

# ============================================================================
# Sessions
# ============================================================================

class CreateSessionRequest(TypedDict):
    """Request body for creating a phone verification session"""

    phone: str
    channel: NotRequired[Literal["whatsapp", "telegram", "viber", "sms"]]

class Session(TypedDict):
    """Phone verification session"""

    id: "ObjectId"
    status: Literal["pending", "verified", "expired"]
    challenge: NotRequired["Challenge"]
    proof: NotRequired["Proof"]
    created_at: str
    expires_at: str

SessionChannel = Literal["telegram", "whatsapp", "viber", "sms"]

class SessionIdParam(TypedDict):
    id: str

# ============================================================================
# Account
# ============================================================================

class DeleteAccountRequest(TypedDict):
    """Request body for final account deletion"""

    session_id: str

class InitiateAccountDeletionRequest(TypedDict):
    """Request body for initiating account deletion"""

    channel: NotRequired[Literal["telegram", "whatsapp", "sms", "email"]]

# ============================================================================
# Verified Users
# ============================================================================

class ExternalUserIdParam(TypedDict):
    externalUserId: str

class VerifiedUserDetail(TypedDict):
    """Detailed verification info for a specific external user"""

    external_user_id: str
    verification_count: int
    types_verified: list["VerificationType"]
    verifications: list[dict[str, Any]]

class VerifiedUserSummary(TypedDict):
    """Aggregated verification summary for an external user"""

    external_user_id: str
    verification_count: int
    types_verified: list["VerificationType"]
    verifications: list[dict[str, Any]]
    first_verified_at: NotRequired[str]
    last_verified_at: NotRequired[str]

class VerifiedUserListResponse(TypedDict):
    """Paginated list of verified users"""

    data: list["VerifiedUserSummary"]
    pagination: dict[str, Any]

# ============================================================================
# Proofs
# ============================================================================

class JWK(TypedDict):
    """JSON Web Key"""

    kty: str
    n: str
    e: str
    use: Literal["sig"]
    alg: Literal["RS256"]
    kid: str

class JWKS(TypedDict):
    """JSON Web Key Set for offline proof verification"""

    keys: list["JWK"]

class Proof(TypedDict):
    """Proof token after successful verification"""

    token: str
    expires_at: str

class RevokeProofRequest(TypedDict):
    """Request body for revoking a proof"""

    reason: NotRequired[Any]

class RevokeProofResponse(TypedDict):
    success: bool
    revoked_at: str

class RevokedProof(TypedDict):
    """Entry in the revocation list"""

    proof_id: str
    revoked_at: str
    reason: "RevocationReason"

class RevocationList(TypedDict):
    """Signed list of revoked proofs"""

    revoked: NotRequired[list["RevokedProof"]]
    generated_at: NotRequired[str]
    signature: NotRequired[str]

class ValidateProofRequest(TypedDict):
    """Request body for validating a proof token"""

    proof_token: str

class ProofStatusResponse(TypedDict):
    """Proof status check result"""

    proof_id: "ObjectId"
    status: "VerificationStatus"
    is_valid: bool
    is_revoked: bool
    revoked_at: Optional[str]
    revoked_reason: Optional[str]
    expires_at: Optional[str]
    is_expired: bool

class ValidateProofResponse(TypedDict):
    """Proof validation result. Returns verification details when valid, or reason/message when invalid."""

    valid: bool
    verification: NotRequired[dict[str, Any]]
    reason: NotRequired[str]
    message: NotRequired[str]
    revoked_at: NotRequired[str]
    revoked_reason: NotRequired[str]

# ============================================================================
# Templates
# ============================================================================

MessageType = Literal[
    "verification_request", "verification_success", "verification_expired", "login_request", "login_success", "2fa_request", "2fa_success",
]

TemplateChannel = Literal["telegram", "whatsapp", "sms", "email"]

class ChannelTypeParam(TypedDict):
    id: "ObjectId"
    channel: "TemplateChannel"
    type: "MessageType"

class Template(TypedDict):
    """Message template"""

    id: NotRequired["ObjectId"]
    channel: "TemplateChannel"
    message_type: "MessageType"
    subject: NotRequired[str]
    body: str
    button_text: NotRequired[str]
    button_url_template: NotRequired[str]
    is_active: NotRequired[bool]
    version: NotRequired[int]
    updated_at: NotRequired[str]

class TemplateContent(TypedDict):
    """Template content fields"""

    subject: NotRequired[str]
    body: str
    button_text: NotRequired[str]
    button_url_template: NotRequired[str]

class TemplatePathParam(TypedDict):
    channel: "TemplateChannel"
    messageType: "MessageType"

class TemplatePreviewRequest(TypedDict):
    """Request body for previewing a template"""

    channel: "TemplateChannel"
    message_type: "MessageType"
    subject: NotRequired[str]
    body: str
    button_text: NotRequired[str]
    button_url_template: NotRequired[str]

class TemplateRenderRequest(TypedDict):
    """Request body for rendering a template with variables"""

    channel: "TemplateChannel"
    message_type: "MessageType"
    variables: NotRequired[dict[str, Any]]

class TemplateVariable(TypedDict):
    """Available template variable"""

    name: str
    description: str

# ============================================================================
# Projects
# ============================================================================

class ProjectBranding(TypedDict):
    """Project branding settings"""

    business_name: NotRequired[str]
    logo_url: NotRequired[str]
    primary_color: NotRequired[str]
    support_email: NotRequired[str]

class CreateProjectRequest(TypedDict):
    """Request body for creating a project"""

    name: str
    description: NotRequired[str]
    branding: NotRequired["ProjectBranding"]

class ProjectCallbacks(TypedDict):
    """Project callback URLs"""

    success_url: NotRequired[str]
    failure_url: NotRequired[str]
    cancel_url: NotRequired[str]

class Project(TypedDict):
    """Project"""

    id: "ObjectId"
    name: str
    description: NotRequired[str]
    branding: NotRequired["ProjectBranding"]
    callbacks: NotRequired["ProjectCallbacks"]
    created_at: str
    updated_at: str

class UpdateProjectRequest(TypedDict):
    """Request body for updating a project"""

    name: NotRequired[str]
    description: NotRequired[str]
    branding: NotRequired["ProjectBranding"]
    callbacks: NotRequired["ProjectCallbacks"]

# ============================================================================
# Verify Flow
# ============================================================================

class StartAssetVerificationRequest(TypedDict):
    """Request body for starting asset verification in a verification request"""

    channel: Literal["telegram", "whatsapp", "sms", "email", "dns", "http", "telegram_bot_token"]
    identifier: NotRequired[str]
    bot_token: NotRequired[str]

class TryItRequest(TypedDict):
    """Request body for creating a demo verification request"""

    type: Literal["phone", "email", "domain"]
    identifier: str

# ============================================================================
# 2FA
# ============================================================================

TwoFAActionType = Literal[
    "api_key_view", "api_key_create", "api_key_revoke", "api_key_regenerate", "phone_add", "phone_remove", "email_add", "email_remove", "account_delete",
]

class Start2FARequest(TypedDict):
    """Request body for starting 2FA verification"""

    action_type: "TwoFAActionType"
    channel: Literal["telegram", "whatsapp", "sms", "email"]
    email_id: NotRequired[str]

# ============================================================================
# Webhook Deliveries
# ============================================================================

class WebhookDeliveryStats(TypedDict):
    """Webhook delivery statistics"""

    total: int
    delivered: int
    failed: int
    pending: int
    success_rate: float

WebhookDeliveryStatus = Literal["pending", "delivered", "failed"]

WebhookEventType = Literal[
    "verification_request.completed", "verification_request.partial", "verification_request.expired", "verification.completed", "confirmation.approved", "confirmation.denied", "proof.revoked",
]

class WebhookDelivery(TypedDict):
    """Webhook delivery record"""

    id: "ObjectId"
    verification_request_id: NotRequired["ObjectId"]
    event_type: "WebhookEventType"
    url: str
    status: "WebhookDeliveryStatus"
    attempts: int
    max_attempts: int
    last_attempt_at: NotRequired[str]
    next_retry_at: NotRequired[str]
    response_status: NotRequired[int]
    response_body: NotRequired[str]
    error_message: NotRequired[str]
    created_at: str
    updated_at: str

class RetryDeliveryResponse(TypedDict):
    success: bool
    delivery: "WebhookDelivery"

class WebhookDeliveryListQuery(TypedDict):
    page: NotRequired[int]
    limit: NotRequired[int]
    status: NotRequired["WebhookDeliveryStatus"]
    event_type: NotRequired["WebhookEventType"]
    verification_request_id: NotRequired[Any]

class WebhookDeliveryListResponse(TypedDict):
    data: list["WebhookDelivery"]
    pagination: dict[str, Any]

class WebhookProof(TypedDict):
    """Proof of a verified asset included in webhook payload"""

    type: "VerificationType"
    identifier: str
    verified_at: NotRequired[str]
    channel: "VerificationChannel"
    proof_token: NotRequired[str]

class WebhookPayload(TypedDict):
    """Outbound webhook payload sent to callback URLs on verification/confirmation events"""

    event: "WebhookEventType"
    request_id: "ObjectId"
    reference_id: NotRequired[str]
    status: "VerificationRequestStatus"
    action_type: "ActionType"
    action_context: NotRequired["ActionContext"]
    client_metadata: NotRequired[dict[str, Any]]
    completed_at: NotRequired[str]
    proofs: list["WebhookProof"]
    progress: dict[str, Any]
    test: NotRequired[bool]
