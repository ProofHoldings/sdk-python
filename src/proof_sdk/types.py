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

    # Deprecated values: "ok" — removed from the API; kept so code written for an earlier 1.x release keeps compiling, and dropped in the next major version.
    status: Literal["ok", "healthy", "degraded", "unhealthy", "unknown"]
    timestamp: Union[str, float]
    components: NotRequired[list[dict[str, Any]]]

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
    total_pages: NotRequired[int]

RevocationReason = Literal[
    "user_request", "fraud", "key_compromise", "asset_transferred", "other",
]

class SuccessResponse(TypedDict):
    """Generic success response"""

    success: bool
    message: NotRequired[str]

# ============================================================================
# Other
# ============================================================================

class AccountDeletionCancelTokenCheck(TypedDict):
    """The emailed cancel link still acts; nothing was changed by this read"""

    valid: Literal["true"]
    state: Literal["none", "scheduled", "on_hold", "in_progress"]
    scheduled_for: Optional[str]
    hold_reason: Optional[Literal["unpaid_invoice", "admin_suspended"]]
    display_name: Optional[str]

class AccountDeletionCancelledResponse(TypedDict):
    """The deletion is cancelled and the lock lifted"""

    success: bool
    ok: Literal["true"]
    was_state: Literal["none", "scheduled", "on_hold", "in_progress"]
    proofs_unsuspended: int
    proofs_kept_suspended: int
    not_restored: list[str]
    notice: list[dict[str, Any]]

class AccountDeletionScheduledResponse(TypedDict):
    """The account is locked and its deletion scheduled"""

    success: bool
    state: Literal["none", "scheduled", "on_hold", "in_progress"]
    scheduled_for: str
    already_scheduled: bool
    proofs_suspended: int
    notice: list[dict[str, Any]]

class AccountDeletionStatus(TypedDict):
    """Where the account stands with its deletion — the lock page's read"""

    state: Literal["none", "scheduled", "on_hold", "in_progress"]
    scheduled_for: Optional[str]
    requested_at: Optional[str]
    hold_reason: Optional[Literal["unpaid_invoice", "admin_suspended"]]
    final_invoice: Optional[dict[str, Any]]
    can_cancel: bool
    grace_days: int
    delayed: bool

class AccountExportJob(TypedDict):
    """One data export of the account — prepared in the background, downloadable only by the signed-in owner"""

    id: str
    status: Literal["preparing", "ready", "failed"]
    error: Optional[Literal["too_large", "internal"]]
    requested_at: str
    ready_at: Optional[str]
    expires_at: str
    downloaded_at: Optional[str]
    size_bytes: Optional[int]
    counts: dict[str, Any]
    download_path: Optional[str]

class AccountExportLatest(TypedDict):
    """The account's most recent export, or null"""

    latest: Optional["AccountExportJob"]

class AccountSessionIdParam(TypedDict):
    id: str

AccountSessionType = Literal["account_creation", "login"]

class AccountSummary(TypedDict):
    """One-call account snapshot for the dashboard home and AI agents"""

    as_of: str
    cache_age_seconds: float
    quota: dict[str, Any]
    request_health: dict[str, Any]
    top_channels: list[dict[str, Any]]
    channels_with_zero_completions: list[str]
    hitl_channels: NotRequired[dict[str, Any]]
    active_api_keys: float
    next_action: Optional[dict[str, Any]]

class AddCircleMemberChannelBody(TypedDict):
    """Request body for declaring a channel for a Circle member"""

    channel: Literal["telegram", "whatsapp"]
    identifier: str

class ApiKeyUsageQueryParams(TypedDict):
    """Per-API-key usage query parameters"""

    environment: NotRequired[Literal["production", "test"]]

class ApprovalLinkResponse(TypedDict):
    """Regenerated approval link for a pending confirmation"""

    approval_url: str

class ArtifactClaimLocation(TypedDict):
    """One place the claim check read, and what it found there"""

    id: Literal["npm_metadata", "mcp_registry", "endpoint_url", "host_server_card", "host_agent_card", "host_agent_card_legacy", "delegating_domains"]
    location: str
    url: Optional[str]
    result: Literal["found_in_force", "found_not_in_force", "found_other_artifact", "found_unverifiable", "nothing_published", "not_applicable", "unchecked"]
    reason: Optional[Literal["unreachable", "not_json", "too_large", "insecure_redirect", "timed_out", "rate_limited", "status_unavailable", "depends_on_unread_location", "invalid_pointer", "dns_lookup_failed", "ambiguous_entry"]]
    detail: str
    checked_at: str

class ArtifactClaimProfileLink(TypedDict):
    """A public profile of the delegating account that shows the principal domain. Exactly one of the two fields is present"""

    username: NotRequired[str]
    profile_id: NotRequired[str]

class ArtifactClaimDelegation(TypedDict):
    """An in-force delegation whose token was found in at least one checked location"""

    principal: str
    proof_id: str
    scope: list[str]
    issued_at: str
    expires_at: str
    token: str
    found_at: list[Literal["npm_metadata", "mcp_registry", "endpoint_url", "host_server_card", "host_agent_card", "host_agent_card_legacy", "delegating_domains"]]
    profile: Optional["ArtifactClaimProfileLink"]

class ArtifactClaim(TypedDict):
    """Whether a domain has published a delegation for this exact artifact, and every place that was checked. A delegation attests who authorized the artifact — not that it is safe, audited or endorsed"""

    delegate: str
    delegate_type: Literal["url", "purl"]
    artifact_path: Optional[str]
    claim: Literal["claimed", "no_claim_found"]
    checked_at: str
    locations: list["ArtifactClaimLocation"]
    delegations: list["ArtifactClaimDelegation"]
    listing: Optional[dict[str, Any]]

class ArtifactClaimedList(TypedDict):
    """Artifacts whose stored answer is `claimed` and which have a page, ordered by delegate"""

    data: list[dict[str, Any]]
    pagination: dict[str, Any]

AssetChannel = Literal[
    "whatsapp", "telegram", "sms", "email", "dns", "http", "auto", "github", "google", "facebook", "x", "linkedin", "instagram", "youtube", "tiktok", "ethereum", "solana", "bitcoin", "coinbase", "kraken", "telegram_bot_token", "otp", "magic_link",
]

class AssetRevocationItem(TypedDict):
    asset_id: str
    outcome: Literal["revoked", "already_revoked", "not_found"]
    type: NotRequired[Literal["phone", "email", "domain", "social", "wallet", "telegram_bot"]]
    identifier: NotRequired[str]
    revoked_asset_ids: NotRequired[list[str]]
    delegations_revoked: NotRequired[list[dict[str, Any]]]
    domain_status: NotRequired[Optional[Literal["pending", "verifying", "verified", "failed", "expired", "revoking", "reverification_required"]]]

class AccountSessionResponse(TypedDict):
    """Account-session response. Same wire format whether the request created a new account or pivoted to login — the `type` field distinguishes the outcome."""

    id: str
    type: "AccountSessionType"
    channel: "AuthChannel"
    status: "AuthSessionStatus"
    deep_link: NotRequired[str]
    qr_code: NotRequired[str]
    qr_text: NotRequired[str]
    sms_code: NotRequired[str]
    sms_message: NotRequired[str]
    email: NotRequired[str]
    email_sent: NotRequired[bool]
    email_error: NotRequired[str]
    expires_at: str
    instructions: NotRequired[str]
    verified_at: NotRequired[str]
    user_id: NotRequired[str]
    created_at: NotRequired[str]

