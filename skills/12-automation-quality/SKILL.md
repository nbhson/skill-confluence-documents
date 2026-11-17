---
name: automation-quality
description: Docs-as-code automation for Confluence — deterministic conversion, lint gates, idempotent publishing, dry runs, backups, verification, drift audits, CI pipelines and document quality metrics.
tags: [confluence, automation, ci, lint, publishing, drift, quality]
related: [storage-format, update-versioning, review-governance, jira-traceability]
---

# Confluence Documents Guide: Automation and Quality

## 1. Definition

Documentation automation is the reproducible path from a reviewed Markdown source to a verified Confluence page, plus the scheduled audits that keep it true. Quality is enforced by executable gates, not by reviewer vigilance: the converter must be deterministic, the linter must enforce the formatting contract, publishing must be idempotent and backed up, and every write must be verified against the remote page. Automation handles the mechanical checks so people can review meaning — scope, correctness, risk and clarity.

## 2. Core Principles

- **Git is the source of truth:** Confluence is a publication target, not the editing surface for managed documents.
- **Deterministic conversion:** the same input and version produce byte-identical storage; a diff means the content changed.
- **Gate before write:** lint, publish-mode checks and well-formedness run before any API call.
- **Idempotent publish:** `upsert` compares the content hash and creates no version when nothing changed.
- **Dry run first:** every write supports a preview; the diff is the review artefact.
- **Explicit version messages:** the message names the section and the change; automation must never invent "update".
- **Backup before write:** the previous storage is retained locally for rollback.
- **Verify after write:** re-fetch, compare the hash and check the version number; success is proven, not assumed.
- **Secrets stay in the environment:** tokens are read from env vars or a local `.env`, never committed or pasted into a prompt.
- **Drift is detected on a schedule:** CQL audits find orphaned, stale and unlabelled pages before an auditor does.
- **Fail closed:** unknown macros, malformed storage and missing credentials stop the run.
- **Templates and examples version together:** a scaffold change is not done until the reference example still passes.

## 3. Spec Tokens

| Role | Token | Value | Notes |
|---|---|---|---|
| Source format | `--auto-source` | `Markdown + frontmatter` | Committed to git |
| Converter check | `--auto-check` | `md2storage.py --check` | Well-formedness gate |
| Lint score | `--auto-min-score` | `90` | 85 for drafts, 100 for examples |
| Publish mode | `--auto-publish` | `--publish` | Placeholders and labels become errors |
| Idempotency | `--auto-upsert` | `hash comparison` | No version when unchanged |
| Version message | `--auto-message` | `v{n} — {area}: {change}` | Required on every write |
| Backup retention | `--auto-backups` | `10 per page` | `.confluence-backups/` |
| Verification | `--auto-verify` | `remote hash + version` | After every write |
| Drift cadence | `--auto-audit` | `weekly` | CQL + ownership check |
| Token scope | `--auto-token` | `minimum space access` | Rotate on a schedule |
| CI runtime | `--auto-ci` | `≤ 5 minutes` | Fast enough to run on every PR |
| Audit columns | `--auto-audit-columns` | `Page, Owner, Version, Age, Status` | One row per finding |

## 4. Composition

- **With storage-format (guide 04):** conversion and XHTML validation are the same gate; the converter is the only writer of storage.
- **With update-versioning (guide 08):** automation implements the read-backup-diff-publish-verify protocol; it does not replace the judgement of what to change.
- **With review-governance (guide 10):** CI enforces mechanical review evidence; humans still record the decision.
- **With jira-traceability (guide 07):** link checks and status reconciliation run on a schedule against the Jira API.
- **With readability-accessibility (guide 11):** lint can flag missing alt text and ASCII-only Vietnamese; a manual accessibility sample remains mandatory.
- **With document-architecture (guide 01):** templates are versioned artefacts; the CI validates every template and the completed example.

## 5. Signature Patterns

- **CI pipeline:** checkout → lint documents → validate examples → convert all templates → repo contract check → publish only on the default branch with an explicit message.
- **Pre-commit hook:** convert the changed Markdown and run the matching profile; block the commit on a malformed fragment.
- **Publish manifest:** title, space, labels, version and content hash produced by the converter and consumed by the publisher.
- **Idempotent upsert:** search by title in the target space, compare hashes, skip or update; labels reconciled from frontmatter.
- **Drift audit:** CQL for `label = fds and lastmodified < now("-180d")`, then a table of page, owner, version and action.
- **Quality dashboard:** documents checked, pass rate, stale pages, broken links, missing owners, next review overdue.
- **Batch migration:** per-page dry run, then a single write loop with a backup directory and a failure report.
- **Agent publish protocol:** read → plan → convert → lint → diff → write with message → verify → report URL and hash.

## 6. Real-World Use Cases

- **Docs-as-code repository** — every FDS, RFC and runbook is reviewed in a pull request and published by CI.
- **Nightly drift audit** — pages with no owner, no changelog row or an expired review date are reported to the space owner.
- **Multi-space template rollout** — the same template is validated once and published to several spaces with different labels.
- **Agent-assisted update** — the agent converts, lints and previews the diff; a human approves the version message and write.
- **Incident documentation** — the postmortem template is generated from the incident record, then reviewed and published with evidence links.
- **Release gate** — the release notes cannot publish while the lint gate or the changelog check fails.

