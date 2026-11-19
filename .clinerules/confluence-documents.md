# Confluence Documents — Cline Rules

This workspace is a portable skill pack for enterprise Confluence Cloud documents. [`SKILL.md`](../SKILL.md) is the canonical router and formatting contract. Read it before authoring, converting, reviewing or publishing anything.

## Routing

| Request | Template | Lint profile | Guide |
|---|---|---|---|
| Functional design / requirements | `assets/templates/fds.md` or `fds.vi.md` | `fds` / `fds-vi` | `skills/02-fds-requirements/` |
| API contract | `assets/templates/api-spec.md` | `api` | `skills/09-api-contracts/` |
| Decision proposal | `assets/templates/rfc.md` | `rfc` | `skills/01-document-architecture/` |
| On-call procedure | `assets/templates/runbook.md` | `runbook` | `skills/01-document-architecture/` |
| Release notes | `assets/templates/release-notes.md` | `release` | `skills/08-update-versioning/` |
| Incident review | `assets/templates/postmortem.md` | `postmortem` | `skills/05-tables-matrices/` |
| Architecture decision | `assets/templates/adr.md` | `adr` | `skills/01-document-architecture/` |
| Anything else | `assets/templates/fds.md`, then trim | `generic` | `skills/01-document-architecture/` |

## Rules

1. Read `SKILL.md` and exactly one relevant guide before writing.
2. Copy the template into the working directory; never edit `assets/templates/` in place.
3. Frontmatter first: title, `doc_id`, version, status, owner, reviewers, Jira key, space, labels, classification, `updated`.
4. Tables over bullets; no bullets-only section; answer first in every H2. Display containers come from the Step 2b palette in `SKILL.md` — titled callouts and expands, at most five callouts per page, unknown macros fail closed.
5. Lint with `--publish`, then convert with `--check`.
6. Publish only with `scripts/confluence.py`: search before create; get → diff → update with a version message → verify.
7. Never invent page IDs, URLs, Jira keys, metrics, owners or approval dates.
8. Never ask for, print or commit an API token. Use `.env` from `.env.example`.
9. Read before write; back up; stop on HTTP 409; deprecate instead of deleting.
10. Report exactly what happened, including when nothing was published.

## Workflows

Use the slash commands in `.clinerules/workflows/`:

- `/new-document.md` — author, lint and convert a new page without publishing.
- `/publish-page.md` — create or update a page with the safe protocol.
- `/audit-document.md` — lint and review an existing document without editing it.

## Commands

```bash
python3 scripts/validate_document.py path/to/doc.md --profile fds --min-score 90 --publish
python3 scripts/md2storage.py path/to/doc.md -o .work/doc.storage.html --manifest .work/doc.json --check
python3 scripts/confluence.py --env-file .env whoami
python3 scripts/confluence.py --env-file .env get --page-id 12345 --out .work/current.storage.html
python3 scripts/confluence.py --env-file .env diff --page-id 12345 --from-md path/to/doc.md
python3 scripts/confluence.py --env-file .env update --page-id 12345 --from-md path/to/doc.md --message "v1.1 — AREA: change"
python3 scripts/confluence.py --env-file .env verify --page-id 12345 --file .work/doc.storage.html
```