class AutoTopUpRequest(TypedDict):
    """Switch auto top-up on or off. Switching it on needs a card saved by an earlier top-up."""

    enabled: bool
    amount: NotRequired[Union[Literal["10"], Literal["50"], Literal["200"]]]

class BalanceResponse(TypedDict):
    """The prepaid balance, from which proofs past the plan's included amount are drawn"""

    billing_enabled: bool
    balance: dict[str, Any]
    low_balance_threshold: int
    top_up_amounts: list[int]
    auto_top_up: dict[str, Any]

class ChatIdDiscoveryPollResponse(TypedDict):
    """Chat ID discovery poll result"""

    status: Literal["pending", "completed"]
    chat_id: NotRequired[str]

class ChatIdDiscoveryResponse(TypedDict):
    """Chat ID discovery token and Telegram deeplink"""

    token: str
    deep_link: str
    qr_code: str
    qr_text: str
    expires_in: int

class CircleMemberInput(TypedDict):
    """A Circle member to create (name + optional declared channels)"""

    name: str
    telegram_chat_id: NotRequired[str]
    whatsapp_phone: NotRequired[str]

CircleStatus = Literal["active", "archived"]

ConfirmationStatus = Literal["pending", "approved", "denied"]

ConfirmationStatusFilter = Literal["pending", "approved", "denied", "expired"]

class CreateAccountRequest(TypedDict):
    """Request body for creating an account-bootstrap session. The server transparently pivots to a login session when the submitted identity already belongs to an active User, so the agent polls identically regardless of outcome."""

    channel: "AuthChannel"
    phone_number: NotRequired[str]
    email: NotRequired[str]

class CreateCircleMemberBody(TypedDict):
    """Request body for adding a member to a Circle"""

    name: str
    whatsapp_phone: NotRequired[str]

class DelegateIdentifier(TypedDict):
    """Typed delegate identifier"""

    type: Literal["url", "purl"]
    value: str

class CreateDelegationRequest(TypedDict):
    """Create a delegation from a proven domain to an artifact"""

    control_proof: str
    delegate: "DelegateIdentifier"
    scope: list[str]
    expires_in: NotRequired[int]

HitlChannel = Union[dict[str, Any], dict[str, Any]]

HitlChannelType = Literal["telegram", "whatsapp", "browser"]

HitlStatus = Literal["pending", "active", "archived"]

class HitlListQuery(TypedDict):
    """Query parameters for listing HITL configurations"""

    page: NotRequired[int]
    limit: NotRequired[int]
    status: NotRequired["HitlStatus"]
    environment: NotRequired[Literal["production", "test"]]
    profile_id: NotRequired[str]

class IdentifierRemovalPreview(TypedDict):
    """What removing a phone or email would do; `allowed: false` carries the reason instead of the counts."""

    allowed: bool
    blocked: Optional[dict[str, Any]]
    type: NotRequired[Literal["phone", "email"]]
    identifier: NotRequired[str]
    is_primary: NotRequired[bool]
    proofs: NotRequired[int]
    authorizations: NotRequired[int]
    hitl_configs_without_approver: NotRequired[list[dict[str, Any]]]
    circles: NotRequired[int]
    new_primary: NotRequired[Optional[dict[str, Any]]]
    lookalike_watch: NotRequired[Literal["repointed", "canceled", "unchanged"]]
    notice_to: NotRequired[list[Literal["email", "telegram", "whatsapp"]]]

class IdentifierRemovedResponse(TypedDict):
    """The cascade a removal performed, line by line — the same lines the notice carries."""

    success: Literal["true"]
    type: Literal["phone", "email"]
    removed_id: str
    identifier: str
    proofs_revoked: int
    authorizations_revoked: int
    hitl_configs_without_approver: list[dict[str, Any]]
    circles_repointed: int
    new_primary: Optional[dict[str, Any]]
    lookalike_watch: Literal["repointed", "canceled", "unchanged"]
    sessions_invalidated: int
    sessions_signed_out: bool
    notice: list[dict[str, Any]]

class IdentityChallengeCreate(TypedDict):
    """Create a cross-channel identity challenge (Proof of Me)"""

    circle_id: str
    member_id: str
    suspicious_channel: NotRequired[Literal["telegram", "whatsapp"]]

class IdentityChallengeResponse(TypedDict):
    """An identity challenge (Proof of Me)"""

    id: str
    status: Literal["pending", "confirmed", "denied", "cancelled", "failed", "expired", "revoked", "suspended"]
    channel: NotRequired[str]
    confirm_channel: NotRequired[str]
    single_channel_warning: NotRequired[bool]
    circle_id: NotRequired[Optional[str]]
    is_drill: NotRequired[bool]
    proof_id: NotRequired[Optional[str]]
    proof_token: NotRequired[Optional[str]]
    created_at: NotRequired[str]
    resolved_at: NotRequired[Optional[str]]
    expires_at: NotRequired[str]

class IdentityChallengeListResponse(TypedDict):
    """Identity challenges, newest first"""

    data: list["IdentityChallengeResponse"]
    pagination: dict[str, Any]

class LedgerEntry(TypedDict):
    """One row of the prepaid balance history"""

    id: str
    kind: Literal["top_up", "auto_top_up", "usage", "refund", "adjustment"]
    amount: int
    currency: Literal["eur"]
    mills: int
    proofs: Optional[int]
    period: Optional[str]
    invoice_id: Optional[str]
    created_at: str
    updated_at: str

class LedgerListResponse(TypedDict):
    """One page of the prepaid balance history, newest first"""

    data: list["LedgerEntry"]
    pagination: dict[str, Any]

class LookalikeWatchSubscribe(TypedDict):
    """Subscribe to Lookalike Watch. `brand_tokens` are the names watched for confusable newly-published artifacts; `owned_namespaces` suppress alerts on artifacts you publish yourself; `notify_email` must be an address already proven on the account, because a subscription is a standing outbound channel rather than a one-shot send. Every bound is published on the fields themselves — restating a cap in prose is the second declaration this block exists to avoid."""

    brand_tokens: list[str]
    owned_namespaces: NotRequired[list[str]]
    notify_email: NotRequired[str]

class MasterKeyResponse(TypedDict):
    """HITL master-key KDF salt for the authenticated user"""

    master_kdf_salt: Optional[str]
    backup_kdf_salt: Optional[str]

class McpConnectInfo(TypedDict):
    message: str
    remote_url: NotRequired[str]
    remote_config: NotRequired[dict[str, Any]]
    install_command: str
    install_caveat: str
    client_config: dict[str, Any]
    docs_url: str

class MeAssetSearchQueryParams(TypedDict):
    """Universal asset search query parameters"""

    value: str
    type: NotRequired[Literal["phone", "email", "domain", "social", "wallet", "telegram_bot"]]
    environment: NotRequired[Literal["production", "test"]]

