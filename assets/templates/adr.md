---
title: "ADR-{NNN}: {Decision title}"
doc_id: ADR-{DOMAIN}-001
version: 1.0
status: Approved
owner: "{Decision Owner}"
reviewers: ["{Architecture Reviewer}", "{Security Reviewer}"]
jira: "{DECISION-KEY}"
space: "{SPACE}"
labels: [adr, architecture, "{domain}"]
classification: Internal
updated: "{YYYY-MM-DD}"
---

{{meta}}

{{toc}}

## 1. Summary

{One paragraph: the decision, the context that forced it, and the consequence the team accepts. An ADR is a record of a choice, not a proposal.}

| Attribute | Value |
|---|---|
| Decision | {Short imperative statement} |
| Scope | {Systems, teams or products affected} |
| Decision date | {YYYY-MM-DD} |
| Effective date | {YYYY-MM-DD} |
| Supersedes | {ADR link or None} |
| Superseded by | {ADR link or None} |

:::info
**Status: {{status:green|Approved}}.** This decision is binding for {scope}. Changes require a new ADR that explicitly supersedes this one.
:::

## 2. Context

{Describe the forces at play: requirements, constraints, existing architecture, cost, risk and organisational context. A reader in two years must be able to judge whether the decision still applies.}

| Driver | Requirement or constraint | Weight | Source |
|---|---|---|---|
| {Driver} | {What must be true} | High / medium / low | {Document or review} |
| {Driver} | {What must be true} | High / medium / low | {Document or review} |
| {Driver} | {What must be true} | High / medium / low | {Document or review} |

## 3. Decision

We will **{decision in one sentence}**.

{Explain the mechanism: what will be built, bought or adopted; where the boundary sits; who owns it; and what is explicitly excluded from the decision.}

| Aspect | Decision detail |
|---|---|
| Technology or pattern | {Choice} |
| Ownership | {Team or role} |
| Runtime location | {Cluster, region, vendor} |
| Data classification | {Internal / confidential / restricted} |
| Operational model | {Managed service, self-hosted, hybrid} |
| Cost model | {Fixed, usage-based, estimate} |

## 4. Consequences

### 4.1 Positive

| Consequence | Measure | Owner |
|---|---|---|
| {Benefit} | {How success is measured} | {Owner} |
| {Benefit} | {How success is measured} | {Owner} |

### 4.2 Negative

| Consequence | Mitigation | Owner |
|---|---|---|
| {Accepted trade-off} | {How the impact is limited} | {Owner} |
| {Accepted trade-off} | {How the impact is limited} | {Owner} |

### 4.3 Follow-up decisions

| ID | Follow-up | Owner | Due | Status |
|---|---|---|---|---|
| DEC-001 | {Decision or migration required by this ADR} | {Owner} | {YYYY-MM-DD} | {{status:yellow\|Open}} |
| DEC-002 | {Decision or migration required by this ADR} | {Owner} | {YYYY-MM-DD} | {{status:grey\|Planned}} |

## 5. Alternatives

| Option | Summary | Why rejected | Revisit trigger |
|---|---|---|---|
| A | {Chosen option} | Selected | {Condition that would reopen the decision} |
| B | {Alternative} | {Reason} | {Condition} |
| C | {Do nothing} | {Reason} | {Condition} |

## 6. Change Log

| Version | Date | Author | Change | Jira |
|---|---|---|---|---|
| 1.0 | {YYYY-MM-DD} | {Decision Owner} | Decision approved | {{jira:{DECISION-KEY}}} |
