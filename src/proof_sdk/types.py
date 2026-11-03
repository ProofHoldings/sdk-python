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

class AccountExportReceipt(TypedDict):
    """A signed receipt for one download of an export; kept after the export and after the account is deleted"""

    id: str
    export_id: str
    downloaded_by: Literal["owner", "admin"]
    downloaded_at: str
    sha256: str
    size_bytes: int
    receipt: str
    notice_suppressed: bool

class AccountExportLatest(TypedDict):
    """The account's most recent export, or null, and the receipts of its downloads"""

    latest: Optional["AccountExportJob"]
    receipts: list["AccountExportReceipt"]

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
    amount: NotRequired[Literal["10", "50", "200", 10, 50, 200]]

class BalanceResponse(TypedDict):
    """The prepaid balance, from which proofs past the plan's included amount are drawn"""

    billing_enabled: bool
    balance: dict[str, Any]
    low_balance_threshold: int
    top_up_amounts: list[int]
    auto_top_up: dict[str, Any]

class CallbackSecret(TypedDict):
    """A sub-account's callback signing secret."""

    profile_id: str
    secret: str

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

class CompanyProfile(TypedDict):
    """The account's company profile: who the client is, printed on its invoices."""

    legal_name: str
    registration_code: Optional[str]
    country: str
    vat_number: Optional[str]
    no_vat_number: bool
    address_line1: str
    address_line2: Optional[str]
    city: str
    postal_code: str
    billing_email: str
    updated_at: Optional[str]
    vat_check: dict[str, Any]
    complete: bool

class CompanyResponse(TypedDict):
    """The account's company profile."""

    company: Optional["CompanyProfile"]

class ConfirmationResend(TypedDict):
    """One "Send again": when, who asked, and which channels it went to"""

    at: str
    actor: dict[str, Any]
    channels: list[dict[str, Any]]

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

class CreateWebhookEndpointRequest(TypedDict):
    """A new webhook endpoint. A sub-account key may create only one scoped `selected` to exactly its own sub-account."""

    url: str
    events: NotRequired[list[str]]
    scope: Literal["all", "selected"]
    profile_ids: NotRequired[list[str]]
    status: NotRequired[Literal["active", "disabled"]]
    description: NotRequired[Optional[str]]

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

class DelegationCarrier(TypedDict):
    """Where a delegation is still visible to a third party"""

    carrier: Literal["dns_pointer", "delegate_card"]
    state: Literal["present", "absent", "unchecked"]
    reason: str
    cardUrl: NotRequired[str]

class DelegationCarriersResponse(TypedDict):
    """Where this delegation is still visible to a third party"""

    carriers: list["DelegationCarrier"]

class DnsProviderMetadataItem(TypedDict):
    """What one DNS provider needs and can do. The keys are camelCase as sent; this body predates the snake_case convention and is kept as it is."""

    name: str
    requiredCredentials: list[str]
    optionalCredentials: list[str]
    capabilities: dict[str, Any]
    apiDocUrl: NotRequired[str]

class DnsProvidersResponse(TypedDict):
    """The DNS providers credentials can be saved for"""

    providers: dict[str, Any]
    count: int

HitlChannel = Union[dict[str, Any], dict[str, Any]]

HitlChannelType = Literal["telegram", "whatsapp", "browser"]

class HitlKeysPutResponse(TypedDict):
    """The keypair stored"""

    kid: str
    message: str

class HitlKeysResponse(TypedDict):
    """A HITL config's keypair. A caller with `hitl:read` (or a dashboard session) gets every field; a key holding `confirmations:create` without `hitl:read` gets `public_key` and `kid` only."""

    public_key: Optional[str]
    kid: str
    encrypted_private_key: NotRequired[str]
    kdf_salt: NotRequired[str]
    wrapped_dek: NotRequired[Optional[str]]
    dek_iv: NotRequired[Optional[str]]
    dek_tag: NotRequired[Optional[str]]
    backup_wrapped_dek: NotRequired[Optional[str]]
    backup_dek_iv: NotRequired[Optional[str]]
    backup_dek_tag: NotRequired[Optional[str]]

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

class AssetCredentialsCheck(TypedDict):
    """Whether the signed-in caller holds saved DNS provider credentials that can verify this domain asset"""

    authenticated: bool
    has_credentials: bool
    message: NotRequired[str]
    credentials: NotRequired[list[dict[str, Any]]]
    domain: NotRequired[Optional[str]]

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
    resends: NotRequired[list["ConfirmationResend"]]
    resolved_at: NotRequired[Optional[str]]
    created_at: str
    updated_at: str

class ConfirmationListQuery(TypedDict):
    """Query parameters for listing confirmations"""

    page: NotRequired[int]
    limit: NotRequired[int]
    status: NotRequired["ConfirmationStatusFilter"]
    hitl_id: NotRequired["ObjectId"]
    profile_id: NotRequired["ObjectId"]
    start_date: NotRequired[Optional[str]]
    end_date: NotRequired[Optional[str]]

class ConfirmationListResponse(TypedDict):
    """Paginated list of confirmations"""

    data: list["Confirmation"]
    pagination: dict[str, Any]

class ConfirmationResendResponse(TypedDict):
    """Counts only — the response never carries a link"""

    confirmation_id: "ObjectId"
    resent: int
    skipped: int