class MeAssetSearchResponse(TypedDict):
    """Exact-match asset dossier. `*_masked` fields are always masked; the owner's JWT session additionally receives unmasked `identifier`/`recipient` twins — never returned to API-key callers (owner-vs-not boundary, SEC-001). Authorizations/confirmations require hitl:read for API-key callers; related records follow the provable verification_id -> authorization_id chain only."""

    data: dict[str, Any]
    total: float

class MeSearchQueryParams(TypedDict):
    """Account search query parameters"""

    q: str
    type: NotRequired[Literal["verification_requests", "verifications", "hitl", "confirmations", "authorizations", "api_keys"]]
    environment: NotRequired[Literal["production", "test"]]
    limit: NotRequired[int]

class MeSearchResponse(TypedDict):
    """Account search results grouped by resource type. `masked_identifier` is always masked; the owner's JWT session additionally receives the unmasked `identifier` twin — never returned to API-key callers (owner-vs-not boundary, SEC-001). The hitl/confirmations buckets require the matching read scope."""

    data: dict[str, Any]
    total: float

MultiChannelPhoneChannel = Literal["whatsapp", "telegram", "sms"]

class CreateMultiChannelVerificationRequest(TypedDict):
    """Request body for creating a multi-channel verification group"""

    profile_id: NotRequired[str]
    type: Literal["phone"]
    identifier: str
    channels: list["MultiChannelPhoneChannel"]
    external_user_id: NotRequired[str]
    client_metadata: NotRequired[dict[str, Any]]
    proof_expiry_days: NotRequired[int]

class OAuthAuthorizationServerMetadata(TypedDict):
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    registration_endpoint: str
    revocation_endpoint: str
    response_types_supported: list[str]
    grant_types_supported: list[str]
    code_challenge_methods_supported: list[str]
    token_endpoint_auth_methods_supported: list[str]
    scopes_supported: list[str]
    service_documentation: str

class OAuthProtectedResourceMetadata(TypedDict):
    resource: str
    authorization_servers: list[str]
    scopes_supported: list[str]
    bearer_methods_supported: list[str]
    resource_name: str
    resource_documentation: str

class ApiKeyUsageResponse(TypedDict):
    """Per-API-key usage: verification counts by type/channel/status + per-collection totals (requests, confirmations, authorizations) + attribution metadata. The counts cover the key and every key it replaced (`api_key.replaced_key_ids`). Counts only — no recipient identifiers (SEC-001). Data is returned for revoked keys (audit)."""

    api_key: dict[str, Any]
    verifications: dict[str, Any]
    verification_requests: dict[str, Any]
    confirmations: dict[str, Any]
    authorizations: dict[str, Any]
    attribution_cutoff_at: Optional[str]
    attributed_fraction: Optional[float]

class AvailableAssetsQuery(TypedDict):
    profile_id: NotRequired[Any]

class CircleMember(TypedDict):
    """A Circle member (channel presence and a masked enrollment phone only, never an identifier)"""

    id: "ObjectId"
    name: str
    status: Literal["pending", "active"]
    has_telegram: bool
    has_whatsapp: bool
    mesh_opted_in: bool
    mesh_opt_out: bool
    enrolled_phone_hint: Optional[str]
    enrolled_at: Optional[str]
    last_verified_at: Optional[str]

class Circle(TypedDict):
    """A Circle — a named group of trusted contacts"""

    id: "ObjectId"
    user_id: Optional["ObjectId"]
    name: Optional[str]
    owner_name: Optional[str]
    profile_id: Optional["ObjectId"]
    environment: Literal["production", "test"]
    proof_me_enabled: bool
    status: "CircleStatus"
    member_count: int
    members: list["CircleMember"]
    created_at: str
    updated_at: str

class CircleListResponse(TypedDict):
    """Paginated list of Circles"""

    data: list["Circle"]
    pagination: dict[str, Any]

class CircleMemberChannel(TypedDict):
    """A member channel (metadata only — never the identifier, SEC-PM-006)"""

    id: "ObjectId"
    channel: Literal["telegram", "whatsapp"]
    status: Literal["declared", "verified"]
    verified_at: Optional[str]
    created_at: str

class CircleMemberChannelListResponse(TypedDict):
    """The channels of a Circle member"""

    channels: list["CircleMemberChannel"]

class CircleMemberDrillResponse(TypedDict):
    """Result of manually triggering a member drill (Proof of Me)"""

    id: Any
    status: Literal["pending"]
    confirm_channel: NotRequired[str]
    single_channel_warning: NotRequired[bool]

class CircleMemberInviteBody(TypedDict):
    """Request body for inviting (enrolling) a Circle member"""

    member_id: Any

class CircleMemberInviteResponse(TypedDict):
    """A single-use member enrollment link (both channels + QR)"""

    token: str
    member_id: "ObjectId"
    telegram_deep_link: str
    whatsapp_deep_link: str
    qr_code: str
    qr_text: str
    expires_in: int
    suggested_share_text: str

class CircleMemberListResponse(TypedDict):
    """The members of a Circle"""

    members: list["CircleMember"]

class Confirmation(TypedDict):
    """A HITL confirmation request"""

    id: "ObjectId"
    hitl_id: Any
    message: str
    status: "ConfirmationStatus"
    response: NotRequired[Optional[dict[str, Any]]]
    timeout_at: NotRequired[Optional[str]]
    proof_token: NotRequired[Optional[str]]
    resolved_at: NotRequired[Optional[str]]
    created_at: str
    updated_at: str

class ConfirmationListQuery(TypedDict):
    """Query parameters for listing confirmations"""

    page: NotRequired[int]
    limit: NotRequired[int]
    status: NotRequired["ConfirmationStatusFilter"]
    hitl_id: NotRequired["ObjectId"]
    start_date: NotRequired[Optional[str]]
    end_date: NotRequired[Optional[str]]

class ConfirmationListResponse(TypedDict):
    """Paginated list of confirmations"""

    data: list["Confirmation"]
    pagination: dict[str, Any]

class ConfirmationWebhookPayload(TypedDict):
    """Body of `confirmation.approved` / `confirmation.denied`. A timeout is `confirmation.denied` with `response.channel` `system` and `response.text` `timeout`."""

    event: Literal["confirmation.approved", "confirmation.denied"]
    confirmation_id: "ObjectId"
    hitl_id: Any
    status: Literal["approved", "denied"]
    message: str
    response: NotRequired[Optional[dict[str, Any]]]
    proof_token: NotRequired[str]
    encrypted: bool
    resolved_at: NotRequired[str]

class CreateCircleBody(TypedDict):
    """Request body for creating a Circle"""

    name: str
    owner_name: NotRequired[Optional[str]]
    profile_id: NotRequired[Any]
    proof_me_enabled: NotRequired[bool]
    members: NotRequired[list["CircleMemberInput"]]

class CreateConfirmationBody(TypedDict):
    """Request body for creating a confirmation"""

    hitl_id: Any
    message: str
    proof_expiry_days: NotRequired[int]

class CreateHitlBody(TypedDict):
    """Request body for creating a HITL configuration"""

    name: str
    channels: NotRequired[list["HitlChannel"]]
    circle_id: NotRequired[Any]
    timeout_seconds: NotRequired[float]
    profile_id: NotRequired[Any]

