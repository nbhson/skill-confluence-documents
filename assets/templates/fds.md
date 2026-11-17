---
title: "{Feature} — Functional Design Specification"
doc_id: FDS-{DOMAIN}-001
version: 0.1
status: Draft
owner: "{Owner}"
reviewers: ["{Reviewer 1}", "{Reviewer 2}"]
jira: "{EPIC-KEY}"
space: "{SPACE}"
labels: [fds, "{domain}"]
classification: Internal
updated: "{YYYY-MM-DD}"
---

{{meta}}

{{toc}}

## 1. Purpose and Scope

This document specifies the functional behaviour of {Feature}. It is the implementation contract for {service or team}, the source of truth for QA test design, and the reference for the operational readiness review.

:::info
**Decision required by {date}.** {One sentence stating the decision, the accountable owner, and the Jira key that tracks it.}
:::

### 1.1 In scope

| Capability | Included | Notes |
|---|---|---|
| {Capability A} | Yes | {Boundary or constraint} |
| {Capability B} | Yes | {Boundary or constraint} |
| {Capability C} | No | Out of scope; see 1.2 |

### 1.2 Out of scope

| Excluded capability | Reason | Handled by |
|---|---|---|
| {Capability X} | {Why it is excluded} | {Team, system or document} |
| {Capability Y} | {Why it is excluded} | {Team, system or document} |

## 2. Stakeholders

| Role | Name | Responsibility | RACI |
|---|---|---|---|
| Product owner | {Name} | Scope, priority and acceptance | A |
| Engineering lead | {Name} | Design and delivery | R |
| QA lead | {Name} | Test strategy and acceptance evidence | R |
| Security engineer | {Name} | Threat review and data handling | C |
| SRE / Operations | {Name} | Runbooks, monitoring and rollback | C |
| Compliance / Legal | {Name} | Regulatory review | C |
| {Dependency team} | {Name} | {Interface ownership} | I |

## 3. Assumptions and Constraints

| ID | Type | Statement | Impact if wrong |
|---|---|---|---|
| ASM-001 | Assumption | {Statement the design relies on} | {Design or scope impact} |
| ASM-002 | Assumption | {Statement the design relies on} | {Design or scope impact} |
| CON-001 | Constraint | {Technical, regulatory or timeline constraint} | {What must change} |
| CON-002 | Constraint | {Technical, regulatory or timeline constraint} | {What must change} |

## 4. Functional Requirements

The table below is the requirement index. Each requirement has one observable outcome, one priority and one source issue. Detailed behaviour and edge cases follow in 4.1.

| ID | Requirement | Priority | Jira | Status |
|---|---|---|---|---|
| FR-001 | {Short, testable statement of the requirement} | Must | {{jira:KEY-1}} | {{status:grey\|Draft}} |
| FR-002 | {Short, testable statement of the requirement} | Should | {{jira:KEY-2}} | {{status:grey\|Draft}} |
| FR-003 | {Short, testable statement of the requirement} | Could | {{jira:KEY-3}} | {{status:grey\|Draft}} |

### 4.1 FR-001 — {Requirement name}

The system **must** {observable behaviour}. The rule applies to {scope}, is enforced at {layer}, and returns {result} within {time boundary}.

| Attribute | Value |
|---|---|
| Trigger | {Event, schedule or user action} |
| Inputs | {Fields, formats and validation rules} |
| Outputs | {Response, state change or emitted event} |
| Preconditions | {Required state or permission} |
| Postconditions | {Guaranteed state after success} |
| Failure behaviour | {Error code, retry policy and user-visible message} |

#### Edge cases

| Case | Expected behaviour | Error code |
|---|---|---|
| {Boundary condition} | {What the system does} | {CODE or none} |
| {Duplicate request} | {Idempotent outcome} | {CODE or none} |
| {Dependency timeout} | {Fallback behaviour} | {CODE or none} |

### 4.2 FR-002 — {Requirement name}

The system **must** {observable behaviour}. {Add detail only where the summary table cannot carry it; do not repeat the table.}

| Attribute | Value |
|---|---|
| Trigger | {Event, schedule or user action} |
| Inputs | {Fields, formats and validation rules} |
| Outputs | {Response, state change or emitted event} |
| Preconditions | {Required state or permission} |
| Postconditions | {Guaranteed state after success} |
| Failure behaviour | {Error code, retry policy and user-visible message} |

## 5. Non-Functional Requirements

| ID | Category | Target | Measurement | Jira |
|---|---|---|---|---|
| NFR-001 | Performance | p95 latency under 300 ms at 500 requests/second | Load test in staging, 30-minute run | {{jira:KEY-4}} |
| NFR-002 | Availability | 99.95% monthly availability | SLO dashboard, 28-day window | {{jira:KEY-5}} |
| NFR-003 | Security | All data encrypted in transit and at rest | TLS 1.2+, KMS key policy review | {{jira:KEY-6}} |
| NFR-004 | Observability | Every failure emits a structured log and metric | Log schema review and alert test | {{jira:KEY-7}} |
| NFR-005 | Accessibility | WCAG 2.2 AA for all new screens | Axe audit plus manual keyboard test | {{jira:KEY-8}} |

## 6. Business Rules