class ConfirmationWebhookPayload(TypedDict):
    """Body of `confirmation.approved` / `confirmation.denied`. A timeout is `confirmation.denied` with `response.channel` `system` and `response.text` `timeout`."""

    event: Literal["confirmation.approved", "confirmation.denied"]
    profile_id: Optional["ObjectId"]
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

class DnsCredentialResponse(TypedDict):
    """A saved DNS provider credential. The secret is never returned."""

    id: "ObjectId"
    provider: str
    name: str
    is_valid: bool
    domains_count: int
    last_used_at: NotRequired[str]
    last_validated_at: NotRequired[str]
    validation_error: NotRequired[str]
    created_at: str
    updated_at: str

class DnsCredentialListResponse(TypedDict):
    """The account's saved DNS provider credentials, ordered by provider"""

    data: list["DnsCredentialResponse"]

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

class HitlApproverKey(TypedDict):
    """An enrolled approver's public key. `authorization_id` is the approver's consent, which a v2 envelope is keyed by. `recipient` and `channel` are absent for a key holding `confirmations:create` without `hitl:read`."""

    authorization_id: "ObjectId"
    recipient: NotRequired[str]
    channel: NotRequired["AuthorizationChannel"]
    public_key: Optional[str]
    kid: str

class HitlApproverKeysResponse(TypedDict):
    """The approvers enrolled against a HITL config with a live consent"""

    approver_keys: list["HitlApproverKey"]

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

class LookalikeAlert(TypedDict):
    """An artifact whose name resembles one of the brand tokens, with the evidence checked"""

    id: "ObjectId"
    registry: str
    artifact_name: str
    canonical_id: Optional[str]
    match_kind: str
    brand_token: str
    match_evidence: str
    evidence: list[dict[str, Any]]
    first_seen_at: str
    notified_at: Optional[str]
    created_at: str

class LookalikeAlertList(TypedDict):
    """A page of alerts, newest first"""

    data: list["LookalikeAlert"]
    pagination: dict[str, Any]

class LookalikeReport(TypedDict):
    """One month's report; a month with no alerts is a report too"""

    id: "ObjectId"
    period: str
    period_start: str
    period_end: str
    alert_count: int
    artifacts_checked: dict[str, Any]
    bounds: list[dict[str, Any]]
    sent_at: Optional[str]

class LookalikeReportList(TypedDict):
    """A page of monthly reports, latest first"""

    data: list["LookalikeReport"]
    pagination: dict[str, Any]

class LookalikeWatchSubscription(TypedDict):
    """The account's Lookalike Watch subscription. Subscribe, read and cancel all answer it; only the cancel answer reads `canceled`, since a read after cancelling answers 404."""

    id: "ObjectId"
    status: Literal["active", "canceled"]
    brand_tokens: list[str]
    owned_namespaces: list[str]
    notify_email: str
    activated_at: Optional[str]
    last_report_period: Optional[str]
    created_at: str
    updated_at: str

class PlanChangePreviewResponse(TypedDict):
    """What a plan change would cost now and when it would take effect. Nothing is changed."""

    plan: "BillingPlan"
    change: Literal["upgrade", "downgrade", "keep"]
    amount_due: int
    currency: str
    effective_at: Optional[str]

class PlanChangeRequest(TypedDict):
    """The plan to move to. Custom is agreed per customer and cannot be chosen here."""

    plan: "BillingPlan"

class PlanChangeResponse(TypedDict):
    """The outcome of a plan change"""

    plan: "BillingPlan"
    change: Literal["upgrade", "downgrade", "keep"]
    status: Literal["changed", "scheduled", "kept", "payment_required"]
    effective_at: Optional[str]
    payment_url: Optional[str]

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

class ProfileOwnerLink(TypedDict):
    """A custom link on a sub-account, as stored (with its id)"""

    _id: "ObjectId"
    title: str
    url: str
    icon: NotRequired[str]
    is_visible: bool
    display_order: int

class ProfileTemplateContent(TypedDict):
    """Body for a profile-scoped template write. Distinct from the account-level `TemplateContent`: it also accepts `is_active`, which every read of the template returns — declaring `TemplateContent` here published a field callers could read and had no documented way to set."""

    subject: NotRequired[str]
    body: str
    button_text: NotRequired[str]
    button_url_template: NotRequired[str]
    is_active: NotRequired[bool]

class PublicProofItem(TypedDict):
    """A proof the owner chose to show on a sub-account, as the owner sees it"""

    asset_id: "ObjectId"
    type: Literal["phone", "email", "domain", "social", "wallet", "telegram_bot", "delegation"]
    display_value: str
    label: NotRequired[str]
    channel: NotRequired[str]
    verified_at: str
    is_visible: bool
    display_order: int
    mask_level: Literal["full", "partial", "hidden"]
    is_revoked: NotRequired[bool]
    delegate_type: NotRequired[Literal["human", "ai_agent"]]
    delegation_id: NotRequired["ObjectId"]