class Delegation(TypedDict):
    """A delegation — link 2 of the proof chain: domain → artifact. NO endpoint returns this shape: every delegation response carries the derived `effective_status`/`is_valid` too, so read `DelegationListItem` (list, revoke) or `DelegationDetail` (create, get). Published as a back-compat type only."""

    id: "ObjectId"
    delegation_id: Optional[str]
    principal: str
    delegate: "DelegateIdentifier"
    scope: list[str]
    control_proof: str
    status: Literal["active", "revoked"]
    revoked_at: Optional[str]
    revoked_reason: Optional[str]
    environment: Literal["production", "test"]
    issued_at: str
    expires_at: str
    created_at: str

class DelegationDetail(TypedDict):
    """A delegation with its derived effective status"""

    id: "ObjectId"
    delegation_id: Optional[str]
    principal: str
    delegate: "DelegateIdentifier"
    scope: list[str]
    control_proof: str
    status: Literal["active", "revoked"]
    revoked_at: Optional[str]
    revoked_reason: Optional[str]
    environment: Literal["production", "test"]
    issued_at: str
    expires_at: str
    created_at: str
    token: Optional[str]
    effective_status: Literal["active", "revoked", "expired", "suspended"]
    is_valid: bool

class DelegationListItem(TypedDict):
    """A delegation without its token, carrying stored status plus derived liveness — what the owner listing reports, and what `POST /delegations/{id}/revoke` answers with"""

    id: "ObjectId"
    delegation_id: Optional[str]
    principal: str
    delegate: "DelegateIdentifier"
    scope: list[str]
    control_proof: str
    status: Literal["active", "revoked"]
    revoked_at: Optional[str]
    revoked_reason: Optional[str]
    environment: Literal["production", "test"]
    issued_at: str
    expires_at: str
    created_at: str
    effective_status: Literal["active", "revoked", "expired", "suspended"]
    is_valid: bool

class DelegationListResponse(TypedDict):
    """The caller's own delegations (no public enumeration exists)"""

    data: list["DelegationListItem"]
    pagination: dict[str, Any]

class DelegationWithToken(TypedDict):
    """A delegation including its publishable signed token. NO endpoint returns this shape — `POST /delegations` and `GET /delegations/{id}` answer with `DelegationDetail`, which adds the derived `effective_status`/`is_valid`. Published as a back-compat type only."""

    id: "ObjectId"
    delegation_id: Optional[str]
    principal: str
    delegate: "DelegateIdentifier"
    scope: list[str]
    control_proof: str
    status: Literal["active", "revoked"]
    revoked_at: Optional[str]
    revoked_reason: Optional[str]
    environment: Literal["production", "test"]
    issued_at: str
    expires_at: str
    created_at: str
    token: Optional[str]

class Hitl(TypedDict):
    """HITL configuration with messaging channels and timeout"""

    id: "ObjectId"
    user_id: Optional["ObjectId"]
    name: NotRequired[Optional[str]]
    profile_id: NotRequired[Optional["ObjectId"]]
    circle_id: NotRequired[Optional["ObjectId"]]
    channels: list["HitlChannel"]
    timeout_seconds: int
    status: "HitlStatus"
    keypair: Optional[dict[str, Any]]
    environment: Literal["production", "test"]
    created_at: str
    updated_at: str

class HitlAuthorizationResponse(TypedDict):
    """Response from requesting authorization consent for HITL channels"""

    hitl_id: "ObjectId"
    authorizations: list[dict[str, Any]]
    message: str

class HitlFinalizeResponse(TypedDict):
    """Finalized HITL configuration (pending → active) with optional authorization dispatch results"""

    id: "ObjectId"
    user_id: Optional["ObjectId"]
    name: NotRequired[Optional[str]]
    profile_id: NotRequired[Optional["ObjectId"]]
    circle_id: NotRequired[Optional["ObjectId"]]
    channels: list["HitlChannel"]
    timeout_seconds: int
    status: "HitlStatus"
    keypair: Optional[dict[str, Any]]
    environment: Literal["production", "test"]
    created_at: str
    updated_at: str
    authorizations: NotRequired[list[dict[str, Any]]]

class HitlListResponse(TypedDict):
    """Paginated list of HITL configurations"""

    data: list["Hitl"]
    pagination: dict[str, Any]
    limits: dict[str, Any]

class ProfileBadgeResponse(TypedDict):
    """Everything needed to embed the verification badge for a username (proof.holdings/badge/{username})"""

    username: str
    subject: str
    verified_count: int
    state: Literal["published", "no_public_record"]
    checked_at: str
    profile_url: str
    badge_urls: dict[str, Any]
    snippets: dict[str, Any]

class ProfileTemplateContent(TypedDict):
    """Body for a profile-scoped template write. Distinct from the account-level `TemplateContent`: it also accepts `is_active`, which every read of the template returns — declaring `TemplateContent` here published a field callers could read and had no documented way to set."""

    subject: NotRequired[str]
    body: str
    button_text: NotRequired[str]
    button_url_template: NotRequired[str]
    is_active: NotRequired[bool]

class PutHitlKeysBody(TypedDict):
    """The client-generated RSA keypair for a HITL config. `public_key`, `encrypted_private_key` and `kdf_salt` are required; the `wrapped_dek`/`dek_iv`/`dek_tag` trio carries the v2 master-key envelope and the `backup_*` trio the recovery wrapper. The server never receives the master password, so it cannot decrypt any of it."""

    public_key: str
    encrypted_private_key: str
    kdf_salt: str
    wrapped_dek: NotRequired[str]
    dek_iv: NotRequired[str]
    dek_tag: NotRequired[str]
    backup_wrapped_dek: NotRequired[str]
    backup_dek_iv: NotRequired[str]
    backup_dek_tag: NotRequired[str]

class ReadinessResponse(TypedDict):
    """Readiness probe response — `ready` is true only when both MongoDB and Redis answer"""

    ready: bool
    checks: dict[str, Any]
    timestamp: str

class RequestHealthHistoryQueryParams(TypedDict):
    """Completion-rate history query parameters"""

    days: NotRequired[int]
    interval: NotRequired[Literal["day", "week"]]
    environment: NotRequired[Literal["production", "test"]]

class RequestHealthHistoryResponse(TypedDict):
    """Per-bucket completion-rate trend: requests bucketed by created_at (UTC day/week), reusing /me/summary's stale-expiry bucketing and completed/(completed+expired+cancelled) rate. Dense (zero-filled), chronological. Counts + rate only — no recipient identifiers (SEC-001). Demo traffic excluded (SEC-003)."""

    interval: Literal["day", "week"]
    days: float
    as_of: str
    points: list[dict[str, Any]]

class ResolveLinkMetadata(TypedDict):
    """Approval link metadata returned by GET /resolve. For resolved confirmations, includes history fields."""

    confirmation_id: str
    hitl_id: str
    status: Literal["pending", "approved", "denied", "expired"]
    encrypted: bool
    timeout_at: str
    created_at: str
    config_name: Optional[str]
    config_archived: NotRequired[bool]
    business_name: NotRequired[Optional[str]]
    logo_url: NotRequired[Optional[str]]
    response: NotRequired[dict[str, Any]]
    resolved_at: NotRequired[Optional[str]]
    masked_actor: NotRequired[Optional[str]]

class SetMasterKeyBody(TypedDict):
    """HITL master-key KDF salt to set or change"""

    master_kdf_salt: str
    backup_kdf_salt: NotRequired[str]

