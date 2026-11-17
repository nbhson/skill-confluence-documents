# Confluence Documents — GitHub Copilot Instructions

This repository is a portable skill pack for enterprise Confluence Cloud documents. [`SKILL.md`](../SKILL.md) is the canonical router, formatting contract and publish protocol. Read it before writing, converting, reviewing or publishing anything.

Copilot does not discover nested `skills/*/SKILL.md` guides automatically. Treat this file as the entry point and open the referenced files explicitly.

## Routing

| Request | Template | Lint profile | Guides |
|---|---|---|---|
| Functional design / requirements | `assets/templates/fds.md` or `fds.vi.md` | `fds` / `fds-vi` | `skills/01-document-architecture`, `skills/02-fds-requirements` |
| API contract | `assets/templates/api-spec.md` | `api` | `skills/09-api-contracts` |
| Decision proposal | `assets/templates/rfc.md` | `rfc` | `skills/01-document-architecture` |
| On-call procedure | `assets/templates/runbook.md` | `runbook` | `skills/01-document-architecture` |
| Release notes | `assets/templates/release-notes.md` | `release` | `skills/08-update-versioning` |
| Incident review | `assets/templates/postmortem.md` | `postmortem` | `skills/05-tables-matrices` |
| Architecture decision | `assets/templates/adr.md` | `adr` | `skills/01-document-architecture` |
| Anything else | `assets/templates/fds.md`, then trim | `generic` | `skills/01-document-architecture` |

## Workflow

1. Classify the request; for updates, classify from the live page.
2. Copy the matching template into the working directory.
3. Fill frontmatter first: title, `doc_id`, version, status, owner, reviewers, Jira key, space, labels, classification, `updated`. Use explicit placeholders and `Draft` when facts are missing.
4. Lint with the matching profile and `--publish`.
5. Convert to storage XHTML with `--check`.
6. Publish only with the safe protocol: search before create; get → diff → update with a version message → verify for existing pages.
7. Report title, page ID, URL, version, score and verification result. Say plainly when nothing was published.

```bash
python3 scripts/validate_document.py path/to/doc.md --profile fds --min-score 90 --publish
python3 scripts/md2storage.py path/to/doc.md -o .work/doc.storage.html --manifest .work/doc.json --check
python3 scripts/confluence.py --env-file .env whoami
python3 scripts/confluence.py --env-file .env create --from-md path/to/doc.md --space KEY --parent-id 123456 --dry-run
python3 scripts/confluence.py --env-file .env get --page-id 12345 --out .work/current.storage.html
python3 scripts/confluence.py --env-file .env diff --page-id 12345 --from-md path/to/doc.md
python3 scripts/confluence.py --env-file .env update --page-id 12345 --from-md path/to/doc.md --message "v1.1 — AREA: change"
python3 scripts/confluence.py --env-file .env verify --page-id 12345 --file .work/doc.storage.html
```

## Guardrails

- Tables over bullet walls; no bullets-only section; three or more parallel facts become a table.
- Answer first in every H2; six to twelve numbered sections, depth at most H3.
- Status must be text plus colour, using `Draft`, `In Review`, `Approved`, `Deprecated`, `Superseded`.
- Every requirement row carries a Jira key; the change log matches the frontmatter version.
- Never invent page IDs, URLs, Jira keys, metrics, owners or approval dates.
- Never request, print or commit an API token. Use `.env` from `.env.example`.
- Read before write; back up, diff, use an explicit version message and verify.
- Stop on HTTP 409 and re-read; deprecate instead of deleting.
- Copilot in plain chat mode cannot run shell commands. Deliver validated files and the exact commands instead of claiming a publish.
