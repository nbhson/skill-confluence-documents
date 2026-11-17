---
title: "Release {version} — {Product or service}"
doc_id: REL-{DOMAIN}-001
version: "{version}"
status: Approved
owner: "{Release Manager}"
reviewers: ["{Product Owner}", "{QA Lead}"]
jira: "{RELEASE-EPIC-KEY}"
space: "{SPACE}"
labels: [release-notes, "{domain}"]
classification: Internal
updated: "{YYYY-MM-DD}"
---

{{meta}}

{{toc}}

## 1. Summary

{One paragraph a customer or support agent can quote: what shipped, who benefits, and when it is available.}

:::info
**Release window:** {YYYY-MM-DD HH:mm} to {YYYY-MM-DD HH:mm} ({timezone}). **Rollback decision by:** {time}. **Status page:** {URL}.
:::

| Attribute | Value |
|---|---|
| Release version | `{version}` |
| Release type | Major / minor / patch / hotfix |
| Deployment window | {start} - {end} {timezone} |
| Environments | Staging, production, {region} |
| Release owner | {Name} |
| Change freeze | {YYYY-MM-DD HH:mm} |
| Feature flags | {flag names and default states} |

## 2. Highlights

| Area | Change | Customer value | Jira |
|---|---|---|---|
| {Area} | {What changed} | {Why the user cares} | {{jira:{KEY-1}}} |
| {Area} | {What changed} | {Why the user cares} | {{jira:{KEY-2}}} |
| {Area} | {What changed} | {Why the user cares} | {{jira:{KEY-3}}} |

## 3. Breaking Changes

| ID | Change | Affected clients | Impact | Required action | Deadline |
|---|---|---|---|---|---|
| BC-001 | {API or behaviour change} | {Consumers} | {Failure if ignored} | {Action} | {YYYY-MM-DD} |
| BC-002 | {Removed field or endpoint} | {Consumers} | {Failure if ignored} | {Action} | {YYYY-MM-DD} |

:::warning
Breaking changes ship only with a migration path and a named owner. If either is missing, remove the change from this release.
:::

## 4. Migration

1. Read section 3 and identify every change that affects your integration.
2. Apply the configuration or code change in the sandbox environment first.
3. Run the verification commands below and compare against the expected output.
4. Schedule production migration before the deadline in the breaking-change table.
5. Confirm completion in {Jira issue or Slack channel}.

```bash
# Example: migrate a configuration key before disabling the legacy field.
{cli} config migrate \
  --from legacy_field \
  --to new_field \
  --dry-run
```

| Legacy behaviour | New behaviour | Verification |
|---|---|---|
| `{legacy_field}` | `{new_field}` | Response contains `new_field` and not `legacy_field` |
| {Old endpoint} | {New endpoint} | `curl` returns 200 from the new path |
| {Old default} | {New default} | {Observable check} |

## 5. Known Issues

| ID | Issue | Affected scope | Workaround | Owner | Status |
|---|---|---|---|---|---|
| KI-001 | {Known defect} | {Who is affected} | {Workaround} | {Owner} | {{status:yellow\|Open}} |
| KI-002 | {Known limitation} | {Who is affected} | {Workaround} | {Owner} | {{status:grey\|Monitoring}} |
| KI-003 | {Resolved during rollout} | {Scope} | None | {Owner} | {{status:green\|Resolved}} |

## 6. Change Log

| Version | Date | Author | Change | Jira |
|---|---|---|---|---|
| {version} | {YYYY-MM-DD} | {Release Manager} | Release published | {{jira:{RELEASE-EPIC-KEY}}} |