class ProfileOwnerResponse(TypedDict):
    """A sub-account as its owner sees it"""

    id: "ObjectId"
    profile_id: str
    username: NotRequired[Optional[str]]
    is_primary: bool
    display_name: NotRequired[str]
    bio: NotRequired[str]
    avatar_url: NotRequired[Optional[str]]
    verification_level: Literal["basic", "verified", "business"]
    is_business: bool
    business_name: NotRequired[str]
    public_proofs: list["PublicProofItem"]
    proof_order: "ProofOrder"
    custom_links: list["ProfileOwnerLink"]
    theme: "ProfileTheme"
    is_public: bool
    show_verification_dates: bool
    show_proof_channels: bool
    show_delegations: bool
    support_email: Optional[str]
    email_theme: Optional[Literal["dark", "light"]]
    view_count: int
    created_at: str
    updated_at: str

class ProfileOwnerListResponse(TypedDict):
    """The account's sub-accounts, as their owner sees them"""

    profiles: list["ProfileOwnerResponse"]
    count: int
    max_profiles: int

class PublicProofsResponse(TypedDict):
    """A sub-account's shown proofs after an update"""

    public_proofs: list["PublicProofItem"]
    proof_order: "ProofOrder"

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

class RefreshSessionResponse(TypedDict):
    """The session renewed; the new tokens travel in cookies. camelCase as sent; kept as it is because the dashboard reads these names."""

    success: bool
    expiresAt: str
    expiresIn: int

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

class ShareVerificationRequestEmailResponse(TypedDict):
    """The verification link was emailed"""

    success: bool
    message: str
    messageId: NotRequired[str]

class SmsNumbersByRegion(TypedDict):
    """Our SMS numbers, one entry per region and always all three. A region with no number configured carries an empty `did` and no QR code."""

    americas: "SessionSmsNumber"
    europe: "SessionSmsNumber"
    israel: "SessionSmsNumber"

StatusListToken = str

class SubscriptionResponse(TypedDict):
    """The account's subscription"""

    plan: "BillingPlan"
    status: Optional[Literal["active", "past_due", "unpaid", "canceled", "incomplete", "incomplete_expired", "trialing", "paused"]]
    current_period_start: Optional[str]
    current_period_end: Optional[str]
    cancel_at_period_end: bool
    scheduled_plan: NotRequired[Optional["BillingPlan"]]
    scheduled_change_at: NotRequired[Optional[str]]

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

    # Deprecated: Removed from the API (templates belong to a sub-account: use the templates resource with the sub-account's id); kept so code written for an earlier 1.x release keeps compiling, and dropped in the next major version.

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

    amount: Literal["10", "50", "200", 10, 50, 200]
    auto_top_up: NotRequired[bool]
    success_url: str
    cancel_url: str

class TopUpResponse(TypedDict):
    """Top-up checkout session creation response"""

    checkout_url: str

class TwoFactorEmailSelectionResponse(TypedDict):
    """No session started: choose which address the code goes to"""

    requires_email_selection: bool
    available_emails: list[dict[str, Any]]
    message: str

class TwoFactorMagicLinkResponse(TypedDict):
    """The step-up is complete"""

    status: Literal["verified"]
    action_type: str
    already_verified: NotRequired[bool]
    verified_at: NotRequired[str]
    grant_expires_at: NotRequired[str]
    grant_single_use: NotRequired[bool]

class TwoFactorSessionResponse(TypedDict):
    """A started 2FA session"""

    session_id: str
    channel: Literal["telegram", "whatsapp", "sms", "email"]
    status: Literal["pending"]
    expires_at: str
    second_method_recommended: NotRequired[bool]
    deep_link: NotRequired[str]
    qr_code: NotRequired[str]
    qr_text: NotRequired[str]
    instructions: str
    sms_code: NotRequired[str]
    sms_message: NotRequired[str]
    sms_dids: NotRequired["SmsNumbersByRegion"]
    email: NotRequired[str]
    email_sent: NotRequired[bool]

class TwoFactorStatusResponse(TypedDict):
    """A 2FA session's state; the grant fields are present once `status` is `verified`"""

    session_id: str
    status: Literal["pending", "verified", "expired"]
    action_type: str
    verified_at: NotRequired[str]
    grant_expires_at: NotRequired[str]
    grant_single_use: NotRequired[bool]

class TwoFactorVerifyResponse(TypedDict):
    """The step-up is complete and its grant stored"""

    status: Literal["verified"]
    verified_at: str
    grant_expires_at: str
    grant_single_use: bool

class UpdateAuthorizationBody(TypedDict):
    """Request body for updating an authorization's owner-editable metadata (F22)"""

    label: Optional[str]

class UpdateCircleBody(TypedDict):
    """Request body for updating a Circle (name and owner name — the profile binding is create-only)"""

    name: NotRequired[str]
    owner_name: NotRequired[Optional[str]]

class UpdateCompanyRequest(TypedDict):
    """The whole company profile; a save replaces it. A VAT number must be an EU number belonging to `country` — refused otherwise with `400 vat_number_not_eu`, `vat_country_mismatch` or `vat_number_invalid`; neither a number nor `no_vat_number` is `400 vat_number_required`."""

    legal_name: str
    registration_code: NotRequired[Optional[str]]
    country: str
    vat_number: NotRequired[Optional[str]]
    no_vat_number: NotRequired[bool]
    address_line1: str
    address_line2: NotRequired[Optional[str]]
    city: str
    postal_code: str
    billing_email: str

