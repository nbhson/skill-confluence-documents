---
name: fds-requirements
description: Functional design specification and requirement modelling — atomic requirements, FR/NFR/BR/AC identifier schemes, MoSCoW priority, Given-When-Then acceptance criteria and end-to-end traceability.
tags: [confluence, fds, requirements, acceptance-criteria, traceability]
related: [document-architecture, tables-matrices, jira-traceability]
---

# Confluence Documents Guide: FDS and Requirements

## 1. Definition

A Functional Design Specification states what a system must do, for whom, under which rules, and how acceptance will be proven. The unit of writing is the requirement: one observable outcome, one identifier, one owner, one source issue and at least one testable acceptance criterion. The FDS is the contract between Product, Engineering, QA and Operations; if two teams can read it and disagree about what "done" means, the requirement is unfinished.

## 2. Core Principles

- **Atomic:** one requirement, one outcome. If the sentence contains "and", split it or make the second clause a business rule.
- **Testable:** every requirement maps to at least one acceptance criterion with a concrete input and observable output.
- **Identified:** `FR-001`, `NFR-001`, `BR-001`, `AC-001` — IDs are stable and never reused.
- **Sourced:** every requirement names the Jira key that authorises it and the stakeholder who asked.
- **Outcome over implementation:** say what must be true, not which class or table to create.
- **Quantified NFRs:** "fast" is not a target; "p95 under 400 ms at 300 rps" is.
- **Traceable:** requirement → Jira → acceptance criterion → test evidence is one unbroken chain.
- **Change-controlled:** scope changes update the requirement row, the change log and the Jira issue together.

## 3. Spec Tokens

| Role | Token | Value | Notes |
|---|---|---|---|
| Requirement ID | `--req-id-format` | `FR-NNN`, `NFR-NNN`, `BR-NNN`, `AC-NNN` | Three digits, never reused |
| Priority | `--req-priority` | `Must, Should, Could, Won't` | MoSCoW, one value per row |
| FR columns | `--req-fr-columns` | `ID, Requirement, Priority, Jira, Status` | Jira column is mandatory |
| AC format | `--req-ac-format` | `Given, When, Then` | One scenario per row |
| Requirement length | `--req-max-words` | `60` | Longer means split or move detail |
| NFR target | `--req-nfr-target` | `numeric + unit + measurement` | No unmeasured adjectives |
| Traceability | `--req-traceability` | `FR → AC → Jira` | Every FR referenced by an AC |
| Status vocabulary | `--req-status-vocab` | `Draft, In Review, Approved, Deprecated` | Mirrors the page status |
| Change rule | `--req-change-control` | `row + changelog + Jira` | Three updates, one change |

## 4. Composition

- **With tables-matrices (guide 05):** the requirement index, acceptance matrix, decision log and risk register are tables, not bullet lists.
- **With jira-traceability (guide 07):** the Jira column and remote links connect the contract to delivery.
- **With api-contracts (guide 09):** API behaviour is referenced from FRs rather than duplicated; schemas live in the API section.
- **With review-governance (guide 10):** status transitions apply to each requirement row, not only to the page.

## 5. Signature Patterns

- **Requirement index + detail:** a summary table for scanning, then one H3 per requirement only where attributes and edge cases need space.
- **Given-When-Then acceptance table:** one row per scenario, one AC ID per row, explicit expected result.
- **Business-rule table:** rule, enforcement point, error code, Jira — the bridge between requirement and API.
- **Traceability matrix:** FR, AC, Jira, test evidence, status; the source for release readiness.
- **Open-question register:** ID, question, owner, needed-by date, status; unresolved questions block approval.

## 6. Real-World Use Cases

- **Payment or refund flow** — money movement requires atomic rules, idempotency and auditable approval thresholds.
- **Regulated onboarding** — each KYC step is a requirement with a compliance source and evidence.
- **Platform migration** — parity requirements compare old and new behaviour, with explicit exceptions.
- **Internal tooling** — even a small admin tool needs acceptance criteria; "it works" is not a release gate.