StatusListToken = str

class SummaryQueryParams(TypedDict):
    """Account summary query parameters"""

    environment: NotRequired[Literal["production", "test"]]
    profile_id: NotRequired[str]

class SuspendProofResponse(TypedDict):
    """Result of a suspend/unsuspend transition (m-proof-status-list)"""

    proof_id: str
    status: Literal["suspended", "active"]
    suspended_at: Optional[str]
    status_list_uri: str

class ProfileTemplate(TypedDict):
    """A message template as resolved for one public profile — either the profile override or the inherited default."""

    # Deprecated: Removed from the API (templates belong to a project: use the templates resource with the project's id); kept so code written for an earlier 1.x release keeps compiling, and dropped in the next major version.

    channel: "TemplateChannel"
    message_type: str
    subject: NotRequired[str]
    body: str
    button_text: NotRequired[str]
    button_url_template: NotRequired[str]
    is_custom: bool
    is_active: bool

class TopUpRequest(TypedDict):
    """Request body for buying a prepaid balance top-up"""

    amount: Union[Literal["10"], Literal["50"], Literal["200"]]
    auto_top_up: NotRequired[bool]
    success_url: str
    cancel_url: str

class TopUpResponse(TypedDict):
    """Top-up checkout session creation response"""

    checkout_url: str

class UpdateAuthorizationBody(TypedDict):
    """Request body for updating an authorization's owner-editable metadata (F22)"""

    label: Optional[str]

class UpdateCircleBody(TypedDict):
    """Request body for updating a Circle (name and owner name — the profile binding is create-only)"""

    name: NotRequired[str]
    owner_name: NotRequired[Optional[str]]

class UpdateHitlBody(TypedDict):
    """Request body for updating a HITL configuration"""

    name: NotRequired[Optional[str]]
    channels: NotRequired[list["HitlChannel"]]
    timeout_seconds: NotRequired[float]

class UserAPIKeyListItem(TypedDict):
    """A live API key as the owner's key list shows it. Never carries the key value."""

    id: "ObjectId"
    name: str
    prefix: str
    environment: Literal["production", "test"]
    scopes: list[str]
    profile_id: Optional["ObjectId"]
    last_used_at: NotRequired[Optional[str]]
    expires_at: Optional[str]
    created_at: str
    replaced_key_ids: list["ObjectId"]

class MultiChannelChannelBlock(TypedDict):
    """Per-channel setup block of a multi-channel verification group"""

    channel: "MultiChannelPhoneChannel"
    verification_id: "ObjectId"
    status: "VerificationStatus"
    deep_link: NotRequired[str]
    qr_code: NotRequired[str]
    qr_text: NotRequired[str]
    message: NotRequired[str]
    instructions: NotRequired[str]
    phone_number: NotRequired[str]
    sms_message: NotRequired[str]
    sms_dids: NotRequired[dict[str, Any]]
    suggested_region: NotRequired[Literal["americas", "europe", "israel"]]

class MultiChannelGroupStatusResponse(TypedDict):
    """Polling status of a multi-channel verification group"""

    group_id: str
    status: Literal["pending", "verified", "expired"]
    winning_channel: Optional["MultiChannelPhoneChannel"]
    channels: list[dict[str, Any]]
    proof: NotRequired[Any]

class MultiChannelVerificationResponse(TypedDict):
    """Multi-channel verification group with one setup block per channel"""

    group_id: str
    type: Literal["phone"]
    identifier: str
    status: "VerificationStatus"
    expires_at: str
    external_user_id: NotRequired[str]
    client_metadata: NotRequired[dict[str, Any]]
    channels: list["MultiChannelChannelBlock"]
    created_at: str

class ProfileAssetOption(TypedDict):
    """An active asset offered for display on a public profile"""

    id: "ObjectId"
    type: "VerificationType"
    identifier: str
    channel: "AssetChannel"
    verified_at: NotRequired[str]
    is_public: bool

class SettingsResponse(TypedDict):
    """Account settings"""

    webhook: "WebhookSettingsResponse"
    proof_expiry_days: Optional[int]
    # Deprecated: Removed from the API (account-level branding is retired: each project (sub-account) carries its own branding, set with the profiles resource); kept so code written for an earlier 1.x release keeps compiling, and dropped in the next major version.
    branding: "BrandingSettings"

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
    id: "ObjectId"
    status: Literal["cancelled"]
    message: str

class ReferenceIdParam(TypedDict):
    referenceId: str

class RequestedAsset(TypedDict):
    """Asset to be verified in a multi-asset request"""

    type: "VerificationType"
    identifier: NotRequired[Optional[str]]
    channel: NotRequired[Optional["VerificationChannel"]]
    allowed_channels: NotRequired[list["VerificationChannel"]]
    required: NotRequired[bool]

# ============================================================================
# Domains
# ============================================================================

class AddDomainRequest(TypedDict):
    """Request body for adding a domain"""

    domain: str
    profile_id: NotRequired[str]
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

class DomainRemovedResponse(TypedDict):
    success: Literal["true"]
    domain: str
    proofs_revoked: int
    delegations_revoked: list[dict[str, Any]]
    external: dict[str, Any]
    carriers: list[dict[str, Any]]
    notice: list[dict[str, Any]]

DomainStatus = Literal["pending", "verified", "failed"]

class Domain(TypedDict):
    """Domain record"""

    id: "ObjectId"
    domain: str
    status: "DomainStatus"
    verification_method: NotRequired[str]
    provider: NotRequired[str]
    email_sending_enabled: NotRequired[bool]
    profile_id: NotRequired["ObjectId"]
    created_at: str
    updated_at: str
    verified_at: NotRequired[str]
    proof_id: NotRequired[Optional[str]]
    proof_status: NotRequired[Optional[Literal["active", "revoked", "expired", "suspended"]]]
    proof_revoked_reason: NotRequired[Optional[str]]
    proof_expires_at: NotRequired[Optional[str]]

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
    channel: "AssetChannel"
    identifier: str
    status: "AssetStatus"
    proof_id: NotRequired[Optional[str]]
    proof_status: NotRequired[Optional[Literal["active", "revoked", "expired", "suspended"]]]
    proof_token: NotRequired[Optional[str]]
    has_proof: NotRequired[bool]
    verified_at: NotRequired[str]
    proof_expires_at: str
    metadata: NotRequired[dict[str, Any]]
    created_at: str

# ============================================================================
# Auth
# ============================================================================

AuthChannel = Literal["telegram", "whatsapp", "sms", "email"]

class AuthSessionIdParam(TypedDict):
    sessionId: str

class AuthSessionListItem(TypedDict):
    """Session entry"""

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
    qr_text: NotRequired[str]
    expires_at: str
    instructions: NotRequired[str]
    verified_at: NotRequired[str]
    user_id: NotRequired[str]

class CreateAuthSessionRequest(TypedDict):
    """Request body for creating a new auth session (login)"""

    channel: "AuthChannel"
    phone_number: NotRequired[str]
    email: NotRequired[str]
    return_to: NotRequired[str]

class ExchangeTokenRequest(TypedDict):
    """Request body for exchanging a one-time token for JWT"""

    token: str

class ExchangeTokenResponse(TypedDict):
    """Token exchange response"""

    success: bool
    jwt: str
    expiresAt: str