class UpdateHitlBody(TypedDict):
    """Request body for updating a HITL configuration"""

    name: NotRequired[Optional[str]]
    channels: NotRequired[list["HitlChannel"]]
    timeout_seconds: NotRequired[float]

class UpdateWebhookEndpointRequest(TypedDict):
    """Fields to change. Moving to `all` drops `profile_ids`; `profile_ids` sent alone keeps a `selected` endpoint selected. A sub-account key can never widen an endpoint."""

    url: NotRequired[str]
    events: NotRequired[list[str]]
    scope: NotRequired[Literal["all", "selected"]]
    profile_ids: NotRequired[list[str]]
    status: NotRequired[Literal["active", "disabled"]]
    description: NotRequired[Optional[str]]

class UsageBalance(TypedDict):
    """The prepaid balance as `GET /me/billing/balance` reports it, without `billing_enabled` (the usage read carries that itself)"""

    balance: dict[str, Any]
    low_balance_threshold: int
    top_up_amounts: list[int]
    auto_top_up: dict[str, Any]

class UsagePeriod(TypedDict):
    """One month's production usage record"""

    period: str
    total_verifications: int
    total_confirmations: int
    total_authorizations: int
    total_delegations: int
    by_type: dict[str, Any]
    by_channel: dict[str, Any]
    by_hitl_channel: dict[str, Any]

class UsageTopChannel(TypedDict):
    """One channel's completion this period"""

    channel: str
    count: int
    completion_rate: float

class UsageResponse(TypedDict):
    """Usage for the current billing period, with the months asked for"""

    plan: str
    limit: int
    billing_enabled: bool
    card_on_file: bool
    hard_limit: Optional[int]
    balance: "UsageBalance"
    current_period: str
    current_usage: int
    percentage: int
    days_remaining: int
    projected_eom_usage: int
    is_on_track: Optional[bool]
    projection_unreliable: bool
    top_channels: list["UsageTopChannel"]
    channels_with_zero_completions: list[str]
    periods: list["UsagePeriod"]

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

class UserDomainVerificationCheckResponse(TypedDict):
    """The result of one check of the published record or file"""

    status: Literal["verified", "pending"]
    verified_at: NotRequired[str]
    asset: NotRequired[dict[str, Any]]
    message: NotRequired[str]

class UserDomainVerificationSessionResponse(TypedDict):
    """A self-service domain verification session"""

    session_id: str
    domain: str
    channel: Literal["dns", "http"]
    status: Literal["pending"]
    expires_at: str
    challenge: dict[str, Any]

class UserDomainVerificationStatusResponse(TypedDict):
    """A self-service domain verification session's state"""

    session_id: str
    domain: str
    channel: Literal["dns", "http"]
    status: Literal["pending", "verified", "failed"]
    created_at: str
    verified_at: NotRequired[str]
    challenge: NotRequired[dict[str, Any]]

class AssetAutoVerifyResult(TypedDict):
    """An asset verified from the signed-in account's existing proof or saved DNS credentials, with the request's status and progress after it"""

    status: Literal["verified"]
    verified_at: str
    request_status: "VerificationRequestStatus"
    progress: dict[str, Any]
    method: Literal["reused_proof", "ownership", "auto_dns"]
    original_verified_at: NotRequired[Optional[str]]
    provider: NotRequired[str]

class AssetCodeSubmitResult(TypedDict):
    """The asset, verified by the submitted code, with the request's status and progress after it. A wrong code answers 400."""

    status: Literal["verified"]
    verified_at: str
    request_status: "VerificationRequestStatus"
    progress: dict[str, Any]

class AssetVerificationCheckResult(TypedDict):
    """A DNS or HTTP check of a domain asset: verified (with the request's `request_status` and `progress` after it), or still pending with the attempts left. A record not found yet is this 200, not an error."""

    status: Literal["verified", "pending"]
    verified_at: NotRequired[str]
    request_status: NotRequired["VerificationRequestStatus"]
    progress: NotRequired[dict[str, Any]]
    message: NotRequired[str]
    attempts_remaining: NotRequired[int]

class ExtendVerificationRequestResponse(TypedDict):
    """The request's new expiry"""

    success: bool
    message: str
    expires_at: str
    status: "VerificationRequestStatus"

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

class IncomingVerificationRequestListItem(TypedDict):
    """A verification request the account was asked to complete"""

    id: "ObjectId"
    reference_id: NotRequired[str]
    status: "VerificationRequestStatus"
    computed_state: dict[str, Any]
    action_type: "ActionType"
    assets: list[dict[str, Any]]
    progress: dict[str, Any]
    expires_at: str
    completed_at: NotRequired[str]
    created_at: str
    requester: NotRequired[dict[str, Any]]

class IncomingVerificationRequestListResponse(TypedDict):
    """The verification requests the account was asked to complete, newest first"""

    data: list["IncomingVerificationRequestListItem"]
    pagination: dict[str, Any]

class OwnVerificationRequestListItem(TypedDict):
    """A verification request the account made, as its own list shows it. `public_profile_id` is the sub-account the request belongs to, absent when the request records no sub-account."""

    id: "ObjectId"
    reference_id: NotRequired[str]
    status: "VerificationRequestStatus"
    computed_state: dict[str, Any]
    action_type: "ActionType"
    source: Literal["dashboard", "api", "demo", "agent"]
    api_key_id: Optional[str]
    api_key_model: Optional[Literal["APIKey", "UserAPIKey"]]
    agent_name: Optional[str]
    assets: list[dict[str, Any]]
    progress: dict[str, Any]
    expires_at: str
    completed_at: NotRequired[str]
    created_at: str
    branding: NotRequired[dict[str, Any]]
    public_profile_id: NotRequired["ObjectId"]

