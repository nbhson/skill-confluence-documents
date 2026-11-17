---
name: api-contracts
description: API specification pages for Confluence — OpenAPI as the canonical schema, endpoint tables, parameters, error catalogues, idempotency, pagination, rate limits, compatibility promises and contract-test evidence.
tags: [confluence, api, openapi, contracts, errors, idempotency]
related: [fds-requirements, tables-matrices, diagrams, update-versioning]
---

# Confluence Documents Guide: API Contracts

## 1. Definition

An API specification page is the human-readable half of the contract. The OpenAPI document defines shape — paths, fields, types and required flags — while the page defines behaviour: what a field means, which errors a client must handle, whether a retry is safe, what happens at a rate limit, and what the compatibility promise is. When the two disagree, the schema wins for structure and the page is regenerated; a hand-maintained page that drifts from the schema is worse than no page at all.

## 2. Core Principles

- **Schema canonical for shape:** link the OpenAPI document and generate the field tables from it; never retype every property by hand.
- **Page canonical for behaviour:** semantics, ordering, side effects, retries and compatibility belong in prose the schema cannot express.
- **Errors are part of the contract:** every endpoint documents its failure codes, HTTP status, retryability and the client action required.
- **Examples are executable:** a request a reader can paste into a sandbox, with secrets redacted and realistic values.
- **Idempotency is explicit:** name the header or key, the retention window and the response on reuse with a different payload.
- **Auth is per endpoint:** scope, tenant boundary and token lifetime stated where the endpoint is defined.
- **Pagination is specified:** cursor or offset, page size, ordering guarantee and the termination condition.
- **Money and time are typed:** minor units or decimal scale, currency, ISO 8601 with UTC and an explicit precision.
- **Compatibility is a promise:** additive changes versus breaking changes are classified before release, not after complaints.
- **Contract tests are linked:** the evidence that the page and the running service agree.

## 3. Spec Tokens

| Role | Token | Value | Notes |
|---|---|---|---|
| Schema source | `--api-schema` | `openapi.yaml` | Linked from the overview; generated tables preferred |
| Endpoint heading | `--api-endpoint-heading` | `METHOD /path` | One H3 per endpoint |
| Parameter columns | `--api-param-columns` | `Name, In, Type, Required, Constraints` | No prose paragraphs in cells |
| Response columns | `--api-response-columns` | `Status, Body, Meaning` | Every documented status, including errors |
| Error columns | `--api-error-columns` | `Code, HTTP, Meaning, Retry, Client action` | Codes are stable identifiers |
| Idempotency | `--api-idempotency` | `header + window` | State reuse semantics with a different body |
| Pagination | `--api-pagination` | `cursor, limit, next_cursor` | Ordering guarantee stated |
| Compatibility | `--api-compat-classes` | `additive, breaking` | Breaking needs a major version and notice |
| Auth | `--api-auth` | `OAuth 2.0 client credentials` | Scope per endpoint |
| Example hygiene | `--api-example-secrets` | `redacted` | Real tokens and customer data forbidden |
| Contract evidence | `--api-contract-tests` | `CI run link` | Page version ↔ test run |

## 4. Composition

- **With fds-requirements (guide 02):** the FR states the capability; the API section states the contract and is referenced, never duplicated.
- **With tables-matrices (guide 05):** endpoint, parameter, response and error tables follow the same column budget and accessibility rules.
- **With diagrams (guide 06):** a sequence diagram shows the call order; the endpoint table remains normative.
- **With update-versioning (guide 08):** an API page and the service share a version boundary; breaking changes follow the deprecation protocol.
- **With review-governance (guide 10):** a consumer-facing API change requires the API owner and a consumer representative in review.
- **With automation-quality (guide 12):** schema diffing, example validation and contract tests run in CI before the page is published.

## 5. Signature Patterns

- **Overview block:** base URLs, protocol, auth, schema link, support channel and the compatibility promise in one table.
- **Endpoint index:** method, path, purpose, auth scope and idempotency — the map before the detail.
- **Endpoint anatomy:** purpose lede → auth and idempotency line → parameter table → request example → response table → error table.
- **Error catalogue:** one page-level table of stable codes with HTTP status, retry policy and the client action; endpoints reference the codes.
- **Idempotency contract:** key format, scope (per client or per tenant), retention window and the conflict response on reuse with a different payload.
- **Pagination contract:** parameters, default and maximum page size, ordering guarantee, `next_cursor` semantics and the empty final page.
- **Deprecation notice:** `Sunset` and `Deprecation` headers, successor endpoint, migration guide and removal date.
- **Contract evidence:** a table mapping page version to contract-test run, environment and date.

## 6. Real-World Use Cases

- **Public payments API** — error semantics and idempotency decide whether a merchant retries or double-charges a customer.
- **Internal service contract** — consumer teams need one page that states ownership, SLO and breaking-change policy before integration.
- **Partner onboarding** — sandbox URLs, scopes and executable examples shorten the first successful call.
- **API deprecation** — a sunset table with consumer, migration owner and deadline replaces an email thread.
- **Incident follow-up** — a missing rate-limit contract becomes a documented limit and a client backoff requirement.

## 7. Combination Notes

### With other confluence-document skills

- **FDS requirements:** a requirement references an endpoint ID; the JSON schema and error table live once, in the API page.
- **Tables and matrices:** parameter and error tables must have header rows, short cells and stable identifiers in the first column.
- **Diagrams:** a sequence diagram is evidence for ordering; it does not replace the response or error tables.
- **Update and versioning:** an additive change is a minor version; removing a field is a breaking change with a migration window.
- **Review governance:** the API owner approves the contract; a consumer representative confirms the migration path.