class ListSessionsResponse(TypedDict):
    """List of sessions"""

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

AuthorizationScope = Literal["confirmations", "identity_challenge"]

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
    hitl_id: NotRequired[Any]
    circle_id: NotRequired[Any]
    recipient: NotRequired[Optional[str]]
    phone: NotRequired[Optional[str]]
    bsuid: NotRequired[Optional[str]]
    channel: "AuthorizationChannel"
    scope: "AuthorizationScope"
    business_name: str
    label: NotRequired[Optional[str]]
    recipient_display_name: Optional[str]
    enrolled: bool
    verification_id: NotRequired["ObjectId"]
    proof_token: NotRequired[str]
    authorized_at: NotRequired[str]
    denied_at: NotRequired[str]
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

class AuthorizationWebhookPayload(TypedDict):
    """Body of `authorization.approved` / `authorization.denied` — the recipient's answer to a consent request. The recipient's phone/identifier is not included; join on `authorization_id`."""

    event: Literal["authorization.approved", "authorization.denied"]
    authorization_id: "ObjectId"
    hitl_id: NotRequired[Any]
    status: Literal["active", "denied"]
    channel: "AuthorizationChannel"
    scope: NotRequired["AuthorizationScope"]
    proof_token: NotRequired[str]
    decided_at: NotRequired[str]
    expires_at: NotRequired[str]

class CreateAuthorizationBody(TypedDict):
    """Request body for creating an authorization"""

    hitl_id: Any
    recipient: str
    phone: str
    bsuid: NotRequired[str]
    channel: "AuthorizationChannel"
    scope: NotRequired[Literal["confirmations"]]
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
    bsuid: NotRequired[Optional[str]]
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

BillingPlan = Literal[
    "free", "starter", "pro", "business", "enterprise",
]

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

    # Deprecated: Removed from the API (account-level branding is retired: each project (sub-account) carries its own branding, set with the profiles resource); kept so code written for an earlier 1.x release keeps compiling, and dropped in the next major version.

    business_name: NotRequired[str]
    logo_url: NotRequired[Optional[str]]
    primary_color: NotRequired[str]
    support_email: NotRequired[str]
    email_theme: NotRequired[Literal["dark", "light"]]

class UsageQueryParams(TypedDict):
    """Usage query parameters"""

    period: NotRequired[str]
    months: NotRequired[int]

class UpdateSettingsRequest(TypedDict):
    """Request body for updating user settings"""

    branding: NotRequired["BrandingSettings"]
    webhook: NotRequired["WebhookSettings"]
    proof_expiry_days: NotRequired[int]

class UpdateSettingsResponse(TypedDict):
    """Account settings as stored after the update. Carries `webhook.secret` when THIS request created or rotated it — the only response that ever does."""

    success: bool
    webhook: "WebhookSettingsResponse"
    proof_expiry_days: Optional[int]
    # Deprecated: Removed from the API (account-level branding is retired: each project (sub-account) carries its own branding, set with the profiles resource); kept so code written for an earlier 1.x release keeps compiling, and dropped in the next major version.
    branding: "BrandingSettings"

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
    "whatsapp", "telegram", "sms", "email", "dns", "http", "auto", "github", "google", "facebook", "x", "linkedin", "instagram", "youtube", "tiktok", "ethereum", "solana", "bitcoin", "coinbase", "kraken", "telegram_bot_token",
]

VerificationConfidence = Literal["high", "standard", "degraded"]

VerificationRequestListStatus = Literal[
    "pending", "partial", "completed", "expired", "cancelled", "active",
]

class VerificationRequestListQuery(TypedDict):
    page: NotRequired[int]
    limit: NotRequired[int]
    status: NotRequired["VerificationRequestListStatus"]
    reference_id: NotRequired[str]

VerificationRequestStatus = Literal[
    "pending", "partial", "completed", "expired", "cancelled",
]

class VerificationRequestListItem(TypedDict):
    """Verification request as listed: a summary — read the request itself for its assets"""

    id: "ObjectId"
    reference_id: NotRequired[str]
    status: "VerificationRequestStatus"
    computed_state: dict[str, Any]
    action_type: "ActionType"
    asset_count: int
    progress: dict[str, Any]
    expires_at: str
    completed_at: NotRequired[str]
    created_at: str

class VerificationRequestListResponse(TypedDict):
    data: list["VerificationRequestListItem"]
    pagination: "PaginationResponse"

VerificationStatus = Literal[
    "pending", "verified", "failed", "expired", "revoked", "cancelled",
]

VerificationType = Literal[
    "phone", "email", "domain", "social", "wallet", "account", "telegram_bot",
]

class CreateVerificationRequest(TypedDict):
    """Request body for creating a new verification"""

    profile_id: NotRequired[str]
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
    identifier: NotRequired[str]
    status: "VerificationStatus"
    challenge: NotRequired["Challenge"]
    proof: NotRequired["Proof"]
    external_user_id: NotRequired[str]
    attempts: NotRequired[int]
    max_attempts: NotRequired[int]
    created_at: str
    updated_at: NotRequired[str]
    verified_at: NotRequired[str]

class VerificationListItem(TypedDict):
    """Verification as listed"""

    id: "ObjectId"
    type: "VerificationType"
    channel: "VerificationChannel"
    status: "VerificationStatus"
    identifier: NotRequired[str]
    environment: Literal["production", "test"]
    created_at: str
    verified_at: NotRequired[str]

class VerificationListQuery(TypedDict):
    page: NotRequired[int]
    limit: NotRequired[int]
    status: NotRequired["VerificationStatus"]
    type: NotRequired["VerificationType"]

class VerificationListResponse(TypedDict):
    """Paginated list of verifications"""

    data: list["VerificationListItem"]
    pagination: "PaginationResponse"

class VerificationRequest(TypedDict):
    """Multi-asset verification request"""

    id: "ObjectId"
    reference_id: NotRequired[str]
    status: "VerificationRequestStatus"
    computed_state: NotRequired[dict[str, Any]]
    assets: list[dict[str, Any]]
    action_type: "ActionType"
    action_context: NotRequired[Optional["ActionContext"]]
    partial_ok: bool
    validity_requirement: NotRequired[Optional[str]]
    verification_url: NotRequired[str]
    redirect_url: NotRequired[Optional[str]]
    callback_url: NotRequired[Optional[str]]
    progress: NotRequired[dict[str, Any]]
    expires_at: str
    completed_at: NotRequired[str]
    created_at: str
    updated_at: NotRequired[str]

class VerificationRequestProofsResponse(TypedDict):
    """Proof tokens for verified assets in a verification request"""

    proofs: list[dict[str, Any]]

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
    email_theme: NotRequired[Literal["dark", "light"]]
    support_email: NotRequired[str]

