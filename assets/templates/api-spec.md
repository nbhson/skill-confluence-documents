---
title: "{Service} — API Specification"
doc_id: API-{DOMAIN}-001
version: 1.0
status: Draft
owner: "{API Owner}"
reviewers: ["{Tech Lead}", "{Security Reviewer}"]
jira: "{EPIC-KEY}"
space: "{SPACE}"
labels: [api, openapi, "{domain}"]
classification: Internal
updated: "{YYYY-MM-DD}"
---

{{meta}}

{{toc}}

## 1. Overview

The {Service} API exposes {capability} to {consumer group}. This page defines the public contract: authentication, resources, payloads, error semantics, rate limits and compatibility rules. The machine-readable OpenAPI document is the canonical schema; this page explains the behaviour a schema cannot express.

| Attribute | Value |
|---|---|
| Base URL (production) | `https://api.{domain}.example.com/v1` |
| Base URL (sandbox) | `https://api.sandbox.{domain}.example.com/v1` |
| Protocol | HTTPS, JSON (`application/json; charset=utf-8`) |
| Authentication | OAuth 2.0 client credentials |
| OpenAPI document | [openapi.yaml]({URL}) |
| Support channel | {Slack channel or email} |

:::info
**Compatibility promise.** Within a major version, we only add optional fields and new endpoints. Removing or renaming a field is a breaking change governed by section 7.
:::

## 2. Authentication

| Concern | Contract |
|---|---|
| Grant type | `client_credentials` |
| Token endpoint | `POST https://auth.{domain}.example.com/oauth2/token` |
| Access token lifetime | 15 minutes |
| Refresh | Request a new token; do not cache beyond expiry |
| Transport | `Authorization: Bearer <access_token>` |
| Clock skew | 60 seconds |

| Scope | Grants | Used by |
|---|---|---|
| `{resource}:read` | Read {resource} records | {Consumer} |
| `{resource}:write` | Create and update {resource} records | {Consumer} |
| `{admin}` | Administrative operations | {Operations only} |

```bash
curl -X POST "https://auth.{domain}.example.com/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}"
```

:::warning
Never embed client secrets in browser code, mobile binaries or public repositories. Rotate a leaked secret immediately and audit its usage.
:::

## 3. Endpoints

| Method | Path | Purpose | Auth | Idempotency |
|---|---|---|---|---|
| POST | `/v1/{resources}` | Create a {resource} | `{resource}:write` | `Idempotency-Key` required |
| GET | `/v1/{resources}/{id}` | Read one {resource} | `{resource}:read` | Safe, repeatable |
| GET | `/v1/{resources}` | List {resources} with pagination | `{resource}:read` | Safe, repeatable |
| PATCH | `/v1/{resources}/{id}` | Update selected fields | `{resource}:write` | `If-Match` required |
| DELETE | `/v1/{resources}/{id}` | Soft-delete a {resource} | `{resource}:write` | Idempotent by ID |

### 3.1 POST /v1/{resources}

Creates a {resource} for the authenticated tenant. The call returns `201 Created` with the canonical representation and a `Location` header.

| Parameter | In | Type | Required | Constraints |
|---|---|---|---|---|
| `Idempotency-Key` | header | string (UUID) | Yes | Reuse returns the original result for 24 hours |
| `{field_a}` | body | string | Yes | 1-64 characters, `^[A-Z0-9-]+$` |
| `{field_b}` | body | decimal(18,2) | Yes | Greater than 0 |
| `{field_c}` | body | enum | No | `{VALUE_1}`, `{VALUE_2}`; default `{VALUE_1}` |

| Status | Body | Meaning |
|---|---|---|
| 201 | `{resource}` | Created; `Location` points to the new resource |
| 400 | `{error}` | Validation failure; `details[]` names each field |
| 409 | `{error}` | Idempotency key reused with a different payload |
| 422 | `{error}` | Business rule rejection; see section 5 |

```json title="Request"
{
  "field_a": "EXAMPLE-001",
  "field_b": 1250.00,
  "field_c": "VALUE_1"
}
```

```json title="201 Created"
{
  "id": "9f1c2b7e-4a6d-4f0e-9a21-2f6f7d8c1b30",
  "field_a": "EXAMPLE-001",
  "field_b": 1250.00,
  "field_c": "VALUE_1",
  "status": "active",
  "created_at": "2026-11-17T08:30:00Z"
}
```

### 3.2 GET /v1/{resources}/{id}

Returns one {resource} visible to the caller's tenant.

| Parameter | In | Type | Required | Constraints |
|---|---|---|---|---|
| `id` | path | string (UUID) | Yes | Existing resource identifier |
| `expand` | query | string | No | Comma-separated: `owner`, `history` |