class OwnVerificationRequestListResponse(TypedDict):
    """The verification requests the account made, newest first"""

    data: list["OwnVerificationRequestListItem"]
    pagination: dict[str, Any]
    stats: dict[str, Any]

class ProfileAssetOption(TypedDict):
    """An active asset offered for display on a public profile"""

    id: "ObjectId"
    type: "VerificationType"
    identifier: str
    channel: "AssetChannel"
    verified_at: NotRequired[str]
    proof_expires_at: NotRequired[Optional[str]]
    is_public: bool

class PublicVerificationRequest(TypedDict):
    """A verification request as its recipient sees it: masked identifiers, branding and progress, never a proof token. `action_context` is null when the request carries none."""

    id: "ObjectId"
    status: "VerificationRequestStatus"
    action_type: "ActionType"
    action_context: Optional["ActionContext"]
    business: Optional[dict[str, Any]]
    assets: list[dict[str, Any]]
    progress: dict[str, Any]
    partial_ok: bool
    redirect_url: NotRequired[str]
    expires_at: str
    completed_at: NotRequired[str]
    created_at: str

class VerifyEmailOtpResponse(TypedDict):
    """The address is now on the account"""

    status: Literal["verified"]
    email: str
    verified_at: str

class SettingsResponse(TypedDict):
    """Account settings"""

    webhook: "WebhookSettingsResponse"
    proof_expiry_days: Optional[int]
    hitl: dict[str, Any]
    # Deprecated: Removed from the API (account-level branding is retired: each sub-account carries its own branding, set with the profiles resource); kept so code written for an earlier 1.x release keeps compiling, and dropped in the next major version.
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

class DomainCredentialAccess(TypedDict):
    """Whether one saved DNS credential can reach a domain"""

    provider: str
    name: str
    has_access: bool
    is_registrar: NotRequired[bool]
    error: NotRequired[str]

class DomainCredentialCheckResponse(TypedDict):
    """Which of the account's DNS credentials can reach a domain"""

    has_credentials: bool
    has_accessible_credential: NotRequired[bool]
    accessible_credentials: list["DomainCredentialAccess"]
    detected_provider: str
    has_registrar_credentials: NotRequired[bool]
    registrar_provider: NotRequired[str]
    can_try_ownership_verification: NotRequired[bool]
    suggestion: NotRequired[str]

class DomainDnsRecord(TypedDict):
    """A DNS record a domain needs, for ownership or for email sending"""

    type: Literal["TXT", "CNAME", "MX"]
    name: str
    value: str
    purpose: Literal["ownership", "dkim", "mx", "spf"]
    priority: NotRequired[int]
    verified: bool
    verified_at: NotRequired[str]

class DomainEmailVerificationState(TypedDict):
    """An email verification of the domain. The code itself is never returned."""

    email_prefix: Literal["admin", "administrator", "webmaster", "hostmaster", "postmaster"]
    email_address: str
    expires_at: str
    attempts: int
    last_sent_at: NotRequired[str]
    verified_at: NotRequired[str]

class DomainRemovedResponse(TypedDict):
    success: Literal["true"]
    domain: str
    proofs_revoked: int
    delegations_revoked: list[dict[str, Any]]
    external: dict[str, Any]
    carriers: list[dict[str, Any]]
    notice: list[dict[str, Any]]

class DomainResendStatus(TypedDict):
    """Email-sending setup for a domain. Present once email sending has been set up."""

    domain_id: NotRequired[str]
    status: Literal["not_registered", "pending", "verified", "failed"]
    dkim_records: list["DomainDnsRecord"]
    registered_at: NotRequired[str]
    verified_at: NotRequired[str]
    last_checked_at: NotRequired[str]

DomainStatus = Literal[
    "pending", "verifying", "verified", "failed", "expired", "revoking", "reverification_required",
]

class DomainVerificationInstructions(TypedDict):
    """How to show control of the domain by the method it is set to"""

    method: str
    steps: list[str]
    dns_record: NotRequired[dict[str, Any]]
    http_file: dict[str, Any]

class Domain(TypedDict):
    """Domain record"""

    id: "ObjectId"
    domain: str
    status: "DomainStatus"
    detected_provider: str
    provider_name: str
    supports_auto_dns: bool
    verification_method: NotRequired[str]
    verification_subtype: NotRequired[Literal["dns_record", "ownership"]]
    for_email_sending: bool
    for_verification: bool
    dns_records: list["DomainDnsRecord"]
    actual_dns_host: NotRequired[str]
    actual_dns_host_name: NotRequired[str]
    has_dns_mismatch: bool
    dns_mismatch_warning: NotRequired[str]
    txt_record_name: str
    txt_record_value: str
    http_file_path: str
    http_file_content: str
    oauth_url: NotRequired[str]
    oauth_connected: bool
    godaddy_connected: bool
    supports_api_token: bool
    supports_api_key: bool
    has_provider_credentials: NotRequired[bool]
    provider_credential_name: NotRequired[str]
    provider: NotRequired[str]
    email_sending_enabled: NotRequired[bool]
    profile_id: NotRequired["ObjectId"]
    from_email: NotRequired[str]
    resend: NotRequired["DomainResendStatus"]
    email_verification: NotRequired["DomainEmailVerificationState"]
    verified_providers: list[str]
    check_count: int
    last_checked_at: NotRequired[str]
    error_message: NotRequired[str]
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