class PublicProfileDelegation(TypedDict):
    """A published, in-force delegation for a domain the profile shows"""

    delegate: str
    delegate_type: Literal["url", "purl"]
    principal: str
    scope: list[str]
    issued_at: str
    expires_at: str
    artifact_path: Optional[str]

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
    show_delegations: NotRequired[bool]
    theme: NotRequired["ProfileTheme"]
    custom_links: NotRequired[list["CustomLink"]]
    email_theme: NotRequired[Literal["dark", "light"]]
    support_email: NotRequired[Optional[str]]

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
    show_delegations: NotRequired[bool]
    email_theme: NotRequired[Optional[Literal["dark", "light"]]]
    support_email: NotRequired[Optional[str]]
    delegations: NotRequired[Optional[list["PublicProfileDelegation"]]]
    created_at: str
    updated_at: str

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
    """Request body for creating a phone-first verification session"""

    profile_id: NotRequired[str]
    channel: NotRequired[Literal["whatsapp", "telegram", "sms"]]
    client_metadata: NotRequired[dict[str, Any]]
    context: NotRequired[dict[str, Any]]
    # Deprecated: Removed from the API (a session takes no phone number (the person shares it in the chat), and the server ignores it); kept so code written for an earlier 1.x release keeps compiling, and dropped in the next major version.
    phone: str

SessionChannel = Literal["telegram", "whatsapp", "sms"]

class SessionIdParam(TypedDict):
    id: str

class SessionSmsNumber(TypedDict):
    """One of our SMS numbers, for one region"""

    did: str
    label: str
    flag: str
    qr_code: NotRequired[str]
    qr_text: NotRequired[str]

class SessionSmsNumbers(TypedDict):
    """Every number an `sms` session's code can be texted to, one per configured region (a region with no number is absent), each with its own QR code. `deep_link` uses the default region's number; the request comes from your server, so nothing in it says where the person is."""

    americas: "SessionSmsNumber"
    europe: NotRequired["SessionSmsNumber"]
    israel: NotRequired["SessionSmsNumber"]

class CreateSessionResponse(TypedDict):
    """A new phone-first session: what to show the person"""

    id: str
    channel: "SessionChannel"
    status: Literal["pending"]
    deep_link: str
    qr_code: str
    qr_text: str
    expires_at: str
    instructions: str
    sms_code: NotRequired[str]
    sms_message: NotRequired[str]
    sms_dids: NotRequired["SessionSmsNumbers"]

class Session(TypedDict):
    """Phone-first session status"""

    id: "ObjectId"
    channel: "SessionChannel"
    status: Literal["pending", "verified", "expired"]
    created_at: str
    phone_number: NotRequired[str]
    verified_at: NotRequired[str]
    verification_id: NotRequired[str]
    proof: NotRequired["Proof"]
    # Deprecated: Removed from the API (GET /api/v1/sessions/{id} never returned it, and nothing replaces it); kept so code written for an earlier 1.x release keeps compiling, and dropped in the next major version.
    challenge: NotRequired["Challenge"]
    # Deprecated: Removed from the API (GET /api/v1/sessions/{id} never returned it; the session's expiry is on the create response); kept so code written for an earlier 1.x release keeps compiling, and dropped in the next major version.
    expires_at: str

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
    """JSON Web Key. The key-type-specific members are optional because one key set may carry both an EC and an RSA key: `crv`/`x`/`y` are present on EC keys, `n`/`e` on RSA keys."""

    kty: Literal["EC", "RSA"]
    crv: NotRequired[Literal["P-256"]]
    x: NotRequired[str]
    y: NotRequired[str]
    n: NotRequired[str]
    e: NotRequired[str]
    use: Literal["sig"]
    alg: Literal["ES256", "RS256"]
    kid: str

class JWKS(TypedDict):
    """JSON Web Key Set for offline proof verification"""

    keys: list["JWK"]

class ProofMePageResponse(TypedDict):
    """Public Proof of Me page payload for a username (proof.holdings/me/{username})"""

    username: str
    display_name: NotRequired[str]
    avatar_url: NotRequired[str]
    proof_me_enabled: bool
    telegram_bot_username: str
    whatsapp_number: str
    telegram_deep_link: str
    whatsapp_deep_link: str
    qr_code: str

ProofStatusValue = Literal[
    "pending", "active", "failed", "expired", "revoked", "cancelled", "suspended",
]

class ProofStatusResponse(TypedDict):
    """Proof status check result"""

    proof_id: str
    status: "ProofStatusValue"
    is_valid: bool
    is_revoked: bool
    revoked_at: Optional[str]
    revoked_reason: Optional[str]
    suspended_at: Optional[str]
    expires_at: Optional[str]
    is_expired: bool

ProofTokenChannel = Literal[
    "whatsapp", "telegram", "sms", "email", "dns", "http", "auto", "github", "google", "facebook", "x", "linkedin", "instagram", "youtube", "tiktok", "ethereum", "solana", "bitcoin", "coinbase", "kraken", "telegram_bot_token", "browser",
]

ProofTokenType = Literal[
    "phone", "email", "domain", "social", "wallet", "account", "telegram_bot", "confirmation", "authorization",
]

class RevokeProofRequest(TypedDict):
    """Request body for revoking a proof"""

    reason: NotRequired[Any]

class RevokeProofResponse(TypedDict):
    success: bool
    proof_id: NotRequired[str]
    proof_type: NotRequired[str]
    verification_id: NotRequired[str]
    revoked_at: str
    reason: str
    principal: NotRequired[Optional[str]]
    owned_domain: NotRequired[bool]
    domain_status: NotRequired[Optional[str]]
    delegations_revoked: NotRequired[list[dict[str, Any]]]

RevokedProofType = Literal[
    "verification", "verification_request", "confirmation", "authorization", "user_asset",
]

class RevokedProof(TypedDict):
    """Entry in the revocation list"""

    proof_id: Optional[str]
    public_proof_id: Optional[str]
    proof_type: "RevokedProofType"
    revoked_at: Optional[str]
    reason: Optional["RevocationReason"]

class RevocationList(TypedDict):
    """Signed list of revoked proofs"""

    revoked: list["RevokedProof"]
    issued_at: str
    count: float
    has_more: bool
    status_list_uri: str
    signature: Optional[str]
    kid: Optional[str]

class ValidateProofRequest(TypedDict):
    """Request body for validating a proof token"""

    proof_token: str
    identifier: NotRequired[str]

class ValidateProofResponse(TypedDict):
    """Proof validation result. Returns verification details when valid, or reason/message when invalid. A DELEGATION token answers with `token_type: "delegation"` and the `delegation` block instead of `verification`; its status resolves the cascade down to the domain control proof, which neither the status list (it packs each row's own bit) nor an offline signature check can show. Delegation-specific reasons: `unknown_delegation` (no registry record — delegations are minted fail-closed, so this is invalid, not merely unresolvable), `status_unavailable`, and `identifier_unverifiable` when an `identifier` binding is requested for a delegation."""

    valid: bool
    proof_id: NotRequired[str]
    verification: NotRequired[dict[str, Any]]
    reason: NotRequired[str]
    suspended_at: NotRequired[str]
    message: NotRequired[str]
    revoked_at: NotRequired[str]
    revoked_reason: NotRequired[str]
    token_type: NotRequired[Literal["delegation"]]
    delegation: NotRequired[dict[str, Any]]

class Proof(TypedDict):
    """Proof token after successful verification"""

    token: str
    expires_at: str
    confidence: NotRequired[Any]

# ============================================================================
# Templates
# ============================================================================

MessageType = Literal[
    "verification_request", "verification_success", "verification_expired", "login_request", "login_success", "2fa_request", "2fa_success", "account_deletion_request", "account_deletion_success", "confirmation_request", "confirmation_approved", "confirmation_denied",
]