| Status | Body | Meaning |
|---|---|---|
| 200 | `{resource}` | Resource found |
| 403 | `{error}` | Caller lacks `{resource}:read` for this tenant |
| 404 | `{error}` | Resource does not exist or is outside the caller's tenant |

## 4. Data Models

### 4.1 {Resource}

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `id` | string (UUID) | Yes | Immutable | Server-generated identifier |
| `field_a` | string | Yes | 1-64 characters | Human-readable business key |
| `field_b` | decimal(18,2) | Yes | Greater than 0 | {What the amount represents} |
| `field_c` | enum | Yes | `{VALUE_1}`, `{VALUE_2}` | {What the state controls} |
| `status` | enum | Yes | `active`, `inactive`, `archived` | Lifecycle state |
| `created_at` | string (ISO 8601) | Yes | UTC, `Z` suffix | Creation time |
| `updated_at` | string (ISO 8601) | Yes | UTC, `Z` suffix | Last modification time |

### 4.2 Enumerations

| Enum | Values | Stability |
|---|---|---|
| `status` | `active`, `inactive`, `archived` | New values may be added; clients must tolerate unknown values |
| `{field_c}` | `{VALUE_1}`, `{VALUE_2}` | Adding a value is non-breaking |

:::note
Treat enums as open sets. A client that fails on an unknown enum value will break on a non-breaking server release.
:::

## 5. Error Handling

Every error uses the same envelope. `code` is stable and safe to branch on; `message` is human-readable and may change.

```json title="Error envelope"
{
  "error": {
    "code": "RESOURCE_CONFLICT",
    "message": "The resource already exists for this tenant.",
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    "details": [
      {"field": "field_a", "issue": "duplicate"}
    ]
  }
}
```

| Code | HTTP | Meaning | Retry | Client action |
|---|---|---|---|---|
| `VALIDATION_FAILED` | 400 | Request body or query is invalid | No | Fix `details[]` and resubmit |
| `UNAUTHENTICATED` | 401 | Missing, expired or invalid token | No | Request a new token |
| `FORBIDDEN` | 403 | Token lacks scope or tenant access | No | Request the correct scope |
| `NOT_FOUND` | 404 | Resource does not exist for this tenant | No | Verify the identifier |
| `RESOURCE_CONFLICT` | 409 | State or idempotency conflict | No | Re-read state; do not blind-retry |
| `RATE_LIMITED` | 429 | Quota exceeded | Yes | Honour `Retry-After` |
| `DEPENDENCY_UNAVAILABLE` | 503 | Upstream dependency failed | Yes | Exponential backoff with jitter |

## 6. Rate Limits

| Scope | Limit | Window | Burst |
|---|---|---|---|
| Per client ID | 1,000 requests | 60 seconds | 100 |
| Per tenant | 10,000 requests | 60 seconds | 500 |
| `POST /v1/{resources}` | 100 requests | 60 seconds | 10 |

| Header | Direction | Meaning |
|---|---|---|
| `X-RateLimit-Limit` | Response | Requests allowed in the current window |
| `X-RateLimit-Remaining` | Response | Requests left in the current window |
| `X-RateLimit-Reset` | Response | Unix timestamp when the window resets |
| `Retry-After` | Response (429) | Seconds to wait before retrying |

## 7. Versioning

The major version lives in the path (`/v1`). Minor, backward-compatible changes ship without a version bump. Breaking changes follow the contract below.

| Change | Classification | Notice |
|---|---|---|
| Add an optional request field | Non-breaking | Changelog only |
| Add a response field | Non-breaking | Changelog only |
| Add an enum value | Non-breaking | Changelog only |
| Remove or rename a field | Breaking | 6 months notice, dual-write window |
| Change a field type or meaning | Breaking | New major version |
| Change authentication | Breaking | New major version |

## 8. Examples

### 8.1 Create a {resource}

```bash
curl -X POST "https://api.{domain}.example.com/v1/{resources}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Idempotency-Key: 3f8c1a52-9d4e-4a1b-8c2f-7e6d5a4b3c21" \
  -H "Content-Type: application/json" \
  -d '{"field_a":"EXAMPLE-001","field_b":1250.00,"field_c":"VALUE_1"}'
```

### 8.2 Handle a rate limit

```python
import time

def call_with_backoff(client, request, attempts=5):
    for attempt in range(attempts):
        response = client.send(request)
        if response.status_code != 429:
            return response
        delay = int(response.headers.get("Retry-After", "2"))
        time.sleep(delay * (2 ** attempt))
    raise RuntimeError("rate limit persisted after retries")
```

## 9. Change Log

| Version | Date | Author | Change | Jira |
|---|---|---|---|---|
| 1.0 | {YYYY-MM-DD} | {API Owner} | Initial public contract | {{jira:{EPIC-KEY}}} |