class DomainDetailResponse(TypedDict):
    """A domain with the steps to verify it"""

    data: "Domain"
    instructions: "DomainVerificationInstructions"

class DomainEmailVerificationResponse(TypedDict):
    """A verification code emailed to an address on the domain"""

    data: "Domain"
    message: str
    email_sent_to: NotRequired[str]
    expires_in_minutes: NotRequired[int]

class DomainListResponse(TypedDict):
    """The account's domains, newest first"""

    data: list["Domain"]

class DomainVerificationResponse(TypedDict):
    """Domain verification initiation response"""

    id: "ObjectId"
    domain: str
    status: Literal["pending", "verified"]
    verification_method: str
    dns_record: dict[str, Any]
    http_file: dict[str, Any]
    provider: dict[str, Any]

class DomainVerificationResult(TypedDict):
    """The domain after a verification check, by DNS or by an emailed code"""

    data: "Domain"
    verified: bool
    renewed: NotRequired[bool]
    message: str

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

class AddEmailSessionResponse(TypedDict):
    """An email-add session: a code was emailed to the address"""

    session_id: str
    email: str
    channel: Literal["otp"]
    status: Literal["pending"]
    expires_at: str
    instructions: str
    email_sent: bool
    email_error: NotRequired[str]

class AddEmailStatusResponse(TypedDict):
    """An email-add session's state"""

    session_id: str
    email: str
    channel: Literal["otp"]
    status: Literal["pending", "verified"]
    verified_at: NotRequired[str]

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

class AddPhoneStatusResponse(TypedDict):
    """A phone-add session's state"""

    session_id: str
    phone_number: NotRequired[str]
    channel: Literal["telegram", "whatsapp", "sms"]
    status: Literal["pending", "verified"]
    verified_at: NotRequired[str]

class AddPhoneSessionResponse(TypedDict):
    """A phone-add session: the person proves the number by sending from it over `channel`"""

    session_id: str
    channel: Literal["telegram", "whatsapp", "sms"]
    status: Literal["pending"]
    expires_at: str
    deep_link: NotRequired[str]
    qr_code: NotRequired[str]
    qr_text: NotRequired[str]
    instructions: str
    sms_code: NotRequired[str]
    sms_message: NotRequired[str]
    sms_dids: NotRequired["SmsNumbersByRegion"]

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

AuthSessionStatus = Literal["pending", "verified", "expired", "completed_elsewhere"]

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
    profile_id: Optional["ObjectId"]
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

    checkout_url: str
    url: str

class PortalRequest(TypedDict):
    """Request body for creating a Stripe billing portal session"""

    return_url: str

class PortalResponse(TypedDict):
    """Billing portal session creation response"""

    portal_url: str
    url: str

# ============================================================================
# Settings
# ============================================================================

class BrandingSettings(TypedDict):
    """Branding settings"""

    # Deprecated: Removed from the API (account-level branding is retired: each sub-account carries its own branding, set with the profiles resource); kept so code written for an earlier 1.x release keeps compiling, and dropped in the next major version.

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
    hitl: NotRequired[dict[str, Any]]

class UpdateSettingsResponse(TypedDict):
    """Account settings as stored after the update. Carries `webhook.secret` when THIS request created or rotated it — the only response that ever does."""

    success: bool
    webhook: "WebhookSettingsResponse"
    proof_expiry_days: Optional[int]
    hitl: dict[str, Any]
    # Deprecated: Removed from the API (account-level branding is retired: each sub-account carries its own branding, set with the profiles resource); kept so code written for an earlier 1.x release keeps compiling, and dropped in the next major version.
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
    """Request body for submitting the code we emailed (`submitCodeSchema`)"""

    code: NotRequired[str]
    # Deprecated: Removed from the API (the route reads the code from `code`, which `verifications.submit` already sends); kept so code written for an earlier 1.x release keeps compiling, and dropped in the next major version.
    challenge_code: str
    # Deprecated: Removed from the API (the route never read it; send only `code`); kept so code written for an earlier 1.x release keeps compiling, and dropped in the next major version.
    source_identifier: NotRequired[str]

class SubmitVerificationCodeRequest(TypedDict):
    """Request body for submitting a verification code"""

    code: str

VerificationChannel = Literal[
    "whatsapp", "telegram", "sms", "email", "dns", "http", "auto", "github", "google", "facebook", "x", "linkedin", "instagram", "youtube", "tiktok", "ethereum", "solana", "bitcoin", "coinbase", "kraken", "telegram_bot_token",
]

VerificationConfidence = Literal["high", "standard", "degraded"]

class VerificationRequestExistingProofs(TypedDict):
    """The recipient's own proofs that could answer the request's unverified assets (Smart Reuse)"""

    request_id: str
    user_logged_in: bool
    assets: list[dict[str, Any]]
    reusable_count: int
    total_required: int

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

