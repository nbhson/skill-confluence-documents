---
name: review-governance
description: Review and approval governance for enterprise Confluence pages — document states, entry and exit criteria, named reviewers, RACI, finding logs, version-specific sign-off, review cadence and deprecation.
tags: [confluence, review, governance, approval, sign-off, audit]
related: [document-architecture, update-versioning, jira-traceability, automation-quality]
---

# Confluence Documents Guide: Review and Governance

## 1. Definition

Review governance is the controlled path a document takes from draft to approved, and the controls that keep it true afterwards. A review is not a meeting or a comment thread; it is an event with a scope, a version, named reviewers, evidence and a recorded decision. Governance makes the difference between a page that says `Approved` and a page an auditor, a new engineer or a partner can actually rely on. If approval cannot be tied to a version and a decision, it is a badge, not a control.

## 2. Core Principles

- **One decision owner:** reviewers advise, the owner decides and is named in the control block.
- **Every state has entry and exit criteria:** `Draft`, `In Review`, `Approved`, `Deprecated`, `Superseded` are defined, not decorative.
- **Approve a version, not a page:** the sign-off records `doc_id`, version and content hash or change-log row.
- **Review the diff:** reviewers read what changed plus its blast radius, not the whole page every time.
- **Findings are tracked:** each finding has an ID, severity, owner and resolution; open findings block approval.
- **Separation where risk demands it:** regulated, security-relevant and customer-facing documents require an approver other than the author.
- **Silence is not approval:** a passed deadline never converts to `Approved`; it converts to `In Review` and an escalation.
- **Evidence is linked:** test runs, threat models, ADRs, legal sign-off and Jira issues are cited beside the decision.
- **Approval expires:** the control block carries a next-review date and the owner is accountable for the cadence.
- **Deprecate, never delete:** superseded pages keep their history and point to the successor.

## 3. Spec Tokens

| Role | Token | Value | Notes |
|---|---|---|---|
| Status vocabulary | `--gov-statuses` | `Draft, In Review, Approved, Deprecated, Superseded` | Same values as the control block |
| Approver rule | `--gov-approver` | `named owner` | One accountable decision maker |
| Quorum | `--gov-quorum` | `owner + required reviewers` | Domain-specific, stated in the page |
| Finding columns | `--gov-findings` | `ID, Section, Finding, Severity, Owner, Status` | Every finding is actionable |
| Decision values | `--gov-decisions` | `Approved, Approved with conditions, Rejected` | No "LGTM" as a decision |
| Review SLA | `--gov-sla` | `5 business days` | Escalate when breached |
| Re-review trigger | `--gov-rereview` | `scope, risk or API change` | Minor edits keep approval |
| Review cadence | `--gov-cadence` | `6 months` | Sensitive docs quarterly |
| Sign-off evidence | `--gov-evidence` | `version + test run + Jira` | Stored in the review record |
| Expiry | `--gov-expiry` | `next review date` | Past due means `In Review` |
| Deprecation notice | `--gov-deprecation` | `successor + date + reason` | Banner at the top of the page |

## 4. Composition

- **With document-architecture (guide 01):** the control block and change log are the governance surface; no separate status page.
- **With fds-requirements (guide 02):** requirement rows inherit the page state and cannot be `Approved` while the page is `In Review`.
- **With jira-traceability (guide 07):** the approval references the epic and every blocking finding has an issue key.
- **With update-versioning (guide 08):** any scope change on an approved page returns it to `In Review` and bumps the version.
- **With readability-accessibility (guide 11):** the review checklist includes accessibility evidence, not only content correctness.
- **With automation-quality (guide 12):** CI enforces the mechanical checks so reviewers spend their time on meaning.

## 5. Signature Patterns

- **State transition table:** state, entry criteria, exit criteria, who can move it and what evidence is required.
- **RACI:** role, name, responsibility and whether they are accountable, consulted or informed.
- **Review record:** document ID, version, scope, reviewers, decision, conditions, date and Jira key in one block.
- **Finding log:** ID, section anchor, finding, severity, owner, status and resolution; open P1/P2 findings block approval.
- **Conditional approval:** conditions with an owner and a due date, and the state remains `In Review` until they close.
- **Review cadence matrix:** document type, cadence, trigger and owner; sensitive documents reviewed more often.
- **Sign-off table:** reviewer, role, scope reviewed, decision and date — one row per person.
- **Deprecation review:** reason, successor, migration deadline and the communication owner.

## 6. Real-World Use Cases

- **Regulated FDS** — an auditor walks from approval to version, reviewer and evidence without asking for a meeting.
- **Security review** — the threat model is approved by security and the page records the scope that was reviewed.
- **Partner-facing API** — a consumer representative signs the migration plan before a breaking change ships.
- **Quarterly document health check** — stale approved pages move to `In Review` and owners are notified.
- **Post-incident governance** — action items are tracked in Jira and the postmortem stays `In Review` until they have owners and dates.

## 7. Combination Notes

### With other confluence-document skills

