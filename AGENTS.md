# Confluence Documents — Agent Adapter

This repository is a portable skill pack for creating, updating and auditing enterprise documents in Atlassian Cloud Confluence. [`SKILL.md`](./SKILL.md) is the canonical router, formatting contract and publish protocol. Read it before writing, converting, reviewing or publishing anything.

Use this file when your host does not load `SKILL.md` automatically: OpenAI Codex, Gemini CLI, Cursor, Windsurf, Aider, GitHub Copilot coding agent, or any agent with file reads and shell access. Host-specific entry points are listed at the end.

## Read in this order

1. `SKILL.md` — non-negotiable contract, create/update protocols, no-credential fallback.
2. One discipline guide from `skills/` that matches the task.
3. The matching template in `assets/templates/`.
4. `assets/examples/fds-payment-refund.vi.md` for a complete, lint-clean reference.

Never improvise a page skeleton or skip the linter.

## Routing

| Request | Template | Lint profile | Guides |
|---|---|---|---|
| Functional design / requirements | `assets/templates/fds.md` or `fds.vi.md` | `fds` / `fds-vi` | 01, 02 |
| API contract | `assets/templates/api-spec.md` | `api` | 09, 05 |
| Decision proposal | `assets/templates/rfc.md` | `rfc` | 01, 05 |
| On-call procedure | `assets/templates/runbook.md` | `runbook` | 01, 03 |
| Release notes | `assets/templates/release-notes.md` | `release` | 03, 08 |
| Incident review | `assets/templates/postmortem.md` | `postmortem` | 05, 10 |
| Architecture decision | `assets/templates/adr.md` | `adr` | 01, 05 |
| Anything else | `assets/templates/fds.md`, then trim | `generic` | 01, 03 |

Guide numbers map to `skills/01-document-architecture/` through `skills/12-automation-quality/`. Open only the guides the task needs.

## Workflow

1. **Classify** the request using the table above. For an update, classify from the live page, not from the new request.
2. **Copy** the template into the working directory; never edit `assets/templates/` in place.
3. **Author** frontmatter first: real title, `doc_id`, version, status, owner, reviewers, Jira key, space, labels, classification, `updated`. Use explicit placeholders and status `Draft` when facts are missing.
4. **Lint** with the matching profile and `--publish`; fix every error and review every warning.
5. **Convert** to storage XHTML and require a well-formed fragment.
6. **Publish** only through the safe protocol below. Dry-run creates; read, diff and back up updates.
7. **Report** title, page ID, URL, version, lint score and verification result. If nothing was published, say so.

```bash
python3 scripts/validate_document.py path/to/doc.md --profile fds --min-score 90 --publish
python3 scripts/md2storage.py path/to/doc.md -o .work/doc.storage.html --manifest .work/doc.json --check

python3 scripts/confluence.py --env-file .env whoami
python3 scripts/confluence.py --env-file .env search --title "Exact page title" --space KEY
python3 scripts/confluence.py --env-file .env create --from-md path/to/doc.md --space KEY --parent-id 123456 --dry-run
python3 scripts/confluence.py --env-file .env get --page-id 12345 --out .work/current.storage.html
python3 scripts/confluence.py --env-file .env diff --page-id 12345 --from-md path/to/doc.md
python3 scripts/confluence.py --env-file .env update --page-id 12345 --from-md path/to/doc.md --message "v1.1 — BR-004: dual approval at 50,000,000 VND"
python3 scripts/confluence.py --env-file .env verify --page-id 12345 --file .work/doc.storage.html
```

## Non-negotiables

- **Tables over bullets.** Three or more parallel facts become a table with a stable ID column. No section may be bullets-only.
- **Answer first.** Each H2 opens with one or two sentences stating the conclusion.
- **Numbered, shallow structure.** Six to twelve H2 sections, depth at most H3, appendices lettered.
- **Status is text plus colour.** Use the controlled vocabulary `Draft`, `In Review`, `Approved`, `Deprecated`, `Superseded`.
- **Traceability.** Requirement rows carry a Jira key; each revision names the authorising issue; the change log matches the frontmatter version.
- **No fabricated facts.** Never invent page IDs, URLs, Jira keys, metrics, owners or approval dates.
- **Accessibility is part of done.** Real headings, table headers, descriptive links, alt text, no colour-only meaning, Vietnamese diacritics preserved.
- **Markdown is the source of truth.** Generate storage XHTML with `scripts/md2storage.py`; do not hand-edit live storage as the normal workflow.
- **No silent writes.** Every update has a backup, a reviewed diff, an explicit version message and post-write verification.
- **Deprecate, never delete.** Old pages keep history and link to the successor.

## Safety

- **Read before write.** A stale local file is not a source of truth.
- **Stop on HTTP 409.** A human edited the page; re-read and rebase, never retry blindly.
- **One logical change per version.** Do not mix a restructure with a scope change.
- **Least privilege.** Use a token restricted to the target spaces.
- **No secrets in documents.** Remove tokens, customer data and internal URLs that should not be public.
- **Respect the tenant.** Confirm that Mermaid, PlantUML and Jira macros are installed; otherwise fall back to tables and links.

## No-credential fallback

When `CONFLUENCE_BASE_URL`, `CONFLUENCE_EMAIL` and `CONFLUENCE_API_TOKEN` are absent:

1. Continue authoring, linting and conversion; they work offline.
2. Run `python3 scripts/confluence.py whoami` to confirm the missing configuration.
3. Do not ask the user to paste a token into chat. Point to `.env.example` and <https://id.atlassian.com/manage-profile/security/api-tokens>.
4. Do not invent a page ID, URL or publish confirmation.
5. Deliver the Markdown source, generated `.storage.html`, lint score and the exact command to run once credentials exist.

## Host-specific entry points

| Host | File |
|---|---|
| Claude Code | `CLAUDE.md`; optionally link the repository into `~/.claude/skills/confluence-documents` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Cline | `.clinerules/confluence-documents.md` and `.clinerules/workflows/` |
| Other agents | This file |

`SKILL.md` remains the single source of truth. Adapters must not fork the contract; change `SKILL.md` first, then adjust the adapters.