class SubmitChallengeResponse(TypedDict):
    """Result of submitting the code we emailed"""

    id: "ObjectId"
    status: "VerificationStatus"
    attempts: int
    max_attempts: int
    verified_at: NotRequired[str]
    proof: NotRequired[dict[str, Any]]
    message: NotRequired[str]
    attempts_remaining: NotRequired[int]

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

class VerificationCompletedWebhookPayload(TypedDict):
    """Body of `verification.completed` — a direct verification (`POST /verifications`, or the winning channel of a multi-channel group) or a phone-first session that completed. Sent once per verification id."""

    event: Literal["verification.completed"]
    profile_id: Optional["ObjectId"]
    verification_id: "ObjectId"
    type: "VerificationType"
    channel: "VerificationChannel"
    identifier: Optional[str]
    status: Literal["verified"]
    environment: Literal["production", "test"]
    external_user_id: Optional[str]
    client_metadata: dict[str, Any]
    verified_at: Optional[str]
    proof_token: str
    proof_expires_at: Optional[str]
    confidence: NotRequired["VerificationConfidence"]
    session_id: NotRequired[str]
    test: NotRequired[bool]

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
    channel: NotRequired["VerificationChannel"]

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

class VerificationRequestAssetStatus(TypedDict):
    """One asset's verification status, polled by the recipient page. `request_status` is the request's, expiry re-derived: `cancelled` or `expired` ends the flow while the asset stays `pending`."""

    asset_index: int
    type: "VerificationType"
    identifier: Optional[str]
    status: Literal["pending", "verified", "failed"]
    verified_at: NotRequired[str]
    confidence: NotRequired["VerificationConfidence"]
    request_status: "VerificationRequestStatus"
    progress: dict[str, Any]

class VerificationRequestProofsResponse(TypedDict):
    """Proof tokens for verified assets in a verification request"""

    proofs: list[dict[str, Any]]

# ============================================================================
# Profiles
# ============================================================================

class ClaimUsernameRequest(TypedDict):
    """Request body for claiming a username"""

    username: str

class ClaimUsernameResponse(TypedDict):
    """The claimed username"""

    username: str
    username_claimed_at: str
    profile_url: str

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

class PublicProfileLeadingProof(TypedDict):
    """The asset a profile's preview card, share tags and badge lead with: the first proof in the profile's order that is not hidden."""

    type: Literal["phone", "email", "domain", "social", "wallet", "telegram_bot"]
    display_value: str
    label: Optional[str]

class PublicProfileLink(TypedDict):
    """A visible link on a public profile."""

    title: str
    url: str
    icon: NotRequired[str]

class PublicProfileProof(TypedDict):
    """A proof shown on a public profile. The channel and the mask level are never published."""

    type: Literal["phone", "email", "domain", "social", "wallet", "telegram_bot", "delegation"]
    display_value: str
    label: NotRequired[str]
    verified_at: NotRequired[str]

class PublicProfileView(TypedDict):
    """A public profile as anyone may read it (`GET /api/v1/profiles/p/{profileId}`, `GET /api/v1/profiles/u/{username}`)."""

    profile_id: str
    username: NotRequired[Optional[str]]
    display_name: NotRequired[str]
    bio: NotRequired[str]
    avatar_url: NotRequired[Optional[str]]
    business_name: NotRequired[str]
    verification_level: Literal["basic", "verified", "business"]
    is_business: bool
    proofs: list["PublicProfileProof"]
    leading_proof: NotRequired[Optional["PublicProfileLeadingProof"]]
    links: list["PublicProfileLink"]
    theme: NotRequired["ProfileTheme"]
    delegations: NotRequired[Optional[list["PublicProfileDelegation"]]]

class UpdateProfileProofsRequest(TypedDict):
    """Request body for updating which proofs are displayed on a profile"""

    proofs: list["ProfileProofEntry"]
    proof_order: NotRequired["ProofOrder"]

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
    """Deprecated. NO endpoint returns this shape: the public reads return `PublicProfileView` and the owner's operations return `ProfileOwnerResponse`. Kept for released SDK types; removed in the next major."""

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
    leading_proof: NotRequired[Optional["PublicProfileLeadingProof"]]
    proof_order: NotRequired["ProofOrder"]
    verification_level: NotRequired[Literal["basic", "verified", "business"]]
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

ProofOrder = Literal["default", "owner"]

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
    last_fallback_at: NotRequired[Optional[str]]
    last_fallback_variables: NotRequired[list[str]]

class TemplateContent(TypedDict):
    """Template content fields"""

    subject: NotRequired[str]
    body: str
    button_text: NotRequired[str]
    button_url_template: NotRequired[str]

class TemplateDefaultsResponse(TypedDict):
    """The platform default templates"""

    defaults: dict[str, Any]

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

class TemplateSendWarning(TypedDict):
    """Why a saved template would never be sent as written. The save still succeeds."""

    code: Literal["template_not_sent", "template_variable_not_filled"]
    message: str
    variables: NotRequired[list[str]]

class TemplateSendablePair(TypedDict):
    """A channel and message type some message is sent for, so a template saved for it is used."""

    channel: "TemplateChannel"
    message_type: "MessageType"
    variables: list[str]

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
# Sub-accounts
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