TemplateChannel = Literal["telegram", "whatsapp", "sms", "email"]

class Template(TypedDict):
    """Message template"""

    id: NotRequired["ObjectId"]
    profile_id: NotRequired[Optional["ObjectId"]]
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

class TemplateScopeQuery(TypedDict):
    profile_id: NotRequired[Any]

class TemplateVariable(TypedDict):
    """Available template variable"""

    name: str
    description: str

# ============================================================================
# API Keys
# ============================================================================

class APIKeyCreatedResponse(TypedDict):
    """A newly created or regenerated API key, with its full value — the one response that carries it."""

    id: "ObjectId"
    key: str
    name: str
    prefix: str
    environment: Literal["production", "test"]
    scopes: list[str]
    profile_id: Optional["ObjectId"]
    created_at: str
    warning: str

class APIKeyResponse(TypedDict):
    """An API key's redacted metadata, as the calling key reads itself (`GET /me/api-key`). Never carries the key value."""

    id: "ObjectId"
    name: str
    key_prefix: str
    environment: Literal["production", "test"]
    scopes: list[str]
    profile_id: NotRequired[Optional["ObjectId"]]
    created_at: str
    last_used_at: NotRequired[Optional[str]]
    expires_at: NotRequired[Optional[str]]
    revoked_at: NotRequired[Optional[str]]
    replaced_key_ids: NotRequired[list["ObjectId"]]

class CreateAPIKeyRequest(TypedDict):
    """Request body for creating an API key"""

    name: NotRequired[str]
    environment: NotRequired[Literal["production", "test"]]
    scopes: NotRequired[list[str]]
    profile_id: NotRequired[Any]

# ============================================================================
# Projects
# ============================================================================

class ProjectDeletedResponse(TypedDict):
    success: Literal["true"]
    message: str
    project: dict[str, Any]
    was_primary: bool
    api_keys_revoked: int
    hitl_archived: int
    hitl_detached: int
    confirmations_denied: int
    authorizations_revoked: int
    requests_cancelled: int
    requests_detached: int
    verifications_detached: int
    domains_detached: int
    circles_detached: int
    templates_deleted: int
    username_retired: bool
    new_primary: Optional[dict[str, Any]]

class ProjectDeletionPreview(TypedDict):
    allowed: bool
    blocked: Optional[dict[str, Any]]
    project: dict[str, Any]
    counts: dict[str, Any]
    new_primary: Optional[dict[str, Any]]

# ============================================================================
# Webhook Deliveries
# ============================================================================

class RetryDeliveryResponse(TypedDict):
    success: bool
    message: str
    delivery_id: "ObjectId"
    next_retry_at: str

class WebhookDeliveryStats(TypedDict):
    """Webhook delivery statistics"""

    total: int
    by_status: dict[str, Any]
    delivery_rate: str
    recent_failures_24h: int

WebhookDeliveryStatus = Literal["pending", "delivered", "failed"]

WebhookEventType = Literal[
    "verification_request.completed", "verification_request.partial", "verification_request.expired", "verification.completed", "confirmation.approved", "confirmation.denied", "authorization.approved", "authorization.denied", "proof.revoked", "proof.suspended", "proof.unsuspended", "account.deletion_scheduled", "account.deletion_cancelled",
]

class WebhookDelivery(TypedDict):
    """Webhook delivery record"""

    id: "ObjectId"
    verification_request_id: Optional["ObjectId"]
    event_type: "WebhookEventType"
    url: str
    status: "WebhookDeliveryStatus"
    attempts: int
    max_attempts: int
    last_attempt_at: Optional[str]
    next_retry_at: Optional[str]
    delivered_at: Optional[str]
    response_status: Optional[int]
    error_message: Optional[str]
    created_at: str
    payload: dict[str, Any]
    response_body: Optional[str]
    updated_at: str

class WebhookDeliveryListItem(TypedDict):
    """Webhook delivery as listed: the payload and the receiver's response body are only on the detail"""

    id: "ObjectId"
    verification_request_id: Optional["ObjectId"]
    event_type: "WebhookEventType"
    url: str
    status: "WebhookDeliveryStatus"
    attempts: int
    max_attempts: int
    last_attempt_at: Optional[str]
    next_retry_at: Optional[str]
    delivered_at: Optional[str]
    response_status: Optional[int]
    error_message: Optional[str]
    created_at: str

class WebhookDeliveryListQuery(TypedDict):
    page: NotRequired[int]
    limit: NotRequired[int]
    status: NotRequired["WebhookDeliveryStatus"]
    event_type: NotRequired["WebhookEventType"]
    verification_request_id: NotRequired[Any]

class WebhookDeliveryListResponse(TypedDict):
    data: list["WebhookDeliveryListItem"]
    pagination: "PaginationResponse"

class WebhookProof(TypedDict):
    """Proof of a verified asset included in webhook payload"""

    type: "VerificationType"
    identifier: Optional[str]
    verified_at: NotRequired[str]
    channel: Optional["VerificationChannel"]
    proof_token: NotRequired[str]
    confidence: NotRequired[Any]

class WebhookPayload(TypedDict):
    """Outbound webhook payload for verification request events (`verification_request.*`), and for `confirmation.approved` when it comes from a verification request created with `action_type: "confirmation"`"""

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

class WebhookSettings(TypedDict):
    """Outbound webhook configuration. The signing secret is created with the first endpoint; deliveries carry it as an HMAC-SHA256 `X-Proof-Signature` over `<X-Proof-Timestamp>.<body>`."""

    url: NotRequired[Optional[str]]
    events: NotRequired[list[str]]
    rotate_secret: NotRequired[bool]

class WebhookSettingsResponse(TypedDict):
    """Outbound webhook configuration as stored."""

    url: Optional[str]
    events: list[str]
    secret_set: bool
    secret: NotRequired[str]

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

class TryItResponse(TypedDict):
    """The 201 of the public demo create. `success` is always true (a failure answers with an error envelope) and `request_id` is the id every subsequent public read takes — `GET /api/v1/verify/request/{id}` and the per-asset status poll. Deliberately NOT the shared `VerificationRequest` component: this path is public, and that component carries the authenticated-owner-only `computed_state` envelope, which must not be advertised here. It names `request_id` rather than `id` — the field the controller has always sent."""

    success: bool
    verification_url: str
    request_id: "ObjectId"
    expires_at: str

# ============================================================================
# 2FA
# ============================================================================

TwoFAActionType = Literal[
    "api_key_view", "api_key_create", "api_key_revoke", "api_key_regenerate", "phone_add", "phone_remove", "email_add", "email_remove", "account_delete", "master_key_change", "hitl_key_rotate", "revocation_bulk", "settings_write", "profile_update", "templates_write", "webhook_write", "delegation_lifecycle", "domain_remove", "profile_delete", "account_delete_cancel",
]

class Start2FARequest(TypedDict):
    """Request body for starting 2FA verification"""

    action_type: "TwoFAActionType"
    channel: Literal["telegram", "whatsapp", "sms", "email"]
    email_id: NotRequired[str]
    phone_id: NotRequired[str]
    ttl_seconds: NotRequired[int]
    single_use: NotRequired[bool]
    targets: NotRequired[list[str]]