## 7. Combination Notes

### With other confluence-document skills

- **Storage format:** never hand-edit generated storage in the browser; the next publish will overwrite it and the diff will be unreadable.
- **Update and versioning:** automation must pass `--message` and must not retry a 409; the conflict is a human edit.
- **Review governance:** a green CI run is evidence, not approval; the decision owner still signs the version.
- **Jira traceability:** automated link checks should verify both directions, not only that a key appears in the text.
- **Readability and accessibility:** automated checks are necessary but insufficient; keep a manual sample in every release.

### With design-system companions

- **skill-design-tokens:** the same pipeline discipline — source of truth, generated artefacts, validation, deprecation.
- **skill-design-review:** use a fixed checklist and a recorded outcome; automation reports facts, reviewers make judgements.

## 8. Anti-Patterns

- **Browser copy-paste as the deployment process** — no diff, no validation, no audit trail
- **Lint warnings ignored because the page looks fine** — the format contract erodes one exception at a time
- **Credentials committed to the repository or pasted into prompts** — a leak that outlives the automation
- **Blind retry after a 409 version conflict** — overwrites a human edit and loses their work
- **Automated publish without post-write verification** — success is assumed, not proven
- **Templates updated without revalidating the examples** — the scaffold and the reference diverge
- **Scheduled audit that reports drift but assigns no owner** — the report becomes noise and the pages stay stale

### Accessibility Notes

Automated checks catch missing alt text, skipped heading levels and colour-only status patterns, but they cannot prove that alt text is meaningful or that the reading order makes sense. Keep one manual screen-reader pass per release for each document type, and never auto-generate alt text as a filename or "image". Lint the Vietnamese profile so ASCII-only headings and missing diacritics fail before publication. In CI reports, state the page, the rule and the fix — a failure without a remediation is just noise.

## 9. Code Examples

### Example 1 — Pull-request quality gate

```yaml
name: validate-documents
on:
  pull_request:
  push:
    branches: [main]
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Repository contract
        run: python3 scripts/validate_skills.py
      - name: Lint every changed document
        run: |
          for file in $(git diff --name-only origin/main...HEAD -- '*.md'); do
            case "$file" in
              assets/templates/*) profile=generic ;;
              assets/examples/*) profile=fds-vi ;;
              *) profile=fds ;;
            esac
            python3 scripts/validate_document.py "$file" --profile "$profile" --min-score 90
          done
      - name: Convert every template
        run: |
          for file in assets/templates/*.md; do
            python3 scripts/md2storage.py "$file" --check
          done
      - name: Validate the completed example
        run: python3 scripts/validate_document.py assets/examples/fds-payment-refund.vi.md \
          --profile fds-vi --min-score 85 --publish
```

### Example 2 — Idempotent publish with verification

```bash
# Read the current page; the backup is written by update/upsert automatically.
python3 scripts/confluence.py get --page-id 12345 --out .work/current.storage.html

# Convert and lint; --check fails on malformed XHTML.
python3 scripts/md2storage.py fds.md -o .work/fds.storage.html --manifest .work/fds.json --check
python3 scripts/validate_document.py fds.md --profile fds --min-score 90 --publish

# Preview the exact diff, then publish only if there is a real change.
python3 scripts/confluence.py diff --page-id 12345 --from-md fds.md
python3 scripts/confluence.py upsert --from-md fds.md --space PAY \
  --message "v1.2 — BR-004: dual approval at 50,000,000 VND" --update-labels

# Prove the remote state matches the source.
python3 scripts/confluence.py verify --page-id 12345 --file .work/fds.storage.html
```

### Example 3 — Weekly drift audit

```bash
# Find approved FDS pages that have not changed in 180 days.
python3 scripts/confluence.py search \
  --cql 'label = "fds" and label = "approved" and lastmodified < now("-180d")' \
  --limit 50 --json > .work/stale-fds.json
```

```markdown
| Page | Owner | Version | Last modified | Finding | Action | Due |
|---|---|---|---|---|---|---|
| FDS-PAY-009 | Payments Eng | 2.3 | 2025-04-12 | Review overdue by 79 days | Re-review or deprecate | 2026-11-30 |
| RUN-PAY-002 | SRE | 1.8 | 2025-09-01 | Runbook not tested this year | Schedule game day | 2026-12-15 |
| FDS-CRM-004 | CRM Platform | 0.9 | 2025-11-20 | Draft abandoned | Archive or assign owner | 2026-12-01 |
```

## 10. Implementation Checklist

- [ ] The Markdown source is committed to git and Confluence is treated as a publication target.
- [ ] Conversion is deterministic and passes `md2storage.py --check` for every template and document.
- [ ] CI runs the document linter with the correct profile and `--publish` for release branches.
- [ ] Every write uses an explicit version message and a dry run or diff has been reviewed.
- [ ] `upsert` skips identical content; unchanged pages do not create versions.
- [ ] Credentials come from environment variables or a local `.env`; nothing is committed.
- [ ] A backup of the previous storage exists before every update.
- [ ] Every publish is verified by re-fetching the page and comparing the hash and version.
- [ ] A weekly or monthly audit reports stale, orphaned and unowned pages with an assigned owner and due date.
- [ ] The repository contract check validates guides, `data.json`, templates and the completed example.
- [ ] A manual accessibility sample is part of every release, not only automated lint.
