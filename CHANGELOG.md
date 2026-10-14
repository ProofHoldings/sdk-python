# Changelog

Notable changes to [`proof-holdings-sdk`](https://pypi.org/project/proof-holdings-sdk/) (import name
`proof_sdk`). Source: [ProofHoldings/sdk-python](https://github.com/ProofHoldings/sdk-python).

## 1.1.0 — 2026-10-14

The first release on PyPI.

### Added

- `Proof()` without a key resolves one: a non-empty `PROOF_API_KEY`, else the entry that
  `npx @proof-holdings/mcp-server login` saved in `~/.proof-holdings/credentials` for the client's base
  URL. The base URL is the `base_url` argument, else `PROOF_BASE_URL`, else
  `https://api.proof.holdings`. An explicit key behaves as before; an explicit empty key is an error.
- `verifications.delete_domain_verification(id)` deletes a domain verification attempt that is not
  verified (pending, verifying or failed). A verified domain is refused with 409 `domain_verified`.
- Types for account deletion and export, identifier, domain and project removal, the artifact claim
  lookup, and the Delegations section of a public profile.
- API-key listings carry `replaced_key_ids`: a key's usage covers every key it replaced.
- The `free` billing plan in `BillingPlan`.