- **Document architecture:** status, owner and reviewers live in one control block; a second status table is a contradiction waiting to happen.
- **FDS requirements:** approving the page approves the requirement set at that version; later row edits need re-review.
- **Jira traceability:** a blocking finding without a Jira key is invisible to delivery; link it before the review closes.
- **Update and versioning:** the version message and the review record must describe the same change.
- **Automation and quality:** automate lint, links and changelog sync; do not automate the judgement of whether the content is correct.

### With design-system companions

- **skill-design-review:** the same gate structure applies — criteria, evidence, named decision, recorded outcome.
- **skill-ux-writing:** review comments must be specific and actionable; "improve wording" is not a finding.
- **skill-accessibility:** an accessibility review is part of the governance checklist, not a separate optional pass.

## 8. Anti-Patterns

- **LGTM comment with no version or scope** — approval cannot be tied to what was actually read
- **Approval by silence when the deadline passes** — unreviewed content ships with a green badge
- **Status changed to Approved without evidence links** — the badge is decoration and the audit fails
- **Reviewing the entire page for a one-row change** — reviewers burn out and stop reading carefully
- **Approved page with no next-review date** — stale contracts remain authoritative long after they are true
- **Review conducted only in chat with no recorded decision** — the outcome disappears with the channel
- **Self-approval on a regulated document with no separation of duties** — a control failure, not a shortcut

### Accessibility Notes

The review checklist must include keyboard, focus, zoom and screen-reader evidence for any document that specifies a UI. Status macros need a text label; a green lozenge alone is not an approval. The sign-off table needs a header row and one reviewer per row so assistive technology can map decisions to people. Review comments should cite the section anchor and quote the sentence under discussion; "see above" is ambiguous for everyone and unusable in a transcript. Meeting-only reviews exclude reviewers who cannot attend; keep a written record with the same evidence.

## 9. Code Examples

### Example 1 — State machine and review record

```markdown
| State | Entry criteria | Exit criteria | Who moves it | Evidence |
|---|---|---|---|---|
| Draft | Author has a complete outline | Required sections present; lint passes | Author | Lint report |
| In Review | Version frozen; reviewers named | All blocking findings closed; quorum met | Owner | Finding log |
| Approved | Decision recorded; evidence linked | Scope change or review expiry | Owner | Sign-off table |
| Deprecated | Successor exists | Successor published and linked | Owner | Deprecation banner |
| Superseded | Successor approved | None; page is read-only | Space admin | Link to successor |

:::info
**Review record — FDS-PAY-014 v1.1.** Scope: BR-004 dual approval, sections 6.2 and 10. Decision: **Approved with conditions**. Reviewers: Risk Operations (accountable), Payments Engineering, Compliance. Conditions: add the ledger evidence link by 2026-11-24. Tracking: {{jira:PAY-1455}}.
:::
```

### Example 2 — Finding log and sign-off table

```markdown
| ID | Section | Finding | Severity | Owner | Status |
|---|---|---|---|---|---|
| FND-001 | {#br-004} | Approval threshold conflicts with the risk policy | P1 | Risk Ops | Closed |
| FND-002 | {#ac-012} | Acceptance criterion does not cover timeout | P2 | QA Lead | Closed |
| FND-003 | {#data-model} | Ledger evidence link missing | P2 | Payments Eng | Open — blocks approval |

| Reviewer | Role | Scope reviewed | Decision | Date |
|---|---|---|---|---|
| Lê Thu Hà | Risk Operations | Sections 6.2, 10, Appendix B | Approved with conditions | 2026-11-17 |
| Trần Minh Quân | Payments Engineering | Sections 4, 6, 8 | Approved | 2026-11-17 |
| Nguyễn Minh An | Author | Full document | Submitted for review | 2026-11-16 |
```

### Example 3 — Enforce the gate before changing state

```bash
# 1. Freeze the version and capture the exact reviewed storage.
python3 scripts/validate_document.py fds.md --profile fds --min-score 90 --publish
python3 scripts/confluence.py get --page-id 12345 --out .work/fds-reviewed.storage.html

# 2. After the review, publish the approved version with the decision in the message.
python3 scripts/confluence.py update --page-id 12345 --from-md fds.md \
  --message "v1.1 — approved after Risk Ops review; condition FND-003 tracked in PAY-1455"

# 3. Verify and label the approved revision.
python3 scripts/confluence.py verify --page-id 12345
python3 scripts/confluence.py labels --page-id 12345 --add approved --remove in-review
```

## 10. Implementation Checklist

- [ ] The page uses the controlled status vocabulary and has one named accountable owner.
- [ ] Every state has written entry and exit criteria, including who may move it.
- [ ] The review record states the version, scope, reviewers, decision, conditions and date.
- [ ] Approval is tied to a version and evidence, not to a comment or a meeting.
- [ ] All P1/P2 findings are closed or explicitly accepted with an owner and date.
- [ ] The sign-off table lists each reviewer, role, scope and decision.
- [ ] The control block carries a next-review date; overdue pages return to `In Review`.
- [ ] Scope changes on an approved page trigger re-review and a version bump.
- [ ] Deprecated pages name the successor and retain their history.
- [ ] The accessibility checklist is part of the review evidence for UI-facing documents.
