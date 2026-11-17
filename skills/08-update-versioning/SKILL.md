---
name: update-versioning
description: Controlled Confluence updates — read before write, backup, section-level diff, version bump rules, mandatory version messages, change-log rows, conflict handling and deprecation.
tags: [confluence, update, versioning, change-log, backup, conflict]
related: [automation-quality, review-governance, document-architecture]
---

# Confluence Documents Guide: Update and Versioning

## 1. Definition

A Confluence page is a versioned product, not a scratchpad. An update is a controlled operation: fetch the current storage, capture a backup, change the smallest possible surface, validate, review the diff, publish with a version message, verify the result, and record the change in the log. The version history is the audit trail; if a change is not in the change log and the version message, it did not happen.

## 2. Core Principles

- **Read before write:** never generate an update from memory or a stale local copy.
- **Back up the current storage:** a local snapshot before every write, retained for rollback.
- **Smallest safe diff:** change the section that changed; do not reformat the whole page.
- **One logical change per version:** a typo fix and a scope change are two revisions.
- **Message is part of the change:** `v12 — BR-004: dual approval at 50M VND` is reviewable; "update" is not.
- **Change log is mandatory:** version, date, author, change, Jira — every time.
- **Verify after publish:** re-fetch and compare the hash; Confluence may normalise storage.
- **Conflict means stop:** a 409 is a human edit, not a retry signal.
- **Deprecate, never delete:** old pages link to the successor and keep their history.

## 3. Spec Tokens

| Role | Token | Value | Notes |
|---|---|---|---|
| Version scheme | `--update-version` | `major.minor[.patch]` | Major for scope, minor for content |
| Message format | `--update-message` | `v{n} — {area}: {change}` | ≤ 255 characters |
| Change log columns | `--update-changelog` | `Version, Date, Author, Change, Jira` | Newest row first |
| Backup retention | `--update-backups` | `10 per page` | Local `.confluence-backups/` |
| Diff review | `--update-diff-review` | `before every write` | `confluence.py diff` or `--dry-run` |
| Conflict policy | `--update-conflict` | `stop and rebase` | Never overwrite a newer version |
| Approval gate | `--update-approval` | `Approved → In Review` | Content change on an approved page |
| Verification | `--update-verify` | `hash + well-formedness` | `confluence.py verify` |

## 4. Composition

- **With document-architecture (guide 01):** the change log is the last numbered section and mirrors the frontmatter version.
- **With review-governance (guide 10):** an approved page returns to In Review when scope changes.
- **With automation-quality (guide 12):** `upsert` is idempotent; identical content does not create a version.
- **With jira-traceability (guide 07):** every version message names the issue that authorised the change.

## 5. Signature Patterns

- **Update protocol:** fetch → backup → edit → validate → diff → publish → verify → changelog → notify.
- **Section replacement:** read storage, replace one anchored block, leave the rest byte-identical.
- **Scope-change reset:** status to `In Review`, reviewers re-added, change log row added.
- **Rollback:** restore the previous storage from backup as a new version; never delete history.
- **Deprecation banner:** an info panel at the top linking the successor page and issue.
- **Version message template:** `v{n} — {section or rule}: {what changed and why}`.

## 6. Real-World Use Cases

- **Approved FDS gets a new business rule** — status reset, BR row added, AC added, version bumped, changelog row.
- **Typo fix on a published runbook** — patch version, message names the section; no scope change.
- **Concurrent edit during an agent update** — the 409 stops the write; the agent re-fetches and rebases.
- **Page superseded by a new service** — deprecation banner, successor link, label `deprecated`, no deletion.

## 7. Combination Notes

### With other confluence-document skills

- **Document architecture:** version and updated fields belong to the control block; do not maintain a second copy in prose.
- **Review governance:** the transition to Approved is a review event; content changes afterwards require a new review.
- **Automation:** all write commands require `--message`; `--dry-run` and `diff` are the default review path.
- **Jira:** the change log's Jira column is the index for audit queries.

### With design-system companions

- **skill-ux-writing (voice and tone):** version messages are interface copy for reviewers — specific, verb-first, no filler.
- **skill-design-tokens (governance):** versioning is the same discipline as token deprecation: announce, migrate, remove later.

## 8. Anti-Patterns

- **Full-page overwrite from a stale local copy** — silently reverts other people's work
- **Silent typo edits on an approved document** — no version message, no audit trail
- **Version bump with an empty or meaningless message** — "update" tells the next reader nothing
- **Editing a published page without a change log row** — the log becomes fiction
- **Deleting the old page instead of marking it superseded** — breaks every inbound link and the audit trail

### Accessibility Notes

Version history is a public surface: keep messages readable by a person, not encoded (`v12 — dual approval`, not `fix#1245`). Change-log tables need a header row and text status. Deprecation banners must state the reason and the successor in text, not only a colour or icon.

## 9. Code Examples

### Example 1 — Safe update protocol

```bash
# 1. Read the current page and keep a local mirror.
python3 scripts/confluence.py get --page-id 12345 --out .work/page.storage.html

# 2. Edit the Markdown source, not the live storage, then lint.
python3 scripts/validate_document.py fds.md --profile fds --min-score 90 --publish

# 3. Review the exact storage diff before writing.
python3 scripts/confluence.py diff --page-id 12345 --from-md fds.md

# 4. Publish with a message that names the change; a backup is written automatically.
python3 scripts/confluence.py update --page-id 12345 --from-md fds.md \
  --message "BR-004: dual approval at 50,000,000 VND" --update-labels

# 5. Verify the remote hash and well-formedness.
python3 scripts/confluence.py verify --page-id 12345
```

### Example 2 — Change-log row and deprecation banner

```markdown
| Version | Date | Author | Change | Jira |
|---|---|---|---|---|
| 1.1 | 2026-11-17 | Nguyễn Minh An | BR-004: dual approval at 50,000,000 VND | {{jira:PAY-1455}} |
| 1.0 | 2026-11-10 | Lê Thu Hà | Approved after security review | {{jira:PAY-1420}} |

:::warning
**Deprecated on 2026-12-01.** This page is superseded by [Refund v2 — FDS]({URL}). Use the successor for all new work; this page remains for audit only.
:::
```

## 10. Implementation Checklist

- [ ] The current page was fetched immediately before the write; no stale copy is used.
- [ ] A backup of the previous storage exists in `.confluence-backups/`.
- [ ] The diff contains only the intended sections, not a whole-page reformat.
- [ ] The version is bumped according to the scheme and the message names the change.
- [ ] A change-log row is added with version, date, author, change and Jira key.
- [ ] The page status is reset to In Review when scope changes on an approved page.
- [ ] The publish is verified by re-fetching and comparing the storage hash.
- [ ] Superseded pages are deprecated with a successor link, never deleted.
