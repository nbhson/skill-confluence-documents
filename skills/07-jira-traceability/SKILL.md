---
name: jira-traceability
description: Linking Confluence specifications to Jira — issue keys in tables, Jira macros, remote links, two-way traceability, status drift and the label taxonomy.
tags: [confluence, jira, traceability, remote-links, labels]
related: [fds-requirements, tables-matrices, update-versioning]
---

# Confluence Documents Guide: Jira Traceability

## 1. Definition

Traceability is the ability to walk from a requirement in Confluence to the Jira issue that authorises it, and from a Jira issue to the page that specifies it. It is a property of the link graph, not a paragraph that mentions a ticket number. Every requirement row carries a key, every published page carries a remote link, and status is read live from Jira rather than copied into prose.

## 2. Core Principles

- **Every requirement has a source issue:** the Jira column is mandatory, not decorative.
- **Link both directions:** the page links to the issue; the issue has a web link back to the page.
- **Key in the table, status live:** use `{{jira:KEY}}` or the Jira column; do not paste a status that will be stale tomorrow.
- **Epic is not enough:** epic-level links give scope; story-level rows give traceability.
- **One issue can cover many requirements:** do not invent a ticket per row; map many-to-one explicitly.
- **Labels are a controlled taxonomy:** `fds`, `api`, `rfc`, `runbook`, `approved`, `deprecated` — not free-form tags.
- **Drift is expected:** reconcile page and Jira at every review; record the reconciliation date.
- **Never duplicate the description:** Jira owns delivery status; Confluence owns the contract.

## 3. Spec Tokens

| Role | Token | Value | Notes |
|---|---|---|---|
| Issue key | `--jira-key-format` | `PROJECT-123` | Uppercase, no spaces |
| Required columns | `--jira-required-columns` | `ID, Requirement, Jira, Status` | Jira column mandatory |
| Link direction | `--jira-link-direction` | `page ↔ issue` | Remote link on the page |
| Link type | `--jira-link-type` | `implements` | Or `documents`, `relates to` |
| Remote link title | `--jira-remote-title` | `{KEY} — {summary}` | Recognisable in Jira |
| Sync cadence | `--jira-sync-cadence` | `every review` | Never let status drift a quarter |
| Label taxonomy | `--jira-label-taxonomy` | `type + domain + state` | `fds`, `payments`, `approved` |
| Status source | `--jira-status-source` | `live macro or API` | No copied status prose |
| Reconciliation | `--jira-reconcile` | `date in change log` | Evidence of the last check |

## 4. Composition

- **With fds-requirements (guide 02):** the requirement ID and Jira key form the traceability pair.
- **With tables-matrices (guide 05):** the Jira column is the join key; keep it short and consistent.
- **With update-versioning (guide 08):** every update records the Jira issue that motivated it.
- **With automation-quality (guide 12):** link checks and status drift detection can run in CI.

## 5. Signature Patterns

- **Requirement traceability row:** `FR-001 | Create refund | PAY-1420 | Approved`.
- **Epic banner:** an info panel naming the epic, owner and scope; the detail table carries stories.
- **Live Jira macro:** embed one macro for the epic or a JQL filter, not twenty individual macros.
- **Remote link:** `confluence.py jira-link add` creates the Jira-side link with a stable global ID.
- **Reconciliation note:** `Last Jira reconciliation: 2026-11-17` beside the requirement table.
- **Deprecation link:** the old page links to the successor issue and page.

## 6. Real-World Use Cases

- **Release audit** — walk every FR to its issue and test evidence before sign-off.
- **Scope change** — a new story adds a row, a version and a change-log entry in one pass.
- **Incident follow-up** — action items live in Jira; the postmortem links them by key.
- **Compliance evidence** — the auditor sees the requirement, the authorising ticket and the approval.

## 7. Combination Notes

### With other confluence-document skills

- **FDS requirements:** IDs without keys are orphans; keys without rows are undocumented scope.
- **Tables:** a Jira column that mixes keys and URLs is not machine-checkable; keep the key only.
- **Update and versioning:** the version message names the Jira key, making the audit trail searchable.
- **Review governance:** approval status in Confluence and issue status in Jira are separate controls; both must agree at release.

### With design-system companions

- **skill-ux-writing:** link text should name the destination — `PAY-1420 refund epic`, not `here`.
- **skill-component-recipes:** status chips in a UI follow the same text-plus-colour rule as Jira macros.

## 8. Anti-Patterns

- **Jira screenshots pasted as the source of truth** — stale, unsearchable and inaccessible
- **Requirements with no Jira key in the table** — impossible to trace or prioritise
- **Copying live status from Jira into prose and never refreshing** — the page lies within a day
- **Linking only the epic and losing story-level traceability** — scope is visible, delivery is not
- **Duplicate descriptions maintained in both Jira and Confluence** — two truths, guaranteed drift

### Accessibility Notes

Link text must include the issue key and a short purpose: `PAY-1420 — refund epic`, not `click here`. The Jira macro renders a link whose accessible name should be meaningful; if it renders only an icon, add a text link beside it. Do not rely on the macro's colour or icon to convey status; the issue key and status text carry the meaning.

## 9. Code Examples

### Example 1 — Requirement table with live Jira references

```markdown
| ID | Requirement | Priority | Jira | Status |
|---|---|---|---|---|
| FR-001 | Create a partial or full refund | Must | {{jira:PAY-1420}} | Approved |
| FR-002 | Replay a repeated idempotency key | Must | {{jira:PAY-1421}} | Approved |
| FR-003 | Publish refund status events | Must | {{jira:PAY-1422}} | Approved |
```

### Example 2 — Create the page-side remote link

```bash
# Adds a Jira remote link to the page; safe to re-run (global ID is stable).
python3 scripts/confluence.py jira-link add --page-id 12345 \
  --issue PAY-1420 --relationship implements --title "PAY-1420 — Refund epic"

# Audit existing links.
python3 scripts/confluence.py jira-link list --page-id 12345
```

```text
CQL for pages that mention a key but are not linked:
text ~ "PAY-1420" and type = page
```

## 10. Implementation Checklist

- [ ] Every requirement row has a Jira key in a dedicated column.
- [ ] The page has a remote link to the epic and, where relevant, to each story.
- [ ] Status is read from Jira or the macro; no copied status prose.
- [ ] The Jira column contains keys only, not URLs or pasted summaries.
- [ ] Labels follow the controlled taxonomy and include the document type.
- [ ] The change log names the Jira key for every revision.
- [ ] The last reconciliation date is recorded beside the requirement table.
- [ ] Deprecated pages link to their successor issue and page.