| ID | Rule | Enforcement | Error code | Jira |
|---|---|---|---|---|
| {{anchor:br-001}} BR-001 | {Business condition that must hold} | {Service, database or policy engine} | {CODE} | {{jira:KEY-9}} |
| {{anchor:br-002}} BR-002 | {Business condition that must hold} | {Service, database or policy engine} | {CODE} | {{jira:KEY-10}} |
| BR-003 | {Business condition that must hold} | {Service, database or policy engine} | {CODE} | {{jira:KEY-11}} |

## 7. Data Model

The model below is normative. Field names match the API contract in section 8.

| Entity | Purpose | Retention | Owner |
|---|---|---|---|
| {Entity A} | {What it represents} | {Retention period} | {Team} |
| {Entity B} | {What it represents} | {Retention period} | {Team} |

### 7.1 {Entity A}

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `id` | string (UUID) | Yes | Immutable | Primary identifier |
| `status` | enum | Yes | {VALUE_1}, {VALUE_2} | Current lifecycle state |
| `amount` | decimal(18,2) | Yes | Greater than 0 | {What the amount represents} |
| `created_at` | timestamp | Yes | ISO 8601, UTC | Creation time |
| `{field}` | {type} | {yes/no} | {constraint} | {description} |

## 8. Integrations and API Contracts

| Consumer | Provider | Protocol | Purpose | Owner |
|---|---|---|---|---|
| {Consumer} | {Provider} | REST / HTTPS | {Purpose} | {Team} |

### 8.1 Endpoints

| Method | Path | Purpose | Auth | Idempotency |
|---|---|---|---|---|
| POST | `/v1/{resource}` | {Create or action} | OAuth 2.0 client credentials | `Idempotency-Key` header |
| GET | `/v1/{resource}/{id}` | {Read one resource} | OAuth 2.0 client credentials | Safe, repeatable |
| PATCH | `/v1/{resource}/{id}` | {Update resource} | OAuth 2.0 client credentials | Last write wins with `If-Match` |

### 8.2 Error handling

| Code | HTTP | Meaning | Retry | User-visible message |
|---|---|---|---|---|
| `{CODE_1}` | 400 | {Validation failure} | No | {Message shown to the user} |
| `{CODE_2}` | 409 | {State conflict} | No | {Message shown to the user} |
| `{CODE_3}` | 503 | {Dependency unavailable} | Yes, exponential backoff | {Message shown to the user} |

:::note
The canonical schema is published in the OpenAPI document. This section explains behaviour; it does not duplicate the schema.
:::

## 9. User Flows and UX Notes

1. The user opens {screen} and selects {entry point}.
2. The system validates {inputs} and displays {summary}.
3. The user confirms the action; the system calls {endpoint} and shows {progress state}.
4. On success, the system displays {confirmation} and records {audit event}.
5. On failure, the system keeps the user on the page, shows {message}, and offers {recovery action}.

:::info
**Empty, loading and error states are part of the acceptance criteria.** Do not specify only the happy path.
:::

| State | Expected experience | Copy reference |
|---|---|---|
| Loading | {Skeleton, spinner or progress text} | {Copy ID or link} |
| Empty | {Explanation and primary action} | {Copy ID or link} |
| Permission denied | {What the user sees and who to contact} | {Copy ID or link} |
| Dependency failure | {Retry behaviour and fallback} | {Copy ID or link} |

## 10. Acceptance Criteria

| AC ID | Requirement | Scenario | Given | When | Then |
|---|---|---|---|---|---|
| AC-001 | FR-001 | {Scenario name} | {Precondition} | {Action} | {Observable outcome} |
| AC-002 | FR-001 | {Boundary scenario} | {Precondition} | {Action} | {Observable outcome} |
| AC-003 | FR-002 | {Failure scenario} | {Precondition} | {Action} | {Error code and message} |
| AC-004 | NFR-001 | {Performance scenario} | {Load profile} | {Sustained traffic} | {Threshold met} |
| AC-005 | FR-003 | {Scenario name} | {Precondition} | {Action} | {Observable outcome} |

## 11. Risks and open questions

### 11.1 Risks

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| RSK-001 | {What could go wrong} | Medium | High | {Mitigation or contingency} | {Owner} | {{status:yellow\|Open}} |
| RSK-002 | {What could go wrong} | Low | Medium | {Mitigation or contingency} | {Owner} | {{status:grey\|Monitoring}} |

### 11.2 Open questions

| ID | Question | Owner | Needed by | Status |
|---|---|---|---|---|
| OQ-001 | {Question that blocks design or delivery} | {Owner} | {Date} | {{status:red\|Open}} |
| OQ-002 | {Question that blocks design or delivery} | {Owner} | {Date} | {{status:green\|Resolved}} |

## 12. Change Log

| Version | Date | Author | Change | Jira |
|---|---|---|---|---|
| 0.1 | {YYYY-MM-DD} | {Owner} | Initial draft | {{jira:EPIC-KEY}} |

## Appendix A. Glossary

| Term | Definition | Source |
|---|---|---|
| {Term} | {Definition a new engineer can understand} | {Glossary or standard} |
| {Term} | {Definition a new engineer can understand} | {Glossary or standard} |

## Appendix B. References

| Source | Link | Why it matters |
|---|---|---|
| Epic | {{jira:EPIC-KEY}} | Scope and delivery tracking |
| API contract | [OpenAPI specification]({URL}) | Canonical request and response schema |
| Design | [Figma flow]({URL}) | Screen-level behaviour and states |
| Runbook | [Operations runbook]({URL}) | On-call procedure and rollback |