class WebhookEndpoint(TypedDict):
    """A webhook endpoint. Deliveries carry `X-Proof-Signature`, an HMAC-SHA256 with this endpoint's secret over `<X-Proof-Timestamp>.<body>`; the secret itself is returned only on create and rotate."""

    id: "ObjectId"
    url: str
    events: list[str]
    scope: Literal["all", "selected"]
    profile_ids: list["ObjectId"]
    status: Literal["active", "disabled"]
    description: Optional[str]
    legacy: bool
    secret_set: bool
    created_at: str
    updated_at: str

class WebhookEndpointList(TypedDict):
    """The endpoints the caller may see. A sub-account key sees only those scoped to exactly its own sub-account."""

    data: list["WebhookEndpoint"]

class WebhookEndpointWithSecret(TypedDict):
    """A webhook endpoint with its signing secret, returned once (create, rotate)."""

    id: "ObjectId"
    url: str
    events: list[str]
    scope: Literal["all", "selected"]
    profile_ids: list["ObjectId"]
    status: Literal["active", "disabled"]
    description: Optional[str]
    legacy: bool
    secret_set: bool
    created_at: str
    updated_at: str
    secret: str

WebhookEventType = Literal[
    "verification_request.completed", "verification_request.partial", "verification_request.expired", "verification.completed", "confirmation.approved", "confirmation.denied", "authorization.approved", "authorization.denied", "proof.revoked", "proof.suspended", "proof.unsuspended", "account.deletion_scheduled", "account.deletion_cancelled",
]

class WebhookDelivery(TypedDict):
    """Webhook delivery record"""

    id: "ObjectId"
    verification_request_id: Optional["ObjectId"]
    endpoint_id: Optional["ObjectId"]
    profile_id: Optional["ObjectId"]
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
    token_omitted_reason: NotRequired[Optional[Literal["source_gone", "token_absent", "token_changed"]]]
    response_body: Optional[str]
    updated_at: str

class WebhookDeliveryListItem(TypedDict):
    """Webhook delivery as listed: the payload and the receiver's response body are only on the detail"""

    id: "ObjectId"
    verification_request_id: Optional["ObjectId"]
    endpoint_id: Optional["ObjectId"]
    profile_id: Optional["ObjectId"]
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
    endpoint_id: NotRequired["ObjectId"]
    profile_id: NotRequired["ObjectId"]

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
    profile_id: Optional["ObjectId"]
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
    """Outbound webhook configuration — DEPRECATED (#421). An account switched over to webhook endpoints sees its account-wide (`legacy`) endpoint here: `url` is null while that endpoint is disabled, a `url` write updates or creates it, `url: null` disables it (its secret is kept), and `rotate_secret` rotates its secret. An account not yet switched over sees its settings fields, as before. Omitted for an API key bound to one sub-account."""

    url: Optional[str]
    events: list[str]
    secret_set: bool
    secret: NotRequired[str]
    deprecated: str

# ============================================================================
# Verify Flow
# ============================================================================

class StartAssetVerificationRequest(TypedDict):
    """Request body for starting asset verification in a verification request"""

    channel: Literal["telegram", "whatsapp", "sms", "email", "dns", "http", "telegram_bot_token", "github", "google", "facebook", "x", "linkedin", "instagram", "youtube", "tiktok", "ethereum", "solana", "bitcoin", "coinbase", "kraken"]
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

class StartAssetVerificationResponse(TypedDict):
    """A started verification for one asset: what to show the person, by asset type and channel. The six fields up to `expires_at` are always sent; each other field only for the type and channel its description names. sms: `sms_dids` lists all three regions here, a region with no number carrying an empty `did`."""

    verification_id: "ObjectId"
    asset_index: int
    type: "VerificationType"
    channel: "VerificationChannel"
    status: Literal["pending", "verified"]
    expires_at: str
    instructions: NotRequired[str]
    deep_link: NotRequired[str]
    qr_code: NotRequired[str]
    qr_text: NotRequired[str]
    message: NotRequired[str]
    phone_number: NotRequired[str]
    sms_code: NotRequired[str]
    sms_message: NotRequired[str]
    sms_dids: NotRequired["SessionSmsNumbers"]
    suggested_region: NotRequired[Literal["americas", "europe", "israel"]]
    email_sent: NotRequired[bool]
    email_error: NotRequired[str]
    record_type: NotRequired[Literal["TXT"]]
    record_name: NotRequired[str]
    record_value: NotRequired[str]
    file_path: NotRequired[str]
    file_content: NotRequired[str]
    file_url: NotRequired[str]
    email_sent_to: NotRequired[str]
    otp_code_length: NotRequired[int]
    verified_data: NotRequired[dict[str, Any]]
    proof_token: NotRequired[str]

# ============================================================================
# 2FA
# ============================================================================

TwoFAActionType = Literal[
    "api_key_view", "api_key_create", "api_key_revoke", "api_key_regenerate", "phone_add", "phone_remove", "phone_primary", "email_add", "email_remove", "email_primary", "account_delete", "master_key_change", "hitl_key_rotate", "revocation_bulk", "settings_write", "profile_update", "templates_write", "webhook_write", "delegation_lifecycle", "company_update", "domain_remove", "profile_delete", "account_delete_cancel", "plan_change", "auto_top_up_change",
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