## 7. Combination Notes

### With other confluence-document skills

- **Tables and matrices:** requirements are tabular by nature; use the table guide's column budget and ID-first rule.
- **Jira traceability:** a requirement without a Jira key is an orphan; a Jira issue without an FDS section is an undocumented change.
- **API contracts:** keep the endpoint contract in the API section and reference it from the FR to avoid two sources of truth.
- **Review governance:** approval is per revision; requirements marked Approved must not drift silently.

### With design-system companions

- **skill-ux-writing:** requirement sentences follow the same plain-language rules as interface copy — active voice, one idea, no jargon.
- **skill-component-recipes:** UI behaviour requirements should reference component states (empty, loading, error), not describe pixels.

## 8. Anti-Patterns

- **Requirements written as bullets with no ID or source** — impossible to trace, test or approve
- **Bundled requirements joined by 'and'** — cannot be tested independently or prioritised separately
- **Non-functional targets without a number or measurement method** — "fast" and "secure" are not acceptance criteria
- **Acceptance criteria that merely restate the requirement** — no new observable evidence
- **Implementation details presented as requirements** — the design is frozen before review

### Accessibility Notes

Write requirements in plain language and define acronyms on first use. A requirement that a screen-reader user cannot understand is not testable by the whole team. For UI requirements, acceptance criteria must include keyboard, focus and announcement behaviour, not only pointer interaction.

## 9. Code Examples

### Example 1 — Requirement index and detailed requirement

```markdown
| ID | Requirement | Priority | Jira | Status |
|---|---|---|---|---|
| FR-001 | Create a partial or full refund for a captured payment | Must | {{jira:PAY-1420}} | {{status:green\|Approved}} |
| FR-002 | Replay the original result for a repeated idempotency key | Must | {{jira:PAY-1421}} | {{status:green\|Approved}} |

### FR-001 — Create a refund

The system **must** create a refund in `pending`, reserve the amount on the original payment and emit `refund.created` within 2 seconds.

| Attribute | Value |
|---|---|
| Trigger | `POST /v1/refunds` |
| Inputs | `payment_id`, `amount`, `reason_code`, `Idempotency-Key` |
| Outputs | `refund_id`, `status=pending`, `reserved_amount` |
| Preconditions | Payment `captured`, within 180 days, amount available |
| Failure | `REFUND_AMOUNT_EXCEEDED`, `PAYMENT_NOT_REFUNDABLE` |
```

### Example 2 — Acceptance criteria and NFR targets

```markdown
| AC ID | FR | Scenario | Given | When | Then |
|---|---|---|---|---|---|
| AC-001 | FR-001 | Partial refund | 500,000 VND available | Refund 200,000 VND | 201, pending, ledger reserves 200,000 |
| AC-002 | FR-001 | Over-refund | 100,000 VND available | Refund 150,000 VND | 422 REFUND_AMOUNT_EXCEEDED, no record |

| ID | Category | Target | Measurement |
|---|---|---|---|
| NFR-001 | Performance | p95 < 400 ms at 300 rps | 30-minute load test in staging |
| NFR-002 | Availability | 99.95% monthly | SLO dashboard, 28-day window |
```

```bash
# Enforce the contract before publishing.
python3 scripts/validate_document.py fds.md --profile fds --min-score 90 --publish
```

## 10. Implementation Checklist

- [ ] Every requirement has a unique ID, one observable outcome, a priority and a Jira key.
- [ ] No requirement sentence exceeds 60 words or hides a second requirement behind "and".
- [ ] Every FR is referenced by at least one AC row; uncovered IDs are listed explicitly.
- [ ] Acceptance criteria use Given-When-Then and state a concrete expected result.
- [ ] Every NFR has a numeric target, a unit and a measurement method.
- [ ] Business rules have an enforcement point and an error code.
- [ ] Open questions have an owner and a needed-by date; unresolved ones block approval.
- [ ] The change log and Jira issues reflect the same scope as the requirement table.