### With design-system companions

- **skill-ux-writing:** error messages shown to end users follow the same plain-language rules as interface copy.
- **skill-component-recipes:** API-driven UI states (loading, empty, error) must be derivable from the documented status codes.

## 8. Anti-Patterns

- **Specification page that only links the schema with no behavioural prose** — clients cannot decide retries, idempotency or error handling
- **API page that retypes every schema field by hand** — guaranteed drift from the OpenAPI source
- **Happy-path-only examples with no error response** — integration failures are discovered in production
- **Error codes renamed or reused without a version boundary** — client branches break silently
- **Rate limits and retry semantics left undocumented** — clients retry blindly and amplify the incident
- **Auth scopes described once in prose rather than per endpoint** — least privilege cannot be implemented
- **Pagination documented without an ordering guarantee** — consumers miss or duplicate records during sync

### Accessibility Notes

Every parameter table needs a header row and one parameter per row; screen readers announce column names, so avoid merged cells. Label code fences with a language so highlighting and assistive technology agree. Do not encode HTTP status or method by colour alone in a table — write `POST` and `429` as text. Link the schema with descriptive text (`OpenAPI 3.1 — refunds v1.4.2`), not "here". Diagrams need alt text that states the call order and failure path, not the file name.

## 9. Code Examples

### Example 1 — Endpoint section with behaviour and errors

````markdown
### POST /v1/refunds

Creates a refund for a captured payment. The ledger reserves the amount before the card adapter is called; a timeout after reservation returns `202` and reconciles asynchronously.

| Attribute | Value |
|---|---|
| Auth | `refunds:write` |
| Idempotency | `Idempotency-Key` header, 24-hour window |
| Success | `201 Created`, `Location: /v1/refunds/{refund_id}` |
| Async | `202 Accepted` when the card adapter times out after reservation |

| Parameter | In | Type | Required | Constraints |
|---|---|---|---|---|
| `Idempotency-Key` | header | UUID | Yes | Reuse with a different body returns `409` |
| `payment_id` | body | string (UUID) | Yes | Payment must be `captured` |
| `amount` | body | integer (minor units) | Yes | 1 to remaining refundable amount |
| `reason_code` | body | enum | Yes | `customer_request`, `duplicate`, `fraud` |

```json title="201 Created"
{
  "refund_id": "rf_9f1c2b7e",
  "payment_id": "pay_4a6d4f0e",
  "amount": 200000,
  "currency": "VND",
  "status": "pending",
  "created_at": "2026-11-17T08:30:00Z"
}
```

| Status | Code | Meaning | Retry | Client action |
|---|---|---|---|---|
| 409 | `IDEMPOTENCY_KEY_REUSED` | Same key, different payload | No | Generate a new key for a new intent |
| 422 | `REFUND_AMOUNT_EXCEEDED` | Amount above the refundable balance | No | Re-read the payment and correct the amount |
| 422 | `REFUND_WINDOW_EXPIRED` | Capture older than 180 days | No | Use the manual settlement process |
| 503 | `CARD_ADAPTER_UNAVAILABLE` | Upstream failure before reservation | Yes | Back off with jitter and retry the same key |
````

### Example 2 — Compatibility and contract evidence

```markdown
| Change | Class | Version | Notice | Consumer action |
|---|---|---|---|---|
| Add `reason_code` value | Additive | 1.4 | Changelog | Tolerate unknown enum values |
| Add optional `metadata` | Additive | 1.4 | Changelog | None |
| Rename `amount_minor` to `amount` | Breaking | 2.0 | 6 months, dual-read | Migrate before 2027-05-01 |
| Remove `legacy_refund_id` | Breaking | 2.0 | 6 months | Use `refund_id` |

| Page version | Contract test | Environment | Result | Date |
|---|---|---|---|---|
| 1.4.2 | [Run 2841]({URL}) | Staging | Passed, 42/42 | 2026-11-17 |
| 2.0.0-rc1 | [Run 2842]({URL}) | Staging | Passed, 47/47 | 2026-11-17 |
```

### Example 3 — Validate and publish the page

```bash
# The API profile requires the nine canonical sections and a synced changelog.
python3 scripts/validate_document.py api.md --profile api --min-score 90 --publish

# Review the storage diff, then publish with a version message that names the contract change.
python3 scripts/confluence.py diff --page-id 23456 --from-md api.md
python3 scripts/confluence.py update --page-id 23456 --from-md api.md \
  --message "v1.5 — errors: add REFUND_WINDOW_EXPIRED and retry guidance" --update-labels
python3 scripts/confluence.py verify --page-id 23456
```

## 10. Implementation Checklist

- [ ] The page links the canonical OpenAPI document and its version matches the text.
- [ ] Every endpoint has one H3, a purpose lede, auth scope and idempotency statement.
- [ ] Parameter and response tables use the standard columns and include every documented status.
- [ ] The error catalogue lists stable codes, HTTP status, retry policy and required client action.
- [ ] Every example is executable, uses realistic values and contains no live secrets or customer data.
- [ ] Money units, time format and currency are explicit in the field tables.
- [ ] Pagination states page-size bounds, ordering and the termination condition.
- [ ] Compatibility class is recorded for every change, and breaking changes have a migration deadline.
- [ ] Contract-test evidence links the page version to a CI run.
- [ ] The change log names the Jira issue and the contract change, and the page passes `--profile api --publish`.
